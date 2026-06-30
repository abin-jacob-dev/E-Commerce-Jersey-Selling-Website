from django import forms
from .models import Addresses
from userauths.models import Account


class AddressesForm(forms.ModelForm):
    class Meta:
        model = Addresses
        fields = [
            "full_name",
            "phone_number",
            "address_line_1",
            "address_line_2",
            "state",
            "city",
            "place",
            "postal_code",
            "address_label",
            "is_default",
        ]


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['profile_image','full_name','phone_number']
    def clean_full_name(self):
        full_name= self.cleaned_data.get('full_name')
        if not full_name:
            raise forms.ValidationError('Full name is required.')
        if len(full_name)<3:
            raise forms.ValidationError('Full name must be at least 3 characters.')
        if not full_name.replace(' ','').isalpha():
            raise forms.ValidationError('Full name must contain only letters.')
        return full_name.strip()
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():
            raise forms.ValidationError('Phone number must contain only digits.')
        if len(phone_number)<10 or len(phone_number)>15:
            raise forms.ValidationError('Phone number must be 10–15 digits.')
        return phone_number

class ReferralForm(forms.Form):
    referral_code = forms.CharField(max_length=20)
