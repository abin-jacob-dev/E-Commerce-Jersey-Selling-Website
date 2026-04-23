from django import forms
from .models import Addresses


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
      