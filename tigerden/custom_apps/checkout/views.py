from oscar.apps.checkout import views, signals
from django.views import generic
from django.urls import reverse, reverse_lazy
from oscar.core.loading import get_classes, get_class

GuestSupervisorForm = get_class('checkout.forms', 'GuestSupervisorForm')


class IndexView(views.IndexView):
    success_url = "checkout:shipping-address" # change to guest stage 1
    
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
                    reverse('checkout:shipping-address'), # change to guest stage 1
                    urlquote(email)
                )
        else:
            if self.request.user.is_supervisor():
                self.success_url = "" # change to supervisor stage 1
            user = form.get_user()
            login(self.request, user)

            # We raise a signal to indicate that the user has entered the
            # checkout process.
            signals.start_checkout.send_robust(
                sender=self, request=self.request)

        return redirect(self.get_success_url())
    
# ===========
# Guest Views
# ===========

class GuestSupervisorView(views.CheckoutSessionMixin, generic.FormView):
    """
    Determine Supervisor of guest to receive and administer guest's order
    """
    template_name = 'oscar/checkout/guest_supervisor.html'
    form_class = GuestSupervisorForm
    success_url = ""
    
    pre_conditions = [
        'check_basket_is_not_empty',
        'check_basket_is_valid',
        'check_user_email_is_captured']