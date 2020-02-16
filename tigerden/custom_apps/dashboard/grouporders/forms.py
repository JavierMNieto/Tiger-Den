from django import forms
from django.http import QueryDict
from oscar.core.loading import get_model
from oscar.forms.widgets import DatePickerInput
from django.utils.translation import gettext_lazy as _

GroupOrder = get_model('order', 'GroupOrder')
SourceType = get_model('payment', 'SourceType')

class GroupOrderSearchForm(forms.Form):
    order_number = forms.CharField(required=False, label=_("Order number"))
    name = forms.CharField(required=False, label=_("Supervisor name"))
    #product_title = forms.CharField(required=False, label=_("Product name"))
    #upc = forms.CharField(required=False, label=_("UPC"))
    #partner_sku = forms.CharField(required=False, label=_("Partner SKU"))

    status_choices = (('', '---------'),) + tuple([(v, v)
                                                   for v
                                                   in GroupOrder.all_statuses()])
    status = forms.ChoiceField(choices=status_choices, label=_("Status"),
                               required=False)

    date_from = forms.DateField(
        required=False, label=_("Date from"), widget=DatePickerInput)
    date_to = forms.DateField(
        required=False, label=_("Date to"), widget=DatePickerInput)

    #voucher = forms.CharField(required=False, label=_("Voucher code"))

    payment_method = forms.ChoiceField(
        label=_("Payment method"), required=False,
        choices=())

    format_choices = (('html', _('HTML')),
                      ('csv', _('CSV')),)
    response_format = forms.ChoiceField(widget=forms.RadioSelect,
                                        required=False, choices=format_choices,
                                        initial='html',
                                        label=_("Get results as"))

    def __init__(self, *args, **kwargs):
        # Ensure that 'response_format' is always set
        if 'data' in kwargs:
            data = kwargs['data']
            del(kwargs['data'])
        elif len(args) > 0:
            data = args[0]
            args = args[1:]
        else:
            data = None

        if data:
            if data.get('response_format', None) not in self.format_choices:
                # Handle POST/GET dictionaries, which are unmutable.
                if isinstance(data, QueryDict):
                    data = data.dict()
                data['response_format'] = 'html'

        super().__init__(data, *args, **kwargs)
        self.fields['payment_method'].choices = self.payment_method_choices()

    def payment_method_choices(self):
        return (('', '---------'),) + tuple(
            [(src.code, src.name) for src in SourceType.objects.all()])