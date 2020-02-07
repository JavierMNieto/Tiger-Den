#from oscar.apps.checkout.forms import 
from django import forms
from django.contrib import auth

from . import fields

def get_supervisors_tuple():
    supervisors = ()
    
    for user in auth.models.User.objects.filter(groups__name='Supervisor'):
        name = user.get_full_name()
        if name.strip() == "":
            name = user.email
        supervisors += ((user.pk, name),)
    
    return supervisors

class GuestSupervisorForm(forms.Form):
    """
    Form to get guest's supervisor
    """
    
    supervisor = forms.CharField(required=True)
    
    def __init__(self, *args, **kwargs):
        super(GuestSupervisorForm, self).__init__(*args, **kwargs)
        
        self.fields['supervisor'].widget = fields.ListTextWidget(data_list=get_supervisors_tuple(), 
                                                                 name='supervisor-list', 
                                                                 attrs={'class': 'form-control m-1'})