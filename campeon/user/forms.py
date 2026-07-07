from django import forms
from .models import Addresses
from userauths.models import Account
import re


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

    def clean_full_name(self):
        full_name = self.cleaned_data.get("full_name")
        if not full_name:
            raise forms.ValidationError("Full name is required.")
        if len(full_name) < 3:
            raise forms.ValidationError("Full name must be at least 3 characters.")
        if not full_name.replace(" ", "").isalpha():
            raise forms.ValidationError("Full name must contain only letters.")
        return full_name.strip()

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if not phone_number:
            raise forms.ValidationError("Phone number is required.")
        phone_number = phone_number.strip()
        if not re.fullmatch(r"^[6-9]\d{9}$", phone_number):
            raise forms.ValidationError("Enter a valid Phone number")
        return phone_number

    def clean_address_line_1(self):
        address_line_1 = self.cleaned_data.get("address_line_1")
        if not address_line_1:
            raise forms.ValidationError("Address Line 1 is required.")
        address_line_1 = address_line_1.strip()
        if len(address_line_1) < 5:
            raise forms.ValidationError("Address is too short")
        if len(address_line_1) > 100:
            raise forms.ValidationError("Address is too long.")
        return address_line_1
    
    def clean_address_line_2(self):
        address = self.cleaned_data.get("address_line_2")
        if address:
            address = address.strip()
            if len(address) > 100:
                raise forms.ValidationError("Address Line 2 is too long.")
        return address

    def clean_city(self):
        city = self.cleaned_data.get("city")
        if not city:
            raise forms.ValidationError("City is required.")
        city = city.strip()
        if not city.replace(" ", "").isalpha():
            raise forms.ValidationError("City must contain only letters.")
        return city.title()
    
    def clean_place(self):
        place = self.cleaned_data.get("place")
        if not place:
            raise forms.ValidationError("Place is required.")
        place = place.strip()
        if len(place) < 2:
            raise forms.ValidationError("Place name is too short.")
        return place.title()

    def clean_state(self):
        state = self.cleaned_data.get("state")
        if not state:
            raise forms.ValidationError("State is required.")
        state = state.strip()
        if not state.replace(" ", "").isalpha():
            raise forms.ValidationError("State must contain only letters.")
        return state.title()

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get("postal_code")
        if not postal_code:
            raise forms.ValidationError("Postal code is required.")
        postal_code = postal_code.strip()
        if not re.fullmatch(r"\d{6}", postal_code):
            raise forms.ValidationError("Postal code must be 6 digits")
        return postal_code


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["profile_image", "full_name", "phone_number"]

    def clean_full_name(self):
        full_name = self.cleaned_data.get("full_name")
        if not full_name:
            raise forms.ValidationError("Full name is required.")
        if len(full_name) < 3:
            raise forms.ValidationError("Full name must be at least 3 characters.")
        if not full_name.replace(" ", "").isalpha():
            raise forms.ValidationError("Full name must contain only letters.")
        return full_name.strip()

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if not phone_number:
            raise forms.ValidationError("Phone number is required.")
        phone_number = phone_number.strip()
        if not re.fullmatch(r"[6-9]\d{9}", phone_number):
            raise forms.ValidationError("Enter a valid mobile number.")
        if (
            Account.objects.filter(phone_number=phone_number)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError("This phone number is already in use.")
        return phone_number
