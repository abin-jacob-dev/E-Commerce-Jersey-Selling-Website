from django.db import models
from django.utils.text import slugify
from django.utils.crypto import get_random_string

from cloudinary.models import CloudinaryField

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Sum
from userauths.models import Account
from user.models import Addresses
from django.utils import timezone
from django.core.exceptions import ValidationError

# Create your models here.


class Coupon(models.Model):

    DISCOUNT_TYPE_CHOICES = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
    ]

    code = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    discount_type = models.CharField(
        max_length=20, choices=DISCOUNT_TYPE_CHOICES, default="percentage"
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_purchase_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.code

    @property
    def is_expired(self):
        if self.end_date:
            return timezone.now().date() > self.end_date
        return False

    @property
    def is_valid(self):
        now = timezone.now().date()
        if not self.is_active:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True


class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    image = CloudinaryField(
        "category_image", folder="category_images"
    )
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
    def cheapest_variant(self):
        return (
            self.variants.filter(is_active=True, stock__gt=0).order_by("price").first()
        )

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


class Offer(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
    ]
    TARGET_TYPE_CHOICES = [
        ("product", "Product"),
        ("category", "Category"),
    ]

    name = models.CharField(max_length=100)

    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    is_active = models.BooleanField(default=True)
    target_type = models.CharField(max_length=20, choices=TARGET_TYPE_CHOICES)
    product = models.ForeignKey(
        Product, null=True, blank=True, on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.start_date:
            return False
        if now > self.end_date:
            return False

        return True


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

    @property
    def offer_price(self):
        from products.offer_service import get_discount_price

        return get_discount_price(self)

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
    image = CloudinaryField("variant_image", folder="variant_images")

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

    @property
    def offer_price(self):
        from products.offer_service import get_discount_price

        return get_discount_price(self.variant)

    @property
    def offer_subtotal(self):
        return self.offer_price * self.quantity


class Wishlist(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="wishlist")
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "variant")
        ordering = ["-created_at"]

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
        ("partially_cancelled", "Partially Cancelled"),
        ("cancelled", "Cancelled"),
        ("partially_returned", "Partially Returned"),
        ("returned", "Returned"),
    ]

    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="orders")
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)

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
    total_refund_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )

    coupon_name = models.CharField(max_length=255, null=True)

    coupon_discount_type = models.CharField(max_length=20, null=True)  # percent/fixed
    coupon_discount_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True
    )

    def save(self, *args, **kwargs):

        if not self.order_id:
            self.order_id = f"ORD-{get_random_string(8).upper()}"

        super().save(*args, **kwargs)

    @property
    def get_subtotal(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def get_coupon_discount(self):
        return self.coupon_discount_value or 0

    @property
    def get_offer_discount(self):
        return sum(item.offer_discount_amount for item in self.items.all())

    @property
    def get_total_after_discount(self):
        return (
            self.subtotal
            - (self.get_coupon_discount + self.get_offer_discount)
            + self.shipping
        )

    def __str__(self):
        return self.order_id


class OrderItem(models.Model):

    ITEM_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("partially_cancelled", "Partially Cancelled"),
        ("returned", "Returned"),
        ("partially_returned", "Partially Returned"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)

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
    returned_reason = models.TextField(blank=True, null=True)
    returned_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    offer_name = models.CharField(max_length=255, null=True)

    offer_discount_type = models.CharField(max_length=20, null=True)  # percent/fixed
    offer_discount_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True
    )
    offer_discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    final_paid_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class Wallet(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - ₹{self.current_balance}"


class WalletTransaction(models.Model):
    SOURCE_CHOICES = [
        ("order_payment", "ORDER PAYMENT"),
        ("refund", "REFUND"),
        ("referral", "REFERRAL"),
    ]
    TRANSACTION_TYPE = (
        ("credit", "CREDIT"),
        ("debit", "DEBIT"),
    )
    order = models.ForeignKey(
        "Order", on_delete=models.SET_NULL, null=True, blank=True, related_name="order"
    )
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="wallet_transactions"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    source = models.CharField(choices=SOURCE_CHOICES, max_length=50)
    transaction_type = models.CharField(choices=TRANSACTION_TYPE, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    # RATING_CHOICES = [
    #     ("5", "Excellent"),
    #     ("4", "Very Good"),
    #     ("3", "Average"),
    #     ("2", "Poor"),
    #     ("1", "Bad"),
    # ]
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("product", "user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"
