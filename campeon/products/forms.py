from django import forms
from products.models import Category, Product, Coupon, Review, Offer, Variant
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
        if not re.fullmatch(r"^[A-Za-z0-9]+(?:[ '-][A-Za-z0-9]+)*$", name):
            raise forms.ValidationError(
                "Name can only contain letters, numbers, spaces, hyphens, and apostrophes."
            )
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
                self.add_error(
                    "name",
                    "Name can only contain letters, numbers, spaces, hyphens, and apostrophes.",
                )

            if (
                Offer.objects.filter(name__iexact=name)
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                self.add_error("name", "Offer already exists.")

            # Target validation
            if not target_type:
                self.add_error("target_type", "Please select a target type.")

            elif target_type == "product":

                if not product:
                    self.add_error("product", "Please select a product.")

                if category:
                    self.add_error(
                        "category",
                        "Category should not be selected for a product offer.",
                    )

            elif target_type == "category":

                if not category:
                    self.add_error("category", "Please select a category.")

                if product:
                    self.add_error(
                        "product",
                        "Product should not be selected for a category offer.",
                    )

            # Date validation
            if start_date and end_date:
                if end_date <= start_date:
                    self.add_error(
                        "end_date",
                        "The end date should be greater than the start date.",
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

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not name:
            raise forms.ValidationError("Product name is required.")
        name = " ".join(name.strip().split())
        if not re.fullmatch(r"^[\w\s\-.,&+()/'%:]+$", name):
            raise forms.ValidationError("Invalid product name.")
        if (
            Product.objects.filter(name__iexact=name)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError("Product already exists.")
        return name

    def clean_category(self):
        category = self.cleaned_data.get("category")

        if not category:
            raise forms.ValidationError("Please select a category.")

        return category

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

    def clean_highlights(self):
        highlights = self.cleaned_data.get("highlights")

        if not highlights:
            raise forms.ValidationError("Highlights is required.")

        highlights = highlights.strip()

        if len(highlights) < 10:
            raise forms.ValidationError(
                "Highlights must be at least 10 characters long."
            )

        if len(highlights) > 500:
            raise forms.ValidationError("Highlights cannot exceed 500 characters.")

        return highlights


class VariantForm(forms.ModelForm):
    class Meta:
        model = Variant
        fields = [
            "size",
            "price",
            "stock",
            "is_active",
        ]

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price < 0:
            raise forms.ValidationError("Price cannot be negative.")

        return price

    def clean_stock(self):
        stock = self.cleaned_data.get("stock")
        if stock < 0:
            raise forms.ValidationError("Stock cannot be negative.")
        return stock


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
        min_purchase_amount = self.cleaned_data.get("min_purchase_amount")

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
            if discount_type == "percentage" and discount_value >= 100:
                self.add_error(
                    "discount_value",
                    "Percentage cannot be greater than or equal to 100.",
                )
            if discount_type == "fixed" and min_purchase_amount <= discount_value:
                self.add_error(
                    "discount_value",
                    "Fixed discount value must be less than the minimum purchase amount.",
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
