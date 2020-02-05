from django.db import models

from oscar.apps.catalogue.abstract_models import AbstractProduct, AbstractProductClass

class AbstractProductClass(AbstractProductClass):
    requires_shipping = False

    track_stock = False

from oscar.apps.catalogue.models import *