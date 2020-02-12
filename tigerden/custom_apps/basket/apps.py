import oscar.apps.basket.apps as apps
from oscar.core.loading import get_class
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

class BasketConfig(apps.BasketConfig):
    name = 'custom_apps.basket'
    
    def ready(self):
        super().ready()
        self.mini_reqs_view = get_class('basket.views', 'MiniReqsCartView')
        self.cart_reqs_view = get_class('basket.views', 'ReqsCartView')
        self.cancel_request_view = get_class('basket.views', 'RequestCancelView')
    
    def get_urls(self):
        urls = [
            url(r'^$', self.summary_view.as_view(), name='summary'),
            url(r'^add/(?P<pk>\d+)/$', self.add_view.as_view(), name='add'),
            url(r'^vouchers/add/$', self.add_voucher_view.as_view(),
                name='vouchers-add'),
            url(r'^vouchers/(?P<pk>\d+)/remove/$',
                self.remove_voucher_view.as_view(), name='vouchers-remove'),
            url(r'^saved/$', login_required(self.saved_view.as_view()),
                name='saved'),
            url(r'^minireqscart/$', self.mini_reqs_view.as_view(), name='mini-reqs-cart'),
            url(r'^reqscart/$', self.cart_reqs_view.as_view(), name='reqs-cart'),
            url(r'^req/(?P<pk>\d+)/remove/$', self.cancel_request_view.as_view(), name='req-cancel'),
        ]
        return self.post_process_urls(urls)
        