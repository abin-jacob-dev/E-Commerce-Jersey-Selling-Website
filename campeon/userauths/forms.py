from django import forms
from .models import Account
import re


class UserSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    referral_code = forms.CharField(max_length=50, required=False)

    class Meta:
        model = Account
        fields = ["email", "full_name"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords doesn't match")
        return cleaned_data

    def clean_full_name(self):
        full_name = self.cleaned_data.get("full_name").strip()
        if not re.fullmatch(r"^[A-Za-z ]+$", full_name):
            raise forms.ValidationError(
                "Full name should contain only letters and spaces."
            )
        if len(full_name) < 3:
            raise forms.ValidationError("Minimum length of name is 3")
        return full_name

    def clean_password(self):
        password = self.cleaned_data.get("password")

        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters")

        if not re.search(r"[A-Z]", password):
            raise forms.ValidationError(
                "Password must contain at least one uppercase letter"
            )

        if not re.search(r"[a-z]", password):
            raise forms.ValidationError(
                "Password must contain at least one lowercase letter"
            )

        if not re.search(r"\d", password):
            raise forms.ValidationError("Password must contain at least one number")

        if not re.search(r"[@$!%*?&]", password):
            raise forms.ValidationError(
                "Password must contain at least one special character"
            )

        return password
