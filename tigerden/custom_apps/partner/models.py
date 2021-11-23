from django.db import models
from django.utils.translation import gettext_lazy as _

from oscar.apps.partner.abstract_models import AbstractStockRecord


class StockRecord(AbstractStockRecord):
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.price_excl_tax = self.price_retail
        super().save(force_insert=force_insert, force_update=force_update,
                     using=using, update_fields=update_fields)
        self.price_excl_tax = self.price_retail


from oscar.apps.partner.models import *  # noqa isort:skip
