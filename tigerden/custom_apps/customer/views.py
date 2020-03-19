from oscar.apps.customer import views
from oscar.core.compat import get_user_model

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import Group

from custom_apps.customer.token import acct_activation_token

User = get_user_model()
supervisor_group = Group.objects.get(name='Supervisor')

class AccountAuthView(views.AccountAuthView):
    def validate_registration_form(self):
        form = self.get_registration_form(bind_data=True)
        if form.is_valid():
            user = self.register_user(form)

            msg = self.get_registration_success_message(form)
            messages.success(self.request, msg)

            if getattr(settings, 'SUPERVISOR_EMAIL_HOST') in user.email:
                messages.info(self.request, self.get_supervisor_registration_message(user))

            return redirect(self.get_registration_success_url(form))

        ctx = self.get_context_data(registration_form=form)
        return self.render_to_response(ctx)
    
    def get_supervisor_registration_message(self, user):
        return _("To become a supervisor, please confirm the email sent to " + user.email)

class SupervisorActView(generic.RedirectView):
    url = settings.LOGIN_REDIRECT_URL
    permanent = False

    def get(self, request, *args, **kwargs):
        uidb64 = kwargs['uidb64']
        token  = kwargs['token']
        try:
            uid  = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            messages.error(request, message=_("Invalid user id!"))
        else:
            if acct_activation_token.check_token(user, token) and getattr(settings, 'SUPERVISOR_EMAIL_HOST', user.email):
                supervisor_group.user_set.add(user)
                messages.success(request, message=_("Successfully confirmed supervisor account!"))
            else:
                messages.error(request, message=_("Activation link is invalid!"))
        return super().get(request, *args, **kwargs)	 