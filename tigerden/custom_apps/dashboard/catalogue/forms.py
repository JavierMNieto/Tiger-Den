from oscar.apps.dashboard.catalogue import forms as base_forms
from django import forms
from oscar.core.loading import get_model
import uuid

Partner = get_model('partner', 'Partner')

class ProductForm(base_forms.ProductForm):

    class Meta(base_forms.ProductForm.Meta):
        #fields = ['title', 'upc', 'description', 'is_public', 'is_discountable', 'structure'] do we need upc?
        fields = ['title', 'description', 'is_public', 'is_discountable', 'structure']
    
class ProductClassForm(base_forms.ProductClassForm):

    class Meta(base_forms.ProductClassForm.Meta):
        #fields = ['name', 'requires_shipping', 'track_stock', 'options']
        fields = ['name', 'options']

class StockRecordForm(base_forms.StockRecordForm):

    def __init__(self, product_class, user, *args, **kwargs):
        super().__init__(product_class, user, *args, **kwargs)
        
        self.fields['partner'].initial = Partner.objects.first().pk # ADD PARTNER AT START OF DATABASE
        self.fields['partner_sku'].initial = uuid.uuid1

    class Meta(base_forms.StockRecordForm.Meta):
        #fields = [
        #    'partner', 'partner_sku',
        #    'price_currency', 'price_excl_tax', 'price_retail', 'cost_price',
        #    'num_in_stock', 'low_stock_threshold']

        fields = ['price_retail', 'partner', 'partner_sku']
        widgets = {
            'partner': forms.HiddenInput(),
            'partner_sku': forms.HiddenInput()
        }