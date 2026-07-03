from django import forms
from products.models import Category, Product, Coupon, Review


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


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = [
            "code",
            "is_active",
            "discount_type",
            "discount_value",
            "min_purchase_amount",
            "start_date",
            "end_date",
        ]

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        discount_value = cleaned_data.get("discount_value")
        discount_type = cleaned_data.get("discount_type")

        if start_date and end_date:
            if start_date >= end_date:
                self.add_error("end_date", "End date must be after start date")
        if discount_value is not None:
            if discount_value <= 0:
                self.add_error(
                    "discount_value", "Discount Value must be greater than zero"
                )
            if discount_type == "percentage" and discount_value > 100:
                self.add_error(
                    "discount_value", "Percentage discount cannot be greater than 100%"
                )
        return cleaned_data


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]

    def clean_comment(self):
        comment = self.cleaned_data.get("comment")
        if not comment:
            raise forms.ValidationError("Comment is required")

        if len(comment.strip()) < 3:
            raise forms.ValidationError("Need more Characters")
        return comment
