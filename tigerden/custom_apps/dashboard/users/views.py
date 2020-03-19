from oscar.apps.dashboard.users import views
from django.http import Http404, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.urls import reverse
from oscar.core.compat import get_user_model
from oscar.templatetags.currency_filters import currency
from django.contrib.auth.models import Group
from oscar_accounts import models, facade, exceptions
from decimal import Decimal as D

User = get_user_model()

supervisor_group = Group.objects.get(name='Supervisor')
bank = models.Account.objects.get(id=4)

class UserDetailView(views.UserDetailView):
    actions = ('change_supervisor', 'credit_action', 'make_credit_acct')
    credit_actions = ('deposit', 'withdraw')

    def post(self, request, *args, **kwargs):
        action = request.POST.get("user_action", "")
        user   = User.objects.get(pk=kwargs['pk'])

        if action in self.actions:
            return getattr(self, action)(request, user)

        return self.reload_page(user.pk, error=_("No valid action submitted"))

    def make_credit_acct(self, request, user):
        if user.accounts.exists():
            return self.reload_page(user.pk, error=_("User already has a default credit account"))
        
        account = models.Account.objects.create(primary_user=user, name=user.username)
        account.save()
        messages.success(self.request, _("Successfully created credit account"))
        return self.reload_page(user.pk)

    def credit_action(self, request, user):
        action = request.POST.get('credit_action', "")

        if action not in self.credit_actions:
            return self.reload_page(user.pk, error=_("No valid credit action submitted"))

        amount = D(str(request.POST.get("amount", 0.00)))

        try:
            getattr(self, action)(amount, request.user, user)
        except exceptions.AccountException as e:
            messages.error(self.request,
                           _(str(e)))
        else:
            messages.success(
                self.request,
                _("%s %s") % (currency(amount), action))
        return self.reload_page(user.pk)

    def deposit(self, amount, staff, user):
        facade.transfer(
                source=bank,
                destination=user.accounts.first(),
                amount=amount,
                user=staff,
                description=_("Credit Deposit")
            )
    
    def withdraw(self, amount, staff, user):
        facade.transfer(
                source=user.accounts.first(),
                destination=bank,
                amount=amount,
                user=staff,
                description=_("Credit Withdraw")
            )

    def change_supervisor(self, request, user):
        if user.is_supervisor():
            supervisor_group.user_set.remove(user)
            messages.info(request, "Removed supervisor permissions from " + user.label())
        else:
            supervisor_group.user_set.add(user)
            messages.info(request, "Added supervisor permissions to " + user.label())
        
        return self.reload_page(user.pk)
    
    def reload_page(self, pk, fragment=None, error=None):
        url = reverse('dashboard:user-detail',
                      kwargs={'pk': pk})
        if fragment:
            url += '#' + fragment
        if error:
            messages.error(self.request, error)
        return HttpResponseRedirect(url)