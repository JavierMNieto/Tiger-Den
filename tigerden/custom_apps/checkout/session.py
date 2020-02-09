from oscar.apps.checkout import session, exceptions
from django.contrib import auth
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from oscar.core.loading import get_classes, get_class

NoShippingRequired = get_class('shipping.methods', 'NoShippingRequired')

class CheckoutSessionMixin(session.CheckoutSessionMixin):
    def check_order_has_supervisor(self, request):
        # Check that supervisor has been set
        if not self.checkout_session.is_supervisor_set():
            raise exceptions.FailedPreCondition(
                url=reverse('checkout:supervisor-info'),
                message=_("Please choose a supervisor")
            )

        # Check that the supervisor is still valid
        supervisor = auth.models.User.objects.filter(pk=self.checkout_session.supervisor()).first()
        if not supervisor or not supervisor.is_supervisor():
            raise exceptions.FailedPreCondition(
                url=reverse('checkout:supervisor-info'),
                message=_("Your previously chosen supervisor is "
                          "no longer valid.  Please choose another one")
            )
    
    def check_order_has_payment(self, request):
        # Check that supervisor has been set
        if not self.checkout_session.is_payment_method_set():
            raise exceptions.FailedPreCondition(
                url=reverse('checkout:payment-method'),
                message=_("Please choose a payment method")
            )
            
    def check_order_has_location(self, request):
        # Check that supervisor has been set
        if request.user.is_supervisor() and not self.checkout_session.is_location_set():
            raise exceptions.FailedPreCondition(
                url=reverse('checkout:delivery-info'),
                message=_("Please indicate your location")
            )
    
    def build_submission(self, **kwargs):
        """
        Return a dict of data that contains everything required for an order
        submission.  This includes payment details (if any).
        This can be the right place to perform tax lookups and apply them to
        the basket.
        """
        # Pop the basket if there is one, because we pass it as a positional
        # argument to methods below
        basket = kwargs.pop('basket', self.request.basket)
        shipping_address = self.get_shipping_address(basket)
        shipping_method = NoShippingRequired()
        billing_address = self.get_billing_address(shipping_address)
        if not shipping_method:
            total = shipping_charge = None
        else:
            shipping_charge = shipping_method.calculate(basket)
        total = self.get_order_totals(
            basket, shipping_charge=shipping_charge, **kwargs)
        submission = {
            'user': self.request.user,
            'basket': basket,
            'shipping_address': shipping_address,
            'shipping_method': shipping_method,
            'shipping_charge': shipping_charge,
            'billing_address': billing_address,
            'order_total': total,
            'order_kwargs': {
                'supervisor_id': self.checkout_session.supervisor()
            },
            'payment_kwargs': {
                'method': self.checkout_session.payment_method()
            },
            'location': self.checkout_session.location()
        }

        # If there is a billing address, add it to the payment kwargs as calls
        # to payment gateways generally require the billing address. Note, that
        # it normally makes sense to pass the form instance that captures the
        # billing address information. That way, if payment fails, you can
        # render bound forms in the template to make re-submission easier.
        if billing_address:
            submission['payment_kwargs']['billing_address'] = billing_address

        # Allow overrides to be passed in
        submission.update(kwargs)

        # Set guest email after overrides as we need to update the order_kwargs
        # entry.
        user = submission['user']
        if (not user.is_authenticated
                and 'guest_email' not in submission['order_kwargs']):
            email = self.checkout_session.get_guest_email()
            submission['order_kwargs']['guest_email'] = email
        return submission