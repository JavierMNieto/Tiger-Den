from oscar.apps.shipping.methods import Free
from django.utils.translation import gettext_lazy as _

class Delivery(Free):
    """
    Delivery
    """
    code = 'delivery'
    name = _('Delivery')