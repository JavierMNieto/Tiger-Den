from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from oscar.apps.checkout import forms as c_forms


def get_supervisors_tuple():
    supervisors = ()

    try:
        for user in User.objects.filter(groups__name='Supervisor'):
            name = user.get_full_name()
            if name.strip() == "":
                name = user.email
            supervisors += ((user.pk, name),)
    except:
        pass

    return supervisors


class GatewayForm(c_forms.GatewayForm):
    guest_name = forms.CharField(
        max_length=25, required=False, label=_('My name is '))


class SupervisorForm(forms.Form):
    """
    Form to get user's supervisor
    """

    supervisor = forms.ChoiceField(
        label="Supervisor",
        required=True,
        choices=get_supervisors_tuple())

    def __init__(self, *args, **kwargs):
        super(SupervisorForm, self).__init__(*args, **kwargs)


class LocationForm(forms.Form):
    """
    """

    location = forms.CharField(required=True, max_length=50)  # change css

    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)


class PaymentMethodForm(forms.Form):
    """

    """
    payment_method = forms.ChoiceField()
    max_credit_allocation = forms.FloatField(widget=forms.NumberInput(attrs={'min': '0.00'}),
                                             required=False, min_value=0.00)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['payment_method'].choices = (
            (0, "Cash"), (1, "Tiger Den Credit"))
