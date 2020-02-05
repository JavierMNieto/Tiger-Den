from django.db import models
from django.utils.translation import gettext_lazy as _
from oscar.apps.address.abstract_models import AbstractUserAddress

class UserAddress(AbstractUserAddress):
    location = models.CharField(_("Location"), max_length=120, blank=False, default="Tiger Den")

from oscar.apps.address.models import *  # noqa isort:skip