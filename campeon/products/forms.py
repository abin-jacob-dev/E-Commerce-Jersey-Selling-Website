from django import forms
from products.models import Category, Product, Coupon, Review, Offer
import re


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        # Removed duplicate 'is_active' that appeared twice before
        fields = ["name", "image", "description", "is_active"]

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not name:
            raise forms.ValidationError("Name is required.")
        name = name.strip()
        if not re.fullmatch(r"^[A-Za-z]+(?: [A-Za-z]+)*$", name):
            raise forms.ValidationError("Name can only contain letters.")
        if (
            Category.objects.filter(name__iexact=name)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError("Category already exists.")
        return name

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            raise forms.ValidationError("Image is required.")
        return image

    def clean_description(self):
        description = self.cleaned_data.get("description")

        if not description:
            raise forms.ValidationError("Description is required.")

        description = description.strip()

        if len(description) < 10:
            raise forms.ValidationError(
                "Description must be at least 10 characters long."
            )

        if len(description) > 500:
            raise forms.ValidationError("Description cannot exceed 500 characters.")

        return description


class OfferForm(forms.ModelForm):

    class Meta:
        model = Offer
        fields = [
            "name",
            "discount_type",
            "discount_value",
            "start_date",
            "end_date",
            "is_active",
            "product",
            "category",
            "target_type",
        ]
        

        widgets = {
            "start_date": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "end_date": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
        }
        

    def clean(self):
        cleaned_data = super().clean()

        name = cleaned_data.get("name")
        product = cleaned_data.get("product")
        category = cleaned_data.get("category")
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        discount_value = cleaned_data.get("discount_value")
        discount_type = cleaned_data.get("discount_type")
        target_type = cleaned_data.get("target_type")

        # Name validation
        if not name:
            self.add_error("name", "Name is required.")
        else:
            name = name.strip().upper()
            cleaned_data["name"] = name

            if not re.fullmatch(r"^[A-Za-z0-9]+(?: [A-Za-z0-9]+)*$", name):
                self.add_error("name", "Name can only contain letters and numbers.")

            if (
                Offer.objects.filter(name__iexact=name)
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                self.add_error("name", "Offer already exists.")

           # Target validation
            if not target_type:
                self.add_error(
                    "target_type",
                    "Please select a target type."
                )

            elif target_type == "product":

                if not product:
                    self.add_error(
                        "product",
                        "Please select a product."
                    )

                if category:
                    self.add_error(
                        "category",
                        "Category should not be selected for a product offer."
                    )


            elif target_type == "category":

                if not category:
                    self.add_error(
                        "category",
                        "Please select a category."
                    )

                if product:
                    self.add_error(
                        "product",
                        "Product should not be selected for a category offer."
                    )


            # Date validation
            if start_date and end_date:
                if end_date <= start_date:
                    self.add_error(
                        "end_date",
                        "The end date should be greater than the start date."
                    )

        # Discount validation
        if discount_value is not None:
            if discount_value <= 0:
                self.add_error("discount_value", "The value should be greater than 0.")

            if discount_type == "percentage" and discount_value >= 100:
                self.add_error(
                    "discount_value",
                    "Percentage cannot be greater than or equal to 100.",
                )

        return cleaned_data


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
        code = self.cleaned_data.get("code")

        if not code:
            self.add_error("code", "Code is required.")
        else:
            code = code.strip().upper()
            cleaned_data["code"] = code

            if not re.fullmatch(r"^[A-Za-z0-9]+(?: [A-Za-z0-9]+)*$", code):
                self.add_error("code", "Code can only contain letters and numbers.")

            if (
                Coupon.objects.filter(code__iexact=code)
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                self.add_error("code", "Coupon already exists.")
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
