from oscar.core.application import OscarDashboardConfig
from oscar.core.loading import get_class
from django.conf.urls import url
from django.utils.translation import gettext_lazy as _

class GroupOrdersDashboardConfig(OscarDashboardConfig):
    name = 'custom_apps.dashboard.grouporders'

    label = 'grouporders_dashboard'
    verbose_name = _('Group Orders dashboard')

    default_permissions = ['is_staff', ]
    
    def ready(self):
        self.grouporder_list_view = get_class('dashboard.grouporders.views', 'GroupOrderListView')
        self.grouporder_detail_view = get_class('dashboard.grouporders.views', 'GroupOrderDetailView')
            
    def get_urls(self):
        urls = [
            url(r'^$', self.grouporder_list_view.as_view(), name='grouporder-list'),
            url(r'^(?P<number>[-\w]+)/$', self.grouporder_detail_view.as_view(), name='grouporder-detail'),
        ]
        return self.post_process_urls(urls)
    