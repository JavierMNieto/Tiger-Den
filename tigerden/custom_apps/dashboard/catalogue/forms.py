from oscar.apps.dashboard.catalogue import forms as base_forms
from django import forms
from oscar.core.loading import get_model
import uuid

Partner = get_model('partner', 'Partner')
Option  = get_model('catalogue', 'Option')

class ProductForm(base_forms.ProductForm):

    class Meta(base_forms.ProductForm.Meta):
        #fields = ['title', 'upc', 'description', 'is_public', 'is_discountable', 'structure'] do we need upc?
        fields = ['title', 'description', 'limited_day', 'is_public', 'is_discountable', 'is_supervisor_only', 'structure']
    
class ProductClassForm(base_forms.ProductClassForm):

    class Meta(base_forms.ProductClassForm.Meta):
        #fields = ['name', 'requires_shipping', 'track_stock', 'options']
        fields = ['name', 'options']

class StockRecordForm(base_forms.StockRecordForm):
    class Meta(base_forms.StockRecordForm.Meta):
        #fields = [
        #    'partner', 'partner_sku',
        #    'price_currency', 'price_excl_tax', 'price_retail', 'cost_price',
        #    'num_in_stock', 'low_stock_threshold']

        fields = ['price_retail', 'cost_price', 'partner', 'partner_sku', 'num_in_stock']
        
class OptionForm(base_forms.ProductAttributesForm):
    class Meta(base_forms.ProductAttributesForm.Meta):
        model = Option