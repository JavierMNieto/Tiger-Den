from django import forms
from django.utils.translation import gettext_lazy as _
from oscar.apps.basket.forms import AddToBasketForm as CustomAddToBasketForm


class AddToBasketForm(CustomAddToBasketForm):
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