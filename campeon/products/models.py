from django.db import models
from django.utils.text import slugify
from django.utils.crypto import get_random_string

# from cloudinary.models import CloudinaryField  # Removed CloudinaryField; using URLField for image URLs
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Sum
from userauths.models import Account
from user.models import Addresses


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    image = models.ImageField(upload_to="category/images")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.pk:
            old = Category.objects.filter(pk=self.pk).first()
            if old and old.name != self.name:
                self.slug = None  # force regenerate
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="products",
    )
    description = models.TextField(blank=True)
    highlights = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_primary_image(self):
        variant = self.variants.filter(is_active=True).first()
        if variant:
            image = variant.images.first()
            if image:
                return image.image.url
        return None

    @property
    def total_stock(self):
        return self.variants.aggregate(total=Sum("stock"))["total"] or 0

    @property
    def active_variants(self):
        return self.variants.filter(is_active=True)

    @property
    def first_active_variant(self):
        return self.variants.filter(is_active=True).first()

    def save(self, *args, **kwargs):
        if self.pk:
            old = Product.objects.filter(pk=self.pk).first()
            if old and old.name != self.name:
                self.slug = None  # force regenerate
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

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

    sku = models.CharField(max_length=100, unique=True, db_index=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.PositiveIntegerField(
        default=0, validators=[MaxValueValidator(100)]
    )
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ["product", "size"]  # Prevent duplicate variants
        ordering = ["id"]
        indexes = [
            models.Index(fields=["product", "is_active"]),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.size}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.sku:
            self.sku = f"CAT{self.product.category.id}-P{self.product.id}-{self.size}"
            super().save(update_fields=["sku"])


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
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", 
        "variant")
        ordering= ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.variant.product.name}"


class Order(models.Model):

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("cod", "Cash On Delivery"),
        ("wallet", "Wallet"),
        ("razorpay", "Razorpay"),
    ]

    ORDER_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("partially_cancel", "Partially Cancelled"),
        ("returned", "Returned"),
        ("partially_return", "Partially Returned"),
    ]

    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="orders")

    # address = models.ForeignKey(
    #     Addresses,
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name="orders",
    # )
    full_name = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=25, blank=True, null=True)

    address_line_1 = models.CharField(max_length=250, null=False, blank=False)
    address_line_2 = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=150, blank=True, null=True)
    place = models.CharField(max_length=150, blank=True, null=True)
    state = models.CharField(max_length=150, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    

    order_id = models.CharField(max_length=20, unique=True, blank=True)

    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    order_status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default="pending"
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if not self.order_id:
            self.order_id = f"ORD-{get_random_string(8).upper()}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_id


class OrderItem(models.Model):

    ITEM_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("partially_cancel", "Partially Cancelled"),
        ("returned", "Returned"),
        ("partially_return", "Partially Returned"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    variant = models.ForeignKey(Variant, on_delete=models.SET_NULL, null=True)

    product_name = models.CharField(max_length=255)

    size = models.CharField(max_length=10)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    quantity = models.PositiveIntegerField(default=1)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=ITEM_STATUS_CHOICES, default="pending"
    )

    cancel_reason = models.TextField(blank=True, null=True)
    cancelled_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

