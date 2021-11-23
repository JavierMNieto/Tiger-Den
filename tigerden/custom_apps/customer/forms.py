from oscar.apps.customer.forms import EmailUserCreationForm as CoreEmailUserCreationForm
from oscar.core.compat import get_user_model

from django import forms
from django.utils.translation import gettext_lazy as _

from decimal import Decimal as D

User = get_user_model()


def get_customers_tuple():
    customers = ()
    try:
        for user in User.objects.all():
            customers += ((user.pk, user.label()),)
    except:
        pass
    return customers


class EmailUserCreationForm(CoreEmailUserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name',)

        def save(self, commit=True):
            user = super().save(commit=False)
            user.set_password(self.cleaned_data['password1'])

            if commit:
                user.save()
            return user


class TransferGiftForm(forms.Form):
    """
    Form to get user's supervisor
    """

    receiver = forms.ChoiceField(
        required=True,
        choices=get_customers_tuple())

    amount = forms.DecimalField(
        decimal_places=2, max_digits=12, min_value=D("0.00"))

    def __init__(self, *args, **kwargs):
        super(TransferGiftForm, self).__init__(*args, **kwargs)
