"""tigerden URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url
from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
import sys

from . import views

urlpatterns = [
    # The Django admin is not officially supported; expect breakage.
    # Nonetheless, it's often useful for debugging.
    path('admin/', admin.site.urls), # REMOVE IN PRODUCTION
    
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include(apps.get_app_config('oscar').urls[0])),
    url(r'^dashboard/accounts/', apps.get_app_config('accounts_dashboard').urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from custom_apps.partner.models import Partner
from django.contrib.auth.models import Group, User

def one_time_startup():
    """
    Not the best but the easiest way to this...
    """
    if not Partner.objects.exists():
        Partner.objects.create(name='Tiger Den')
    if not Group.objects.filter(name__iexact='Supervisor').exists():
        Group.objects.create(name='Supervisor')
    supervisor_group = Group.objects.get(name='Supervisor')
    
    for staff in User.objects.filter(is_staff=True):
        supervisor_group.user_set.add(staff)

if ('makemigrations' not in sys.argv and 'migrate' not in sys.argv):
    one_time_startup()