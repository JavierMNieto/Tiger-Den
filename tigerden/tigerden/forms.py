from django import forms

class TeacherForm(forms.Form):
    name  = forms.CharField(label='Your Name', max_length=100, widget=forms.TextInput(attrs={'class' : 'form-control text-center w-75 mx-auto'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class' : 'form-control text-center w-75 mx-auto'}))