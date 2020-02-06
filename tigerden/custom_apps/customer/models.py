from django.contrib import auth

def is_supervisor(user):
    return user.groups.filter(name='Supervisor').exists()

auth.models.User.add_to_class('is_supervisor', is_supervisor)

from oscar.apps.customer.models import *  # noqa isort:skip
