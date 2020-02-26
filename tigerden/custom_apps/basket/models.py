from oscar.apps.basket.abstract_models import AbstractLine
from django.utils.encoding import smart_str

class Line(AbstractLine):
    @property
    def description(self):
        d = smart_str(self.product)
        ops = []
        for attribute in self.attributes.all():
            if attribute.value.strip() != "":
                ops.append("%s = '%s'" % (attribute.option.name, attribute.value))
        if ops:
            d = "%s (%s)" % (d, ", ".join(ops))
        return d

from oscar.apps.basket.models import *  # noqa isort:skip