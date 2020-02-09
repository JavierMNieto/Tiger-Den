from django.contrib import auth
from django.conf import settings

def is_supervisor(user):
    return user.groups.filter(name='Supervisor').exists()

def get_order_requests(user):
    if not user.is_supervisor():
        return None
    
    return user.order_requests.all().filter(status=settings.OSCAR_INITIAL_ORDER_STATUS)

auth.models.User.add_to_class('is_supervisor', is_supervisor)
auth.models.User.add_to_class('get_order_requests', get_order_requests)

from oscar.apps.customer.models import *  # noqa isort:skip
