from django import forms
from django.utils.translation import gettext_lazy as _
from oscar.apps.basket import forms as base_forms
from oscar.core.loading import get_model
from oscar.forms.widgets import DateTimePickerInput, ImageInput
from django.db.models.query import QuerySet

Option = get_model('catalogue', 'option')

def _option_text_field(attribute):
    return forms.CharField(label=attribute.name,
                           required=attribute.required)


def _option_textarea_field(attribute):
    return forms.CharField(label=attribute.name,
                           widget=forms.Textarea(),
                           required=attribute.required)


def _option_integer_field(attribute):
    return forms.IntegerField(label=attribute.name,
                              required=attribute.required)


def _option_boolean_field(attribute):
    return forms.BooleanField(label=attribute.name,
                              required=attribute.required,
                              widget=forms.CheckboxInput())


def _option_float_field(attribute):
    return forms.FloatField(label=attribute.name,
                            required=attribute.required)


def _option_date_field(attribute):
    return forms.DateField(label=attribute.name,
                           required=attribute.required,
                           widget=forms.widgets.DateInput)


def _option_datetime_field(attribute):
    return forms.DateTimeField(label=attribute.name,
                               required=attribute.required,
                               widget=DateTimePickerInput())


def _option_option_field(attribute):
    return forms.ModelChoiceField(
        label=attribute.name,
        required=attribute.required,
        queryset=attribute.option_group.options.all())


def _option_multi_option_field(attribute):
    return forms.ModelMultipleChoiceField(
        label=attribute.name + " <small>(multi select)</small>",
        required=attribute.required,
        queryset=attribute.option_group.options.all())


def _option_entity_field(attribute):
    # Product entities don't have out-of-the-box supported in the ProductForm.
    # There is no ModelChoiceField for generic foreign keys, and there's no
    # good default behaviour anyway; offering a choice of *all* model instances
    # is hardly useful.
    return None


def _option_numeric_field(attribute):
    return forms.FloatField(label=attribute.name,
                            required=attribute.required)


def _option_file_field(attribute):
    return forms.FileField(
        label=attribute.name, required=attribute.required)


def _option_image_field(attribute):
    return forms.ImageField(
        label=attribute.name, required=attribute.required)

class AddToBasketForm(base_forms.AddToBasketForm):
    
    OPTION_FIELD_FACTORIES = {
        "text": _option_text_field,
        "richtext": _option_textarea_field,
        "integer": _option_integer_field,
        "boolean": _option_boolean_field,
        "float": _option_float_field,
        "date": _option_date_field,
        "datetime": _option_datetime_field,
        "option": _option_option_field,
        "multi_option": _option_multi_option_field,
        "entity": _option_entity_field,
        "numeric": _option_numeric_field,
        "file": _option_file_field,
        "image": _option_image_field,
    }

    def clean(self):
        info = self.basket.strategy.fetch_for_product(self.product)
        
        # Check that a price was found by the strategy
        if not info.price.exists:
            raise forms.ValidationError(
                _("This product cannot be added to the basket because a "
                  "price could not be determined for it."))

        # Check currencies are sensible
        if (self.basket.currency
                and info.price.currency != self.basket.currency):
            raise forms.ValidationError(
                _("This product cannot be added to the basket as its currency "
                  "isn't the same as other products in your basket"))

        # Check user has permission to add the desired quantity to their
        # basket.
        current_qty = self.basket.product_quantity(self.product)
        desired_qty = current_qty + self.cleaned_data.get('quantity', 1)
        is_permitted, reason = info.availability.is_purchase_permitted(
            desired_qty)
        if not is_permitted:
            raise forms.ValidationError(reason)

        return self.cleaned_data
    
    def _add_option_field(self, product, option):
        """
        Creates the appropriate form field for the product option.
        This is designed to be overridden so that specific widgets can be used
        for certain types of options.
        """
        field = self.OPTION_FIELD_FACTORIES[option.type](option)
        
        if field:
            self.fields[option.code] = field
    
    def cleaned_options(self):
        """
        Return submitted options in a clean format
        """
        options = []
        for option in self.parent_product.options:
            if option.code in self.cleaned_data:
                value = self.cleaned_data[option.code]
                if isinstance(value, QuerySet):
                    new_value = ""
                    for val in value.all():
                        if len(new_value) > 0:
                            new_value += ", "
                        new_value += str(val)
                    value = new_value
                
                if value is None:
                    value = ""    
                       
                options.append({
                    'option': option,
                    'value': value})
        return options
        
class SimpleAddToBasketForm(AddToBasketForm):
    """
    Simplified version of the add to basket form where the quantity is
    defaulted to 1 and rendered in a hidden widget

    Most of the time, you won't need to override this class. Just change
    AddToBasketForm to change behaviour in both forms at once.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'quantity' in self.fields:
            self.fields['quantity'].initial = 1
            self.fields['quantity'].widget = forms.HiddenInput()