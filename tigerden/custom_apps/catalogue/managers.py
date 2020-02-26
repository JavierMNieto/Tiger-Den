from oscar.apps.catalogue import managers
from django.db.models import F

class ProductQuerySet(managers.ProductQuerySet):
    def browsable(self):
        browsable = super().browsable()
        return browsable.order_by('-stats__num_purchases')