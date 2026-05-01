from django import forms
from products.models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','image','description','is_active']
