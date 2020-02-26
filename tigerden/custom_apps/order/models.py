from oscar.apps.order.abstract_models import AbstractOrder, AbstractLine, exceptions
from django.utils.translation import gettext_lazy as _
from django.db import models
from oscar.core.loading import get_class
from oscar.apps.order.signals import order_placed
from oscar.core.compat import AUTH_USER_MODEL
from django.conf import settings
from decimal import Decimal as D
from django.utils.timezone import now
from django.core.signing import BadSignature, Signer
from oscar.core.utils import get_default_currency
from django.utils.crypto import constant_time_compare

EventHandler = get_class('order.processing', 'EventHandler')

class Order(AbstractOrder):
    group_order = models.ForeignKey(
        'order.GroupOrder', null=True, blank=True,
        verbose_name=_("Group Order"),
        related_name='orders',
        on_delete=models.CASCADE)
    
    supervisor = models.ForeignKey(
        AUTH_USER_MODEL, related_name='order_requests', null=True, blank=True,
        verbose_name=_("Supervisor"), on_delete=models.SET_NULL)
    
    def set_status(self, new_status):
        super().set_status(new_status)
        
        if new_status == self.all_statuses()[1]:
            order_placed.send(sender=self, order=self, user=self.user)
        else:
            if self.group_order and self.available_statuses() == ():
                self.group_order.check_all_order_statuses(self.number)

class Line(AbstractLine):
    @property
    def description(self):
        """
        Returns a description of this line including details of any
        line attributes.
        """
        desc = self.title
        ops = []
        for attribute in self.attributes.all():
            if (attribute.value.strip() != ""):
                ops.append("%s = '%s'" % (attribute.type, attribute.value))
        if ops:
            desc = "%s (%s)" % (desc, ", ".join(ops))
        return desc

class GroupOrder(models.Model):
    """
    Group Order Model
    """
    
    number = models.CharField(_("Group Order number"), max_length=128, db_index=True, unique=True)
    
    # Supervisor placing order
    user = models.ForeignKey(
        AUTH_USER_MODEL, related_name='grouporders', null=True,
        verbose_name=_("Supervisor"), on_delete=models.SET_NULL)
    
    location = models.CharField(_("Delivery Location"), max_length=50)
    
    currency = models.CharField(_("Currency"), max_length=14, default=get_default_currency)
    
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
                        order, new_status, note_msg=success_msg)
                except exceptions.InvalidOrderStatus:
                    pass
        
        if self.available_statuses() != ():
            self._set_status(old_status, new_status)

    def _set_status(self, old_status, new_status):
        self.status = new_status
        self.save()
        self._create_order_status_change(old_status, new_status)

    set_status.alters_data = True

    def _create_order_status_change(self, old_status, new_status):
        # Not setting the status on the order as that should be handled before
        self.status_changes.create(old_status=old_status, new_status=new_status)
    
    def check_all_order_statuses(self, cur_order):
        is_cancelled = True
        for order in self.orders.all():
            if order.number == cur_order:
                order = Order.objects.get(number=cur_order)
            if order.available_statuses() != ():
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
        #if self.check_deprecated_verification_hash(hash_to_check):
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
    
    def set_date_placed_default(self):
        if self.date_placed is None:
            self.date_placed = now()

    def save(self, *args, **kwargs):
        # Ensure the date_placed field works as it auto_now_add was set. But
        # this gives us the ability to set the date_placed explicitly (which is
        # useful when importing orders from another system).
        self.set_date_placed_default()
        super().save(*args, **kwargs)
    
    """
    @property
    def total_excl_tax(self):
        total = D('0.00')
        for order in self.orders.all():
            total += order.total_excl_tax()
        return total
    """

class GroupOrderStatusChange(models.Model):
    group_order = models.ForeignKey(
        'order.GroupOrder',
        on_delete=models.CASCADE,
        related_name='status_changes',
        verbose_name=_('Order Status Changes')
    )
    old_status = models.CharField(_('Old Status'), max_length=100, blank=True)
    new_status = models.CharField(_('New Status'), max_length=100, blank=True)
    date_created = models.DateTimeField(_('Date Created'), auto_now_add=True, db_index=True)

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
