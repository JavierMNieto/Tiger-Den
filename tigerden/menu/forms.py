from django import forms
from menu.models import Order
from .fields import ListTextWidget

class ItemForm(forms.Form):
    id       = forms.CharField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(label='', initial=1, min_value=1, widget=forms.TextInput(attrs={'class' : 'form-control text-center pr-0 mr-1 w-25', 'placeholder': 'Quantity', 'type': 'number', 'min': '1'}))

class OrderForm(forms.Form):
    items = forms.CharField(max_length=1024, widget=forms.HiddenInput())
    name  = forms.CharField(label='Your Name', max_length=100, widget=forms.TextInput(attrs={'class' : 'form-control text-center w-75 mx-auto'}))
    user  = forms.CharField(label='Your Supervisor', max_length=100, required=True)

    def __init__(self, *args, **kwargs):
        _staff_list = kwargs.pop('data_list', None)
        super(FormForm, self).__init__(*args, **kwargs)

        self.fields['user'].widget = ListTextWidget(data_list=_staff_list, name='staff-list', attrs={'class' : 'form-control text-center w-75 mx-auto'})

class GroupOrderForm(forms.Form):
    orders = forms.CharField(max_length=2048, widget=forms.HiddenInput())
    personal_items = forms.CharField(max_length=1024, widget=forms.HiddenInput())
    location = forms.CharField(label='Your Location', max_length=100, widget=forms.TextInput(attrs={'class' : 'form-control text-center w-75 mx-auto'}))