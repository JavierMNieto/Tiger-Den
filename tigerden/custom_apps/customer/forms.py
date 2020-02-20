from oscar.apps.customer.forms import EmailUserCreationForm as CoreEmailUserCreationForm
from django import forms
from django.utils.translation import gettext_lazy as _
from oscar.core.compat import (existing_user_fields, get_user_model)

User = get_user_model()

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