from django.db import models

# from cloudinary.models import CloudinaryField  # Removed CloudinaryField; using URLField for image URLs
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Sum
from userauths.models import Account


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)
    image = models.ImageField(upload_to="category/images", blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(
        choices=[(True, "Active"), (False, "Inactive")], default=True
    )
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


def get_primary_image(self):
    for variant in self.variants.all():
        image = variant.images.first()
        if image:
            return image.image.url
    return ""


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="products",
    )
    description = models.TextField(blank=True)
    highlights = models.TextField(blank=True)
    is_active = models.BooleanField(choices=[(True, "Active"), (False, "Inactive")])
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_primary_image(self):
        variant = self.variants.first()
        if variant:
            image = variant.images.first()
            if image:
                return image.image.url
        return None

    def total_stock(self):
        return self.variants.aggregate(total=Sum("stock"))["total"] or 0

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=7, blank=True)  # for HEX code storing #000000

    def __str__(self):
        return self.name


class Variant(models.Model):
    SIZE_CHOICES = [
        ("S", "Small"),
        ("M", "Medium"),
        ("L", "Large"),
        ("XL", "Extra Large"),
        ("XXL", "Double Extra Large"),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    size = models.CharField(max_length=5, choices=SIZE_CHOICES)
    color = models.ForeignKey(
        Color,
        on_delete=models.CASCADE,
        related_name="variants",
        null=True,
        blank=True,  # must be boolean True, not the string "True"
    )
    sku = models.CharField(max_length=100, unique=True, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.PositiveIntegerField(
        default=0, validators=[MaxValueValidator(100)]
    )
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ["product", "size", "color"]  # Prevent duplicate variants
        ordering = ["id"]
        indexes = [
            models.Index(fields=["product", "is_active"]),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.size} - {self.color or 'No Color'}"


class VariantImage(models.Model):
    variant = models.ForeignKey(
        Variant, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="variants/images")

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Image for {self.variant.sku}"


class Cart(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("cart", "variant")

    def __str__(self):
        return f"{self.quantity} x {self.variant.product.name}"

    @property
    def subtotal(self):
        return self.variant.price * self.quantity


class Wishlist(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
