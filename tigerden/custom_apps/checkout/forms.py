#from oscar.apps.checkout.forms import 
from django import forms
from django.contrib.auth.models import User

from . import fields

def get_supervisors_tuple():
    supervisors = ()
    
    for user in User.objects.filter(groups__name='Supervisor'):
        name = user.get_full_name()
        if name.strip() == "":
            name = user.email
        supervisors += ((user.pk, name),)
    
    return supervisors

class SupervisorForm(forms.Form):
    """
    Form to get user's supervisor
    """
    
    supervisor = forms.CharField(required=True)
    
    def __init__(self, *args, **kwargs):
        super(SupervisorForm, self).__init__(*args, **kwargs)
        
        self.fields['supervisor'].widget = fields.ListTextWidget(data_list=get_supervisors_tuple(), 
                                                                 name='supervisor-list', 
                                                                 attrs={'class': 'form-control'})

class LocationForm(forms.Form):
    """
    """
    
    location = forms.CharField(required=True, max_length=50) # change css
    
    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)

class PaymentMethodForm(forms.Form):
    """
    
    """
    payment_method = forms.ChoiceField() # change css
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['payment_method'].choices = ((0, "Cash"), (1, "Balance"))