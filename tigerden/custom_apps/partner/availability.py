from oscar.apps.partner import availability
from django.utils.translation import gettext_lazy as _


class Available(availability.Available):
    code = 'instock'


class Unavailable(availability.Unavailable):
    code = 'outofstock'

    def __init__(self, message=_("Unavailable")):
        super().__init__()
        self.message = message


class StockRequired(availability.StockRequired):
    @property
    def short_message(self):
        if self.num_available > 0:
            return _("Available")
        return _("Unavailable")

    @property
    def message(self):
        """
        Full availability text, suitable for detail pages.
        """
        if self.num_available > 0:
            return _("Available")
        return _("Unavailable")
