from oscar.apps.order.abstract_models import AbstractOrder
from django.utils.translation import gettext_lazy as _
from django.db import models
from oscar.core.loading import get_class
from oscar.apps.order.signals import order_placed
from oscar.core.compat import AUTH_USER_MODEL

class Order(AbstractOrder):
    group_order = models.ForeignKey(
        'grouporder.GroupOrder', null=True, blank=True,
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

from oscar.apps.order.models import *  # noqa isort:skip
