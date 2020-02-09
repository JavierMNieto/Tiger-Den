from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from oscar.core.compat import AUTH_USER_MODEL
from decimal import Decimal as D
from django.conf import settings

from django.core.signing import BadSignature, Signer
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
        self.status = new_status
        
        for order in self.orders.all():
            order.set_status(self.status)
            
        self.save()

        self._create_order_status_change(old_status, new_status)

    set_status.alters_data = True

    def _create_order_status_change(self, old_status, new_status):
        # Not setting the status on the order as that should be handled before
        self.status_changes.create(old_status=old_status, new_status=new_status)
    
    class Meta:
        app_label = 'grouporder'
        ordering = ['-date_placed']
        verbose_name = _("Group Order")
        verbose_name_plural = _("Group Orders")
    
    def __str__(self):
        return "#%s" % (self.number,)
    
    def verification_hash(self):
        signer = Signer(salt='oscar.apps.grouporder.GroupOrder')
        return signer.sign(self.number)
    
    def check_verification_hash(self, hash_to_check):
        """
        Checks the received verification hash against this order number.
        Returns False if the verification failed, True otherwise.
        """
        #if self.check_deprecated_verification_hash(hash_to_check):
        #   return True

        signer = Signer(salt='oscar.apps.grouporder.GroupOrder')
        try:
            signed_number = signer.unsign(hash_to_check)
        except BadSignature:
            return False

        return constant_time_compare(signed_number, self.number)
    
    @property
    def email(self):
        return self.user.email
    
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
        'grouporder.GroupOrder',
        on_delete=models.CASCADE,
        related_name='status_changes',
        verbose_name=_('Order Status Changes')
    )
    old_status = models.CharField(_('Old Status'), max_length=100, blank=True)
    new_status = models.CharField(_('New Status'), max_length=100, blank=True)
    date_created = models.DateTimeField(_('Date Created'), auto_now_add=True, db_index=True)

    class Meta:
        app_label = 'grouporder'
        verbose_name = _('Group Order Status Change')
        verbose_name_plural = _('Group Order Status Changes')
        ordering = ['-date_created']

    def __str__(self):
        return _('{order} has changed status from {old_status} to {new_status}').format(
            order=self.group_order, old_status=self.old_status, new_status=self.new_status
        )