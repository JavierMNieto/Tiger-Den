import oscar.apps.checkout.apps as apps
from oscar.core.loading import get_class
from django.conf.urls import url

class CheckoutConfig(apps.CheckoutConfig):
    name = 'custom_apps.checkout'

    def ready(self):
        super().ready()
        
        self.supervisor_info_view = get_class('checkout.views', 'GuestSupervisorView')

    def get_urls(self):
        urls = [
            url(r'^$', self.index_view.as_view(), name='index'),

            # Guest Views
            url(r'supervisor-info/$', self.supervisor_info_view.as_view(), name='supervisor-info'),
            

            # Shipping/user address views
            #url(r'shipping-address/$', self.shipping_address_view.as_view(), name='shipping-address'),
            #url(r'user-address/edit/(?P<pk>\d+)/$', self.user_address_update_view.as_view(), name='user-address-update'),
            #url(r'user-address/delete/(?P<pk>\d+)/$', self.user_address_delete_view.as_view(), name='user-address-delete'),

            # Shipping method views
            #url(r'shipping-method/$', self.shipping_method_view.as_view(), name='shipping-method'),

            # Payment views
            #url(r'payment-method/$', self.payment_method_view.as_view(), name='payment-method'),
            #url(r'payment-details/$', self.payment_details_view.as_view(), name='payment-details'),

            # Preview and thankyou
            url(r'preview/$',
                self.payment_details_view.as_view(preview=True),
                name='preview'),
            
            url(r'thank-you/$', self.thankyou_view.as_view(),
                name='thank-you'),
        ]
        
        return self.post_process_urls(urls)