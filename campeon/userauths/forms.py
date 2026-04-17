from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Account


class UserSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    referral_code = forms.CharField( max_length=50, required=False)
    class Meta:
        model = Account
        fields = ["email", "full_name", "referral_code"]
    def clean(self):
        cleaned_data=super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords doesn't match")
        