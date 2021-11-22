from oscar.apps.order.abstract_models import AbstractOrder, AbstractLine, exceptions, logger
from oscar.core.loading import get_class, get_model
from oscar.apps.order.signals import order_placed
from oscar.core.compat import AUTH_USER_MODEL
from oscar.core.utils import get_default_currency
from oscar_accounts import models as acct_models, facade, exceptions as acct_exceptions
from oscar.apps.order.signals import order_status_changed

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from decimal import Decimal as D
from django.utils.timezone import now
from django.contrib.sites.models import Site
from django.core.signing import BadSignature, Signer
from django.utils.crypto import constant_time_compare
from django.urls import NoReverseMatch, reverse

EventHandler = get_class('order.processing', 'EventHandler')
bank = acct_models.Account.objects.get(id=4)


class Order(AbstractOrder):
    group_order = models.ForeignKey(
        'order.GroupOrder', null=True, blank=True,
        verbose_name=_("Group Order"),
        related_name='orders',
        on_delete=models.CASCADE)

    guest_name = models.CharField(_("Name"), max_length=25, blank=True)

    supervisor = models.ForeignKey(
        AUTH_USER_MODEL, related_name='order_requests', null=True, blank=True,
        verbose_name=_("Supervisor"), on_delete=models.SET_NULL)

    total_credit = models.DecimalField(
        _("Credit Used"), decimal_places=2, max_digits=12, null=True, default=None)

    max_alloc_credit = models.DecimalField(
        _("Maximum Amount of Credit Allowed to Use"), decimal_places=2, max_digits=12, default=D('0.00'))

    @property
    def total_cash(self):
        return self.total_excl_tax - (self.total_credit if self.total_credit else D("0.00"))

    @property
    def is_complete(self):
        return len(self.available_statuses()) < 2

    @property
    def is_cancelled(self):
        return not self.available_statuses()

    def set_status(self, new_status, code=None):
        """
        Set a new status for this order.

        If the requested status is not valid, then ``InvalidOrderStatus`` is
        raised.
        """
        if new_status == self.status:
            return

        old_status = self.status

        if new_status not in self.available_statuses():
            raise exceptions.InvalidOrderStatus(
                _("'%(new_status)s' is not a valid status for order %(number)s"
                  " (current status: '%(status)s')")
                % {'new_status': new_status,
                   'number': self.number,
                   'status': self.status})
        self.status = new_status
        if new_status in self.cascade:
            for line in self.lines.all():
                if not line.is_complete:
                    line.status = self.cascade[self.status]
                    line.save()
        self.save()

        # Send signal for handling status changed
        order_status_changed.send(sender=self,
                                  order=self,
                                  old_status=old_status,
                                  new_status=new_status,
                                  )

        self._create_order_status_change(old_status, new_status)

        if new_status == self.all_statuses()[1]:
            order_placed.send(sender=self, order=self, user=self.user)
        elif self.group_order and self.is_complete:
            if self.total_credit is not None and new_status == "Processed":
                self.complete_payment()
            self.group_order.check_all_order_statuses(self.number)

        if new_status == "Cancelled" and code is not None:
            self.send_cancellation_message(code)
    set_status.alters_data = True

    def calculate_total(self, line_ids=[]):
        lines = self.lines.all()
        total = D("0.00")
        if not self.is_cancelled:
            lines = lines.exclude(id__in=line_ids).exclude(status="Cancelled")
        for line in lines:
            total += line.line_price_excl_tax
        self.total_excl_tax = total
        self.save()
        self.group_order.calculate_total([self.id])

    def get_cancelled_lines(self):
        return self.lines.filter(status="Cancelled")

    def check_all_line_statuses(self, cur_line):
        is_cancelled = True
        for line in self.lines.all():
            if line.id == cur_line:
                line = self.lines.get(id=cur_line)
            if not line.is_complete:
                return
            if line.status != "Cancelled":
                is_cancelled = False

        if is_cancelled:
            self.set_status("Cancelled", "ORDER_OUT")
        else:
            self.set_status("Processed")

    def complete_payment(self):
        account = self.user.accounts.first()
        self.total_credit = max(
            min(min(account.balance, self.max_alloc_credit), self.total_excl_tax), 0.00)
        if self.total_credit > 0.00:
            transfer = None
            try:
                transfer = facade.transfer(
                    source=account,
                    destination=bank,
                    amount=self.total_credit,
                    # user=self.supervisor,
                    merchant_reference=self.number,
                    description=_("Credit Spent on Order #" + self.number)
                )
            except acct_exceptions.AccountException as e:
                if transfer:
                    facade.reverse(transfer)
            else:
                pass

        self.save()

    def send_cancellation_message(self, code):
        CommunicationEventType = get_model(
            'customer', 'CommunicationEventType')
        Dispatcher = get_class('customer.utils', 'Dispatcher')

        try:
            ctx = self.get_message_context(code)
        except TypeError:
            # It seems like the get_message_context method was overridden and
            # it does not support the code argument yet
            logger.warning(
                'The signature of the get_message_context method has changed, '
                'please update it in your codebase'
            )
            ctx = self.get_message_context()

        try:
            event_type = CommunicationEventType.objects.get(code=code)
        except CommunicationEventType.DoesNotExist:
            # No event-type in database, attempt to find templates for this
            # type and render them immediately to get the messages.  Since we
            # have not CommunicationEventType to link to, we can't create a
            # CommunicationEvent instance.
            messages = CommunicationEventType.objects.get_and_render(code, ctx)
            event_type = None
        else:
            messages = event_type.get_messages(ctx)
        if messages and messages['body']:
            logger.info("Order #%s - sending %s messages", self.number, code)
            dispatcher = Dispatcher(logger)
            dispatcher.dispatch_order_messages(self, messages, event_type)
        else:
            logger.warning(
                "Order #%s - no %s communication event type", self.number, code)

    def get_message_context(self, code=None):
        ctx = {
            'user': self.user,
            'order': self,
            'site': Site.objects.get_current()
        }

        # Attempt to add the order status URL to the email template ctx.
        try:
            if self.user:
                path = reverse('customer:order',
                               kwargs={'order_number': self.number})
            else:
                path = reverse('customer:anon-order',
                               kwargs={'order_number': self.number,
                                       'hash': self.verification_hash()})
        except NoReverseMatch:
            # We don't care that much if we can't resolve the URL
            pass

        ctx['status_url'] = 'http://%s%s' % (ctx['site'].domain, path)
        return ctx

    @property
    def user_label(self):
        if self.guest_name:
            return self.guest_name + " (Guest)"
        if self.guest_email:
            return self.guest_email + " (Guest)"
        if self.user:
            return self.user.label()
        return "Customer has deleted his or her account"


class Line(AbstractLine):

    @property
    def is_complete(self):
        return len(self.available_statuses()) < 2

    def out_of_stock(self):
        refund = False
        if self.status == "Processed" and self.order.total_credit:
            refund = True
        try:
            self.set_status("Cancelled")
        except exceptions.InvalidLineStatus as e:
            pass
        self.order.calculate_total([self.id])
        if refund:
            self.refund()

        if self.order.status != "Cancelled":
            self.order.send_cancellation_message(code="ORDER_LINE_OUT")

    def refund(self):
        if self.order.total_credit:
            amt = max(min(self.line_price_excl_tax,
                          self.order.total_credit), D("0.00"))
            if amt > 0.00:
                self.order.total_credit -= amt
                self.order.save()
                facade.transfer(
                    source=bank,
                    destination=self.order.user.accounts.first(),
                    amount=amt,
                    # user=self.order.supervisor,
                    merchant_reference=self.order.number,
                    description=_("Credit Refund on Order #" + \
                                  self.order.number)
                )

    def set_status(self, new_status):
        super().set_status(new_status)

        if self.order and self.is_complete:
            self.order.check_all_line_statuses(self.id)

    @property
    def description(self):
        """
        Returns a description of this line including details of any
        line attributes.
        """
        desc = self.title
        ops = []
        for attribute in self.attributes.all():
            if attribute.value.strip() != "":
                ops.append("%s = '%s'" % (attribute.type, attribute.value))
        if ops:
            desc = "%s (%s)" % (desc, ", ".join(ops))
        return desc

    def get_clean_attrs(self):
        attrs = []

        for attribute in self.attributes.all():
            if attribute.value.strip() != "":
                attrs.append({
                    'option': attribute.option,
                    'value': attribute.value
                })

        return attrs

    @property
    def code(self):
        if not self.product:
            return str(self.id)
        code = str(self.product.id)

        for attr in self.attributes.all():
            if attr.value.strip() != "":
                code += attr.value.replace(" ", "")

        return code


class GroupOrder(models.Model):
    """
    Group Order Model
    """

    number = models.CharField(_("Group Order number"),
                              max_length=128, db_index=True, unique=True)

    # Supervisor placing order
    user = models.ForeignKey(
        AUTH_USER_MODEL, related_name='grouporders', null=True,
        verbose_name=_("Supervisor"), on_delete=models.SET_NULL)

    location = models.CharField(_("Delivery Location"), max_length=50)

    currency = models.CharField(
        _("Currency"), max_length=14, default=get_default_currency)

    total_excl_tax = models.DecimalField(
        _("Order total (excl. tax)"), decimal_places=2, max_digits=12)

    # Use this field to indicate that an order is on hold / awaiting payment
    status = models.CharField(_("Status"), max_length=100, blank=True)

    # Index added to this field for reporting
    date_placed = models.DateTimeField(db_index=True)

    #: Order status pipeline.  This should be a dict where each (key, value) #:
    #: corresponds to a status and a list of possible statuses that can follow
    #: that one.
    pipeline = getattr(settings, 'OSCAR_ORDER_STATUS_PIPELINE', {})

    #: Order status cascade pipeline.  This should be a dict where each (key,
    #: value) pair corresponds to an *order* status and the corresponding
    #: *line* status that needs to be set when the order is set to the new
    #: status
    cascade = getattr(settings, 'OSCAR_ORDER_STATUS_CASCADE', {})

    @classmethod
    def all_statuses(cls):
        """
        Return all possible statuses for an order
        """
        return list(cls.pipeline.keys())

    def available_statuses(self):
        """
        Return all possible statuses that this order can move to
        """
        return self.pipeline.get(self.status, ())

    @property
    def is_complete(self):
        return len(self.available_statuses()) < 2

    @property
    def is_cancelled(self):
        return not self.available_statuses()

    def set_status(self, new_status):
        """
        Set a new status for this order.
        If the requested status is not valid, then ``InvalidOrderStatus`` is
        raised.
        """
        if new_status == self.status:
            return

        old_status = self.status
        if new_status not in self.available_statuses():
            raise exceptions.InvalidOrderStatus(
                _("'%(new_status)s' is not a valid status for order %(number)s"
                  " (current status: '%(status)s')")
                % {'new_status': new_status,
                   'number': self.number,
                   'status': self.status})

        for order in self.orders.all():
            if order.status != new_status:
                handler = EventHandler(order.user)
                success_msg = _(
                    "Order status changed from '%(old_status)s' to "
                    "'%(new_status)s'") % {'old_status': old_status,
                                           'new_status': new_status}
                try:
                    handler.handle_order_status_change(
                        order, new_status, note_msg=success_msg, code="ORDER_BUSY")
                except exceptions.InvalidOrderStatus:
                    pass

        if self.available_statuses():
            self._set_status(old_status, new_status)

    def _set_status(self, old_status, new_status):
        self.status = new_status
        self.save()
        self._create_order_status_change(old_status, new_status)

    set_status.alters_data = True

    def _create_order_status_change(self, old_status, new_status):
        # Not setting the status on the order as that should be handled before
        self.status_changes.create(
            old_status=old_status, new_status=new_status)

    def check_all_order_statuses(self, cur_order):
        is_cancelled = True
        for order in self.orders.all():
            if order.number == cur_order:
                order = self.orders.get(number=cur_order)
            if not order.is_complete:
                return
            if order.status != "Cancelled":
                is_cancelled = False

        if is_cancelled:
            self._set_status(self.status, "Cancelled")
        else:
            self._set_status(self.status, "Processed")

    class Meta:
        app_label = 'order'
        ordering = ['-date_placed']
        verbose_name = _("Group Order")
        verbose_name_plural = _("Group Orders")

    def __str__(self):
        return "#%s" % (self.number,)

    def verification_hash(self):
        signer = Signer(salt='oscar.apps.order.GroupOrder')
        return signer.sign(self.number)

    def check_verification_hash(self, hash_to_check):
        """
        Checks the received verification hash against this order number.
        Returns False if the verification failed, True otherwise.
        """
        # if self.check_deprecated_verification_hash(hash_to_check):
        #   return True

        signer = Signer(salt='oscar.apps.order.GroupOrder')
        try:
            signed_number = signer.unsign(hash_to_check)
        except BadSignature:
            return False

        return constant_time_compare(signed_number, self.number)

    @property
    def email(self):
        return self.user.email

    @property
    def num_orders(self):
        return self.orders.all().count()

    @property
    def order_requests(self):
        return self.orders.all().exclude(user_id=self.user.id)

    @property
    def is_expired(self):
        return now().timestamp() - self.date_placed.timestamp() > 7200  # 2 hours

    def set_date_placed_default(self):
        if self.date_placed is None:
            self.date_placed = now()

    def save(self, *args, **kwargs):
        # Ensure the date_placed field works as it auto_now_add was set. But
        # this gives us the ability to set the date_placed explicitly (which is
        # useful when importing orders from another system).
        self.set_date_placed_default()
        super().save(*args, **kwargs)

    def get_all_lines(self):
        return Line.objects.filter(order__group_order__id=self.id)

    def get_all_lines_sorted(self):
        lines = self.get_all_lines()
        if self.status != "Cancelled":
            lines = lines.exclude(status="Cancelled")
        lines_dict = {}

        for line in lines:
            if line.code in lines_dict:
                lines_dict[line.code]['quantity'] += line.quantity
            else:
                lines_dict[line.code] = {
                    'title': line.title,
                    'product_id': line.product.id,
                    'quantity': line.quantity,
                    'attributes': line.get_clean_attrs()
                }

        return lines_dict

    def calculate_total(self, order_ids=[]):
        orders = self.orders.all()
        total = D("0.00")
        if not self.is_cancelled:
            orders = orders.exclude(status="Cancelled", id__in=order_ids)
        for order in orders:
            total += order.total_excl_tax
        self.total_excl_tax = total
        self.save()


class GroupOrderStatusChange(models.Model):
    group_order = models.ForeignKey(
        'order.GroupOrder',
        on_delete=models.CASCADE,
        related_name='status_changes',
        verbose_name=_('Order Status Changes')
    )
    old_status = models.CharField(_('Old Status'), max_length=100, blank=True)
    new_status = models.CharField(_('New Status'), max_length=100, blank=True)
    date_created = models.DateTimeField(
        _('Date Created'), auto_now_add=True, db_index=True)

    class Meta:
        app_label = 'order'
        verbose_name = _('Group Order Status Change')
        verbose_name_plural = _('Group Order Status Changes')
        ordering = ['-date_created']

    def __str__(self):
        return _('{order} has changed status from {old_status} to {new_status}').format(
            order=self.group_order, old_status=self.old_status, new_status=self.new_status
        )


from oscar.apps.order.models import *  # noqa isort:skip
