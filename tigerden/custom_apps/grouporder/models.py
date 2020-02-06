from django.db import models
from django.utils.translation import gettext_lazy as _
from oscar.core.compat import AUTH_USER_MODEL

class GroupOrder(models.Model):
    """
    Group Order Model
    """
    
    number = models.CharField(_("Group Order number"), max_length=128, db_index=True, unique=True)
    # Supervisor placing order
    user = models.ForeignKey(
        AUTH_USER_MODEL, related_name='grouporders', null=True,
        verbose_name=_("Supervisor"), on_delete=models.SET_NULL)