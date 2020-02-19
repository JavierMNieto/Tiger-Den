from oscar.apps.catalogue import managers
from django.db.models import Q
from datetime import datetime

class ProductQuerySet(managers.ProductQuerySet):
    def browsable(self, is_supervisor=False):
        """
        Excludes non-canonical products and non-public products
        Filters out limited time products
        """
    #    if not is_supervisor:
    #        return self.filter( Q(limited_day=-1) | Q(limited_day=datetime.today().weekday()), parent=None, is_public=True, is_supervisor_only=False)
        return self.filter( Q(limited_day=-1) | Q(limited_day=datetime.today().weekday()), parent=None, is_public=True)