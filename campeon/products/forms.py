from django import forms
from products.models import Category, Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        # Removed duplicate 'is_active' that appeared twice before
        fields = ["name", "image", "description", "is_active"]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # Added 'is_active' — it's a required field on the model (no default)
        fields = ["name", "category", "description", "highlights", "is_active"]


