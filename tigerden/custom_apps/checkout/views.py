from oscar.apps.checkout import views, signals
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from oscar.core.loading import get_classes, get_class
from django.contrib import messages
from django.utils.http import urlquote
from django.contrib.auth import login
from django.shortcuts import redirect
from django import http

logger = views.logger

SupervisorForm, PaymentMethodForm, LocationForm \
    = get_classes('checkout.forms', ['SupervisorForm',
                                         'PaymentMethodForm',
                                         'LocationForm'])

UnableToPlaceOrder = get_class('order.exceptions', 'UnableToPlaceOrder')
RedirectRequired, UnableToTakePayment, PaymentError \
    = get_classes('payment.exceptions', ['RedirectRequired',
                                         'UnableToTakePayment',
                                         'PaymentError'])

class IndexView(views.IndexView):
    success_url = reverse_lazy("checkout:supervisor-info") # stage 1
    
    def form_valid(self, form):
        if form.is_guest_checkout() or form.is_new_account_checkout():
            email = form.cleaned_data['username']
            self.checkout_session.set_guest_email(email)

            # We raise a signal to indicate that the user has entered the
            # checkout process by specifying an email address.
            signals.start_checkout.send_robust(
                sender=self, request=self.request, email=email)

            if form.is_new_account_checkout():
                messages.info(
                    self.request,
                    _("Create your account and then you will be redirected "
                      "back to the checkout process"))
                self.success_url = "%s?next=%s&email=%s" % (
                    reverse('customer:register'),
                    reverse('checkout:supervisor-info'), # guest stage 1
                    urlquote(email)
                )
        else:
            #if self.request.user.is_supervisor():
            #    self.success_url = 'checkout:supervisor-info' # change to supervisor stage 1
            user = form.get_user()
            login(self.request, user)

            # We raise a signal to indicate that the user has entered the
            # checkout process.
            signals.start_checkout.send_robust(
                sender=self, request=self.request)

        return redirect(self.get_success_url())

# =============
# Payment Views
# =============

class PaymentMethodView(views.CheckoutSessionMixin, generic.FormView):
    """
    Determine the user's method of payment (either through credits or cash)
    """
    template_name = 'oscar/checkout/payment_method.html'
    form_class = PaymentMethodForm
    success_url = reverse_lazy('checkout:payment-details')
    
    pre_conditions = [
        'check_basket_is_not_empty',
        'check_basket_is_valid',
        'check_user_email_is_captured',
        'check_order_has_supervisor']

    #skip_conditions = ['skip_unless_payment_is_required']
    
    def form_valid(self, form):
        self.checkout_session.pay_by(form.cleaned_data['payment_method'])
        return super().form_valid(form)
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_supervisor() and request.basket.is_empty:
            self.success_url = reverse_lazy('checkout:order-requests')
            return self.get_success_response()
        
        return super().get(request, *args, **kwargs)
    
    def get_success_response(self):
        return redirect(self.get_success_url())

class PaymentDetailsView(views.PaymentDetailsView):
    pre_conditions = [
        'check_basket_is_not_empty',
        'check_basket_is_valid',
        'check_user_email_is_captured',
        'check_order_has_supervisor',
        'check_order_has_payment',
        'check_order_has_location']
    
    preview = True
    
    def submit(self, user, basket, shipping_address, shipping_method,  # noqa (too complex (10))
               shipping_charge, billing_address, order_total,
               payment_kwargs=None, order_kwargs=None, location=None):
        """
        Submit a basket for order placement.

        The process runs as follows:

         * Generate an order number
         * Freeze the basket so it cannot be modified any more (important when
           redirecting the user to another site for payment as it prevents the
           basket being manipulated during the payment process).
         * Attempt to take payment for the order
           - If payment is successful, place the order
           - If a redirect is required (e.g. PayPal, 3D Secure), redirect
           - If payment is unsuccessful, show an appropriate error message

        :basket: The basket to submit.
        :payment_kwargs: Additional kwargs to pass to the handle_payment
                         method. It normally makes sense to pass form
                         instances (rather than model instances) so that the
                         forms can be re-rendered correctly if payment fails.
        :order_kwargs: Additional kwargs to pass to the place_order method
        """
        if payment_kwargs is None:
            payment_kwargs = {}
        if order_kwargs is None:
            order_kwargs = {}
        if location is None:
            location = "Tiger Den"
            
        # Taxes must be known at this point
        #assert basket.is_tax_known, (
        #    "Basket tax must be set before a user can place an order")
        #assert shipping_charge.is_tax_known, (
        #    "Shipping charge tax must be set before a user can place an order")

        # We generate the order number first as this will be used
        # in payment requests (ie before the order model has been
        # created).  We also save it in the session for multi-stage
        # checkouts (e.g. where we redirect to a 3rd party site and place
        # the order on a different request).
        order_number = self.generate_order_number(basket)
        self.checkout_session.set_order_number(order_number)
        logger.info("Order #%s: beginning submission process for basket #%d",
                    order_number, basket.id)

        # Freeze the basket so it cannot be manipulated while the customer is
        # completing payment on a 3rd party site.  Also, store a reference to
        # the basket in the session so that we know which basket to thaw if we
        # get an unsuccessful payment response when redirecting to a 3rd party
        # site.
        self.freeze_basket(basket)
        self.checkout_session.set_submitted_basket(basket)

        # We define a general error message for when an unanticipated payment
        # error occurs.
        error_msg = _("A problem occurred while processing payment for this "
                      "order - no payment has been taken.  Please "
                      "contact customer services if this problem persists")

        signals.pre_payment.send_robust(sender=self, view=self)

        try:
            self.handle_payment(order_number, order_total, **payment_kwargs)
        except RedirectRequired as e:
            # Redirect required (e.g. PayPal, 3DS)
            logger.info("Order #%s: redirecting to %s", order_number, e.url)
            return http.HttpResponseRedirect(e.url)
        except UnableToTakePayment as e:
            # Something went wrong with payment but in an anticipated way.  Eg
            # their bankcard has expired, wrong card number - that kind of
            # thing. This type of exception is supposed to set a friendly error
            # message that makes sense to the customer.
            msg = str(e)
            logger.warning(
                "Order #%s: unable to take payment (%s) - restoring basket",
                order_number, msg)
            self.restore_frozen_basket()

            # We assume that the details submitted on the payment details view
            # were invalid (e.g. expired bankcard).
            return self.render_payment_details(
                self.request, error=msg, **payment_kwargs)
        except PaymentError as e:
            # A general payment error - Something went wrong which wasn't
            # anticipated.  Eg, the payment gateway is down (it happens), your
            # credentials are wrong - that king of thing.
            # It makes sense to configure the checkout logger to
            # mail admins on an error as this issue warrants some further
            # investigation.
            msg = str(e)
            logger.error("Order #%s: payment error (%s)", order_number, msg,
                         exc_info=True)
            self.restore_frozen_basket()
            return self.render_preview(
                self.request, error=error_msg, **payment_kwargs)
        except Exception as e:
            # Unhandled exception - hopefully, you will only ever see this in
            # development...
            logger.error(
                "Order #%s: unhandled exception while taking payment (%s)",
                order_number, e, exc_info=True)
            self.restore_frozen_basket()
            return self.render_preview(
                self.request, error=error_msg, **payment_kwargs)

        signals.post_payment.send_robust(sender=self, view=self)

        # If all is ok with payment, try and place order
        logger.info("Order #%s: payment successful, placing order",
                    order_number)
        try:
            return self.handle_order_placement(
                order_number, user, basket, shipping_address, shipping_method,
                shipping_charge, billing_address, order_total, location, **order_kwargs)
        except UnableToPlaceOrder as e:
            # It's possible that something will go wrong while trying to
            # actually place an order.  Not a good situation to be in as a
            # payment transaction may already have taken place, but needs
            # to be handled gracefully.
            msg = str(e)
            logger.error("Order #%s: unable to place order - %s",
                         order_number, msg, exc_info=True)
            self.restore_frozen_basket()
            return self.render_preview(
                self.request, error=msg, **payment_kwargs)

# ===========
# Custom Views
# ===========

class SupervisorView(views.CheckoutSessionMixin, generic.FormView):
    """
    Determine Supervisor of guest to receive and administer guest's order
    """
    template_name = 'oscar/checkout/supervisor.html'
    form_class = SupervisorForm
    success_url = reverse_lazy('checkout:payment-method')
    
    pre_conditions = [
        'check_basket_is_not_empty',
        'check_basket_is_valid',
        'check_user_email_is_captured']
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_supervisor():
            self.checkout_session.set_supervisor(request.user.pk)
            self.success_url = reverse_lazy("checkout:delivery-info")
            return self.get_success_response()
        
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        self.checkout_session.set_supervisor(form.cleaned_data['supervisor'])
        return super().form_valid(form)
    
    def get_success_response(self):
        return redirect(self.get_success_url())

class LocationView(views.CheckoutSessionMixin, generic.FormView):
    """
    Get location of supervisor for delivery
    """
    
    template_name = 'oscar/checkout/location.html'
    form_class = LocationForm
    success_url = reverse_lazy('checkout:payment-method')
    
    pre_conditions = [
        'check_basket_is_not_empty',
        'check_basket_is_valid',
        'check_user_email_is_captured',
        'check_order_has_supervisor']
    
    def form_valid(self, form):
        self.checkout_session.set_location(form.cleaned_data['location'])
        return super().form_valid(form)

class OrderRequestsView(views.OrderPlacementMixin, generic.TemplateView):
    template_name = 'oscar/checkout/order_requests.html'
    
    pre_conditions = [
        'check_basket_is_not_empty',
        'check_user_email_is_captured',
        'check_order_has_location']
    
    def post(self, request, *args, **kwargs):

        # We use a custom parameter to indicate if this is an attempt to place
        # an order (normally from the preview page).  Without this, we assume a
        # payment form is being submitted from the payment details view. In
        # this case, the form needs validating and the order preview shown.
        if request.POST.get('action', '') == 'place_requests':
            return self.place_requests(request)
    
    def place_requests(self, request):
        return super().handle_requests_placement(request.user,
                                          request.user.get_order_requests().first().number,
                                          self.checkout_session.location(),
                                          "USD")