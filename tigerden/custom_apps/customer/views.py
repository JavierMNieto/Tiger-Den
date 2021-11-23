import datetime

from oscar.apps.customer import views
from oscar.core.compat import get_user_model
from oscar.core.loading import get_model, get_class
from oscar.views.generic import PostActionMixin

from oscar_accounts import models as acct_models, facade, exceptions as acct_exceptions
from oscar_accounts.dashboard.forms import TransferSearchForm

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.template.loader import render_to_string

from decimal import Decimal as D

from custom_apps.customer.token import acct_activation_token
from .forms import TransferGiftForm

User = get_user_model()

try:
    supervisor_group = Group.objects.get(name='Supervisor')
except:
    supervisor_group = None

PageTitleMixin = get_class('customer.mixins', 'PageTitleMixin')

Account = get_model('oscar_accounts', 'Account')
Transfer = get_model('oscar_accounts', 'Transfer')
Transaction = get_model('oscar_accounts', 'Transaction')

# =======
# Account
# =======


class AccountAuthView(views.AccountAuthView):
    def validate_registration_form(self):
        form = self.get_registration_form(bind_data=True)
        if form.is_valid():
            user = self.register_user(form)

            msg = self.get_registration_success_message(form)
            messages.success(self.request, msg)

            if getattr(settings, 'SUPERVISOR_EMAIL_HOST') in user.email:
                messages.info(
                    self.request, self.get_supervisor_registration_message(user))

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
        token = kwargs['token']
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            messages.error(request, message=_("Invalid user id!"))
        else:
            if acct_activation_token.check_token(user, token) and getattr(settings, 'SUPERVISOR_EMAIL_HOST', user.email):
                supervisor_group.user_set.add(user)
                messages.success(request, message=_(
                    "Successfully confirmed supervisor account!"))
            else:
                messages.error(request, message=_(
                    "Activation link is invalid!"))
        return super().get(request, *args, **kwargs)

# ================
# Transfer history
# ================


class AccountTransactionsView(PageTitleMixin, PostActionMixin, generic.ListView):
    model = Transaction
    context_object_name = 'transfers'
    template_name = 'oscar/customer/transfer/transfer_list.html'
    form_class = TransferSearchForm
    description = _("All transfers")
    page_title = _('Transfer History')
    paginate_by = getattr(
        settings, 'OSCAR_ACCOUNTS_DASHBOARD_ITEMS_PER_PAGE', 20)
    active_tab = 'transfers'

    def do_undo_transfer(self, account):
        if "pk" in self.request.POST:
            try:
                transfer = Transfer.objects.get(pk=self.request.POST["pk"])
            except Transfer.DoesNotExist:
                messages.error(self.request, "Invalid transfer!")
            else:
                facade.reverse(transfer,
                               description="Reversed credit gift")
                messages.success(
                    self.request, "Successfully reversed transfer!")
        else:
            messages.error(self.request, "Missing transfer id!")

        self.response = self.get(self.request)

    def do_send_credits(self, account):
        self.gift_form = TransferGiftForm(self.request.POST)

        if self.gift_form.is_valid():
            data = self.gift_form.cleaned_data

            try:
                receiver = User.objects.get(id=data["receiver"])
                if not receiver.accounts.exists():
                    raise Account.DoesNotExist()
                receiver_acct = receiver.accounts.first()
            except User.DoesNotExist or Account.DoesNotExist:
                messages.error(self.request, "Invalid user set as receiver!")
            else:
                if receiver.id != self.request.user.id:
                    amount = D(data["amount"])
                    if not amount.is_nan() and amount.is_finite() and amount > 0.00:
                        if amount <= account.balance:
                            transfer = None
                            try:
                                transfer = facade.transfer(
                                    source=account,
                                    destination=receiver_acct,
                                    amount=amount,
                                    user=self.request.user,
                                    description=_("Credit gift to %s from %s" % (
                                        receiver.label(), self.request.user.label()))
                                )
                            except acct_exceptions.AccountException as e:
                                if transfer:
                                    facade.reverse(transfer)
                                messages.error(
                                    self.request, "Unable to send credits!")
                            else:
                                messages.success(self.request,
                                                 render_to_string("oscar/customer/transfer/undo_transfer_form.html",
                                                                  context={
                                                                      "transfer": transfer},
                                                                  request=self.request))
                        else:
                            messages.error(
                                self.request, "You have insufficient credits!")
                    else:
                        messages.error(self.request, "Invalid amount set!")
                else:
                    messages.error(
                        self.request, "You can't send credits to yourself!")
        else:
            messages.error(self.request, "Form was not valid!")

        self.response = self.get(self.request)

    def get_object(self):
        return get_object_or_404(Account, id=self.request.user.accounts.first().id)

    def get(self, request, *args, **kwargs):
        self.account = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['account'] = self.account
        ctx['form'] = self.form
        ctx['gift_form'] = TransferGiftForm()
        ctx['queryset_description'] = self.description
        return ctx

    def get_queryset(self):
        queryset = self.account.transactions.all().order_by('-date_created')

        if 'reference' not in self.request.GET:
            # Form not submitted
            self.form = self.form_class()
            return queryset

        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            # Form submitted but invalid
            return queryset

        # Form valid - build queryset and description
        data = self.form.cleaned_data
        desc_template = _(
            "Transfers %(reference)s %(date)s")
        desc_ctx = {
            'reference': "",
            'date': "",
        }
        if data['reference']:
            queryset = queryset.filter(reference=data['reference'])
            desc_ctx['reference'] = _(
                " with reference '%s'") % data['reference']

        if data['start_date'] and data['end_date']:
            # Add 24 hours to make search inclusive
            date_from = data['start_date']
            date_to = data['end_date'] + datetime.timedelta(days=1)
            queryset = queryset.filter(date_created__gte=date_from).filter(
                date_created__lt=date_to)
            desc_ctx['date'] = _(" created between %(start_date)s and %(end_date)s") % {
                'start_date': data['start_date'],
                'end_date': data['end_date']}
        elif data['start_date']:
            queryset = queryset.filter(date_created__gte=data['start_date'])
            desc_ctx['date'] = _(" created since %s") % data['start_date']
        elif data['end_date']:
            date_to = data['end_date'] + datetime.timedelta(days=1)
            queryset = queryset.filter(date_created__lt=date_to)
            desc_ctx['date'] = _(" created before %s") % data['end_date']

        self.description = desc_template % desc_ctx
        return queryset


class TransferDetailView(PageTitleMixin, PostActionMixin, generic.DetailView):
    model = Transfer
    active_tab = 'transfers'

    def get_template_names(self):
        return ["oscar/customer/transfer/transfer_detail.html"]

    def get_page_title(self):
        """
        Transfer reference as page title
        """
        return '%s %s' % (_('Transfer'), self.object.reference)

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, reference=self.kwargs['reference'])
