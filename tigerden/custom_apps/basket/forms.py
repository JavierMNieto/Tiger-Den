from django import forms
from django.utils.translation import gettext_lazy as _
from oscar.apps.basket import forms as base_forms
from oscar.core.loading import get_model

Option = get_model('catalogue', 'option')


class SimpleAddToBasketForm(base_forms.AddToBasketForm):
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
