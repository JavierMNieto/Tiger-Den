from oscar.apps.checkout.forms import ShippingAddressForm

class ShippingAddressForm(ShippingAddressForm):

    class Meta:
        fields = [
            'first_name', 'last_name', 'supervisor'
        ]