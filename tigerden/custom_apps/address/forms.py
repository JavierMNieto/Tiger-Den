from oscar.apps.address import forms as base_forms

class UserAddressForm(base_forms.UserAddressForm):
    class Meta(base_forms.UserAddressForm.Meta):
        fields = ['location']