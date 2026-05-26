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


# 📄 README — Django E-commerce Project (Wishlist + Cart + Variant System)
# 🧠 Project Overview

# This is a Django-based e-commerce project where:

# Products are variant-based (not product-based purchases)
# Wishlist stores variant items per user
# Cart stores variants with quantity
# Checkout system uses addresses + orders
# UI is custom-built (Tailwind-based ecommerce design)
# 🏗️ Core Architecture
# 📦 Model Relationship (VERY IMPORTANT)
# User
#   ├── Cart (OneToOne)
#   │     └── CartItem → Variant → Product → Category
#   │
#   ├── Wishlist
#   │     └── Variant → Product → Category
#   │
#   ├── Address
#   └── Orders
#         └── OrderItems → Variant
# 🧩 KEY MODEL RULE

# ✔ Customers DO NOT buy Products
# ✔ Customers ONLY buy Variants

# So everywhere:

# product_id ❌ WRONG
# variant_id ✔ CORRECT
# 🛒 CART SYSTEM
# Features:
# Add variant to cart
# Increase quantity if item exists
# Uses Cart + CartItem
# Quantity is integer
# Logic:
# Cart → CartItem (variant + quantity)
# Important:
# Quantity must always be int
# Duplicate cart items are merged
# ❤️ WISHLIST SYSTEM
# Features:
# Stores variant per user
# Prevent duplicates using get_or_create
# Add to cart from wishlist
# Current Issues to fix:
# ❌ Max quantity limit (5) not implemented
# ❌ Add-to-cart duplicate handling needs better UX
# 🧾 CHECKOUT SYSTEM
# Features:
# User selects address
# Orders created from cart
# Address linked to order
# Issues:
# ❌ Address add redirects to profile (should return to checkout)
# ❌ Toast messages show on wrong page (profile instead of checkout)
# ❌ No "Add Address" button when none exists
# ❌ Address delete popup UI broken
# ❌ Deleting address sometimes affects orders
# 🏠 LANDING PAGE
# Issue:
# Product and category list alignment needs fixing
# 🧑‍💼 ADMIN PANEL ISSUES
# Category:
# ❌ Duplicate category error message not user-friendly
# Orders:
# ❌ Admin should NOT change status after user cancels order
# ❌ Changing one item status incorrectly updates full order status
# 🧾 INVOICE SYSTEM
# ❌ Invoice download is currently broken (error occurring)
# 🔁 RETURNS SYSTEM
# ❌ Not implemented yet
# 🧠 WISHLIST → CART RULES

# When adding from wishlist to cart:

# Expected behavior:
# If item NOT in cart → add normally
# If item EXISTS → either:
# Increase quantity OR
# Show toast message
# 🧪 CART HEADER ISSUE
# ❌ Cart count in header is currently dummy data
# Needs dynamic context processor
# ⚠️ IMPORTANT BUSINESS RULES
# Cart works on variants only
# Wishlist works on variants only
# Quantity must be limited (max 5 in wishlist soon)
# Orders are variant-based
# 🎨 UI SYSTEM
# Tailwind CSS based ecommerce UI
# Wishlist page already uses:
# modal for delete
# variant-based pricing
# responsive card layout
# 🚀 PRIORITY FIX LIST
# 🔥 HIGH PRIORITY
# Wishlist max quantity = 5
# Cart header dynamic count
# Wishlist → cart duplicate handling fix
# Checkout address redirect fix
# Toast message placement fix
# ⚡ MEDIUM
# Address delete modal fix
# No-address state UI in checkout
# Admin order cancellation lock
# 🧊 LOW
# Invoice download fix
# Returns system
# Landing page alignment polish
# 🤖 FULL RESTART PROMPT (COPY THIS INTO NEW AI)

# Use this to continue exactly where we left off:

# 📌 START PROMPT

# You are helping me build a Django e-commerce project.

# PROJECT CONTEXT:

# This is a Django-based ecommerce system where:

# Products are sold via VARIANTS, not products
# All purchasing logic must use variant_id
# Models:
# User
# Cart (OneToOne with User)
# CartItem (cart, variant, quantity)
# Wishlist (user, variant)
# Product → Category → Variant
# Orders → OrderItems (variant-based)
# Address model for checkout
# CURRENT IMPLEMENTATION:
# Wishlist stores variant items correctly
# Cart system exists using Cart + CartItem
# Add to wishlist and add to cart logic already implemented
# Quantity is handled in cart with increment logic
# Django messages used for feedback
# Tailwind UI used for frontend
# CURRENT PROBLEMS TO FIX:
# Wishlist:
# Add max quantity limit = 5
# Add-to-cart from wishlist should:
# increase quantity if exists OR
# show proper toast
# Cart:
# Header cart count is dummy → needs dynamic fix
# Checkout:
# Address add redirects incorrectly (should return to checkout)
# Toast messages appear on wrong page (profile instead of checkout)
# If no address exists → show "Add Address"
# Address delete popup UI broken
# Deleting address should NOT affect orders
# Invoice:
# Download invoice throws error
# Returns:
# Not implemented yet
# Admin:
# Prevent status change after user cancels order
# Fix order item status affecting full order incorrectly
# Improve duplicate category error message
# UI:
# Landing page alignment issue for products/categories
# RULES:
# Always use variant-based logic (NOT product-based)
# Keep Django best practices
# Avoid breaking existing wishlist/cart system
# Provide production-ready code

# Now continue helping me fix, improve, and build features step by step.

# ✅ END PROMPT

# If you want next step, I can also:

# ✔ convert this into a GitHub README.md file
# ✔ or design full DB schema diagram
# ✔ or help you fix wishlist max quantity + cart header next (recommended)

# include parital pending and completed status also with the context

# Got it — here is your updated full README + restart prompt with:

# ✅ Completed features
# 🟡 Partial / buggy features
# ❌ Pending features
# Full project context
# Clean restart prompt for another AI
# 📄 README — Django E-commerce Project (Variant-Based System)
# 🧠 Project Overview

# This is a Django e-commerce application where:

# Products are purchased using variants (NOT products)
# Wishlist and Cart both store variant-based items
# Checkout uses address-based order system
# Custom Tailwind UI is used for frontend
# 🏗️ CORE ARCHITECTURE
# 📦 Model Flow
# User
#  ├── Cart (OneToOne)
#  │     └── CartItem → Variant → Product → Category
#  │
#  ├── Wishlist
#  │     └── Variant → Product → Category
#  │
#  ├── Address
#  └── Orders
#        └── OrderItems → Variant
# 🧠 BUSINESS RULE

# ✔ ALL purchases are variant-based
# ✔ Product is only a display layer

# product_id ❌ WRONG
# variant_id ✔ CORRECT
# ✅ COMPLETED FEATURES
# 🛒 Cart System
# ✔ Cart + CartItem implemented
# ✔ Variant-based cart logic
# ✔ Quantity increment working
# ✔ Duplicate item handling using get_or_create
# ✔ Messages system integrated
# ❤️ Wishlist System
# ✔ Variant-based wishlist implemented
# ✔ Duplicate prevention (get_or_create)
# ✔ Add-to-wishlist working
# ✔ UI page built (Tailwind ecommerce style)
# ✔ Remove from wishlist modal working
# 🧾 Core Product System
# ✔ Product → Variant → Category structure working
# ✔ Variant-based pricing system implemented
# ✔ Product detail page supports variant selection
# 🧠 Backend Logic
# ✔ Variant-based architecture correctly implemented
# ✔ Quantity conversion fixed (int() handling)
# ✔ Basic redirect + flow system working
# 🟡 PARTIALLY COMPLETED (WORKING BUT NEED FIXES)
# ❤️ Wishlist → Cart Flow
# ✔ Works basic add-to-cart from wishlist
# ❌ Needs improvement:
# If item exists → better UX (toast vs increment logic unclear)
# No max quantity rule applied
# 🧾 Checkout System
# ✔ Address system exists
# ✔ Order flow partially working
# ❌ Issues:
# Address add redirects to wrong page (profile instead of checkout)
# Toast messages appear on wrong page
# No "Add Address" option when empty
# 🧪 Cart Header
# ✔ Cart system exists
# ❌ Header cart count is still dummy/static
# 🎨 UI System
# ✔ Wishlist UI fully designed
# ✔ Tailwind ecommerce styling used
# ❌ Landing page alignment issues (products/categories)
# 🧾 Wishlist Constraints
# ✔ Variant-based wishlist working
# ❌ Max quantity limit (5) not implemented
# 🧑‍💼 Admin Panel
# ✔ Basic admin working
# ❌ Duplicate category error message not user-friendly
# ❌ Order status logic partially broken
# ❌ PENDING FEATURES / BUGS
# 🔥 Wishlist
# ❌ Implement max quantity = 5 rule
# ❌ Improve wishlist → cart UX behavior
# 🧾 Cart
# ❌ Header cart count dynamic implementation (context processor needed)
# 🧾 Checkout
# ❌ Fix address redirect (must return to checkout)
# ❌ Fix toast message context issue
# ❌ Fix address delete popup alignment
# ❌ Fix address deletion affecting orders
# ❌ Add "Add Address" option when empty
# 📄 Invoice System
# ❌ Download invoice throws error
# 🔁 Returns System
# ❌ Not implemented yet
# 🧑‍💼 Admin Improvements
# ❌ Block order status change after user cancellation
# ❌ Fix single item status affecting full order
# ❌ Improve duplicate category error message
# 🎨 UI Fixes
# ❌ Landing page product/category alignment issue
# ⚠️ IMPORTANT RULES
# Always use variant_id (never product_id for purchases)
# Cart and Wishlist both depend on Variant
# Quantity must always be integer
# Orders are variant-based
# Keep existing system stable while improving
# 🚀 PRIORITY ROADMAP
# 🔥 HIGH PRIORITY
# Wishlist max quantity = 5
# Cart header dynamic count
# Wishlist → cart UX fix
# Checkout address redirect fix
# Toast message placement fix
# ⚡ MEDIUM PRIORITY
# Address delete modal fix
# No-address checkout UI
# Admin order cancellation restriction
# 🧊 LOW PRIORITY
# Invoice fix
# Returns system
# Landing page UI polish
# 🤖 FULL RESTART PROMPT (COPY THIS)
# 📌 START PROMPT

# You are helping me build a Django e-commerce system.

# CORE RULE:
# Products are NOT purchased directly
# Only VARIANTS are purchased (variant_id is always used)
# Product is only for display grouping
# MODEL STRUCTURE:

# User:

# Cart (OneToOne)
# CartItem → Variant → Product → Category
# Wishlist
# Variant → Product → Category
# Address
# Orders
# OrderItems → Variant
# COMPLETED FEATURES:

# ✔ Cart system (variant-based, quantity handling working)
# ✔ Wishlist system (variant-based, duplicate prevention)
# ✔ Product/variant/category structure working
# ✔ Tailwind UI implemented
# ✔ Basic checkout system exists

# PARTIALLY COMPLETED:

# 🟡 Wishlist → cart flow (needs UX improvement)
# 🟡 Checkout system (address flow + toast issues)
# 🟡 Cart header count is static
# 🟡 UI alignment issues in landing page
# 🟡 Wishlist max quantity rule not implemented
# 🟡 Admin order logic partially broken

# PENDING FEATURES:

# ❌ Wishlist max quantity = 5
# ❌ Dynamic cart header count
# ❌ Checkout address redirect fix
# ❌ Toast message context fix
# ❌ Address delete popup fix
# ❌ Invoice download fix
# ❌ Returns system implementation
# ❌ Admin order cancellation + status fixes
# ❌ Landing page UI alignment fix

# RULES:
# Always use variant-based logic
# Do NOT break existing wishlist/cart system
# Keep production-ready Django best practices
# Fix bugs step-by-step with safe changes

# Now continue helping me debug and improve this system step by step.
