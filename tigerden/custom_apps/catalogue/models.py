from django.db import models
from django.utils.translation import gettext_lazy as _
from oscar.apps.catalogue.abstract_models import AbstractProduct, AbstractProductClass

class ProductClass(AbstractProductClass):
    # Not implementing stock tracking
    track_stock = models.BooleanField(_("Track stock levels?"), default=False)
    
    # Not implementing shipping
    requires_shipping = models.BooleanField(_("Requires shipping?"), default=False)

from oscar.apps.catalogue.models import *