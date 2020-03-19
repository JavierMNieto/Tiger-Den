from django.contrib.auth.models import User
from django.conf import settings
from decimal import Decimal as D

def is_supervisor(user):
    return user.groups.filter(name='Supervisor').exists()

def get_order_requests(user):
    return user.order_requests.all().filter(status=settings.OSCAR_INITIAL_ORDER_STATUS).order_by('user')

def get_reqs_total(user):
    reqs = user.get_order_requests()
    
    total = D('0.00')
    
    for req in reqs:
        total += req.total_excl_tax
    
    return total    

def label(user):
    if user.get_full_name().strip() == "":
        return user.email
    return user.get_full_name()

def get_bal(user):
    accounts = user.accounts
    if accounts.exists():
        return accounts.first().balance
    return D('0.00')

User.add_to_class('is_supervisor', is_supervisor)
User.add_to_class('get_order_requests', get_order_requests)
User.add_to_class('get_reqs_total', get_reqs_total)
User.add_to_class('label', label)
User.add_to_class('get_bal', get_bal)

from oscar.apps.customer.models import *  # noqa isort:skip
