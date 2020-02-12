from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from oscar.core.loading import get_model
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.views.generic import View

class MiniReqsCartView(TemplateView):
    """
    Get students requests of supervisor for the mini cart
    """
    context_object_name = "mini_reqs"
    template_name = 'oscar/basket/partials/requests_quick.html'

class ReqsCartView(TemplateView):
    """
    Get students requests of supervisor for the mini cart
    """
    context_object_name = "reqs_cart"
    template_name = 'oscar/basket/partials/requests_content.html'
    
class RequestCancelView(View):
    order_model = get_model('order', 'Order')
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        response = redirect('basket:summary')

        order_id = kwargs['pk']
        if not request.basket.id:
            return response
        try:
            order = request.basket.owner.get_order_requests().get(id=order_id)
        except ObjectDoesNotExist:
            messages.error(request, _("No order found with id '%s'") % order_id)
        else:
            order.set_status('Cancelled')
            messages.info(request, _("%s Order '%s' has been cancelled") % (order.user.label(), order.number))

        return response