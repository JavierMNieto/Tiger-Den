from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

class MiniCartContentView(TemplateView):
    """
    Get mini cart of supervisor
    """
    context_object_name = "mini_cart"
    template_name = 'oscar/basket/partials/basket_quick.html'
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)