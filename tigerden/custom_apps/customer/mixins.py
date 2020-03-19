from oscar.apps.customer import mixins
from oscar_accounts.models import Account
from oscar.core.compat import get_user_model
from oscar.apps.customer.signals import user_registered

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import login as auth_login, authenticate
from django.conf import settings

from custom_apps.customer.token import acct_activation_token

User = get_user_model()

class RegisterUserMixin(mixins.RegisterUserMixin):
    def register_user(self, form):
        """
        Create a user instance and send a new registration email (if configured
        to).
        """
        user = form.save()

        # Raise signal robustly (we don't want exceptions to crash the request
        # handling).
        user_registered.send_robust(
            sender=self, request=self.request, user=user)

        if getattr(settings, 'SUPERVISOR_EMAIL_HOST') in user.email:
            self.send_supervisor_email(user)
        elif getattr(settings, 'OSCAR_SEND_REGISTRATION_EMAIL', True):
            self.send_registration_email(user)

        # We have to authenticate before login
        try:
            user = authenticate(
                username=user.email,
                password=form.cleaned_data['password1'])
        except User.MultipleObjectsReturned:
            # Handle race condition where the registration request is made
            # multiple times in quick succession.  This leads to both requests
            # passing the uniqueness check and creating users (as the first one
            # hasn't committed when the second one runs the check).  We retain
            # the first one and deactivate the dupes.
            mixins.logger.warning(
                'Multiple users with identical email address and password'
                'were found. Marking all but one as not active.')
            # As this section explicitly deals with the form being submitted
            # twice, this is about the only place in Oscar where we don't
            # ignore capitalisation when looking up an email address.
            # We might otherwise accidentally mark unrelated users as inactive
            users = User.objects.filter(email=user.email)
            user = users[0]
            for u in users[1:]:
                u.is_active = False
                u.save()

        auth_login(self.request, user)

        if not user.accounts.exists():
            account = Account.objects.create(primary_user_id=user.id, name=user.username)
            account.save()
        
        return user
    
    def send_supervisor_email(self, user):
        code = "CONFIRM_SUPERVISOR"
        ctx = {'user': user,
               'site': get_current_site(self.request),
               'uid':urlsafe_base64_encode(force_bytes(user.pk)),
               'token':acct_activation_token.make_token(user),}
        messages = mixins.CommunicationEventType.objects.get_and_render(code, ctx)
        if messages and messages['body']:
            mixins.Dispatcher().dispatch_user_messages(user, messages)