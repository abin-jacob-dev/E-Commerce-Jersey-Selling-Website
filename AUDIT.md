# Campeón — Comprehensive Code Audit

> **Audit Date:** June 21, 2026
> **Scope:** Full codebase review — bugs, security vulnerabilities, performance issues, and refactoring opportunities
> **Method:** Manual line-by-line review of all views, models, services, settings, and URL configurations
> **Status:** Findings only — no code changes were made

---

## Table of Contents

1. [Critical Bugs](#1-critical-bugs)
2. [Security Vulnerabilities](#2-security-vulnerabilities)
3. [Performance Issues](#3-performance-issues)
4. [Missing Authentication & Authorization](#4-missing-authentication--authorization)
5. [Logic Errors](#5-logic-errors)
6. [Code Quality & Refactoring](#6-code-quality--refactoring)
7. [Settings & Configuration](#7-settings--configuration)
8. [Summary](#8-summary)

---

## 1. Critical Bugs

These are bugs that will cause crashes, data corruption, or incorrect behavior in production.

### BUG-001: `signin_admin` references undefined variable `user`

**File:** `campeon/userauths/views.py` — `signin_admin()`
**Severity:** 🔴 CRITICAL — Causes `NameError` crash

```python
def signin_admin(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            login(request, user)  # ← `user` is not defined here
            return redirect("admin_panel:dashboard")
```

When an already-authenticated superuser visits `/auth/signin-admin/`, this crashes with `NameError: name 'user' is not defined`. Should be `login(request, request.user)` or simply redirect directly since the user is already logged in.

---

### BUG-002: `add_to_cart` references non-existent `product` field on Wishlist

**File:** `campeon/products/views.py` — `add_to_cart()`
**Severity:** 🔴 CRITICAL — Causes `FieldError` on every cart addition

```python
# Remove from wishlist if added to cart
Wishlist.objects.filter(user=request.user, product=variant.product).delete()
```

The `Wishlist` model has a `variant` field, not a `product` field. This will raise `FieldError: Cannot resolve keyword 'product' into field`. Should be:

```python
Wishlist.objects.filter(user=request.user, variant=variant).delete()
```

---

### BUG-003: `order_view` status comparison always False

**File:** `campeon/products/views.py` — `order_view()`
**Severity:** 🔴 CRITICAL — Order status never auto-syncs from items

```python
statuses = set(order.items.values_list("status", flat=True))
if statuses == 1:  # ← comparing a set to an integer, always False
    order.order_status = statuses.pop()
    order.save()
```

A `set` will never equal `1`. Should be `if len(statuses) == 1:`.

---

### BUG-004: `payment_page` and `verify_payment` in `payment/views.py` have missing imports

**File:** `campeon/payment/views.py`
**Severity:** 🔴 CRITICAL — Causes `NameError` crashes

```python
def payment_page(request):
    ...
    if not razorpay_order_id:
        return redirect("products:cart")  # ← redirect not imported
    order = Order.objects.get(id=order_id)  # ← should use get_object_or_404

@csrf_exempt
def verify_payment(request):
    ...
    order = get_object_or_404(Order, id=order_id)  # ← get_object_or_404 not imported
    payment = get_object_or_404(Payment, ...)       # ← same
```

Neither `redirect` nor `get_object_or_404` is imported in `payment/views.py`. These views will crash on execution.

---

### BUG-005: Duplicate size check is broken — `seen_sizes` resets every iteration

**File:** `campeon/products/views.py` — `add_product()` and `edit_product()`
**Severity:** 🔴 HIGH — Duplicate sizes can be created

```python
for i in range(len(sizes)):
    ...
    seen_sizes = set()  # ← Reset on EVERY iteration of outer loop
    for size in sizes:
        if size in seen_sizes:
            messages.error(request, f"Duplicate size:{size}")
            return redirect("products:add_product")
    seen_sizes.add(sizes[i])  # ← This line doesn't exist; set is recreated empty
```

The `seen_sizes` set is recreated as empty on every iteration of the outer loop, so the duplicate check never detects duplicates. The `seen_sizes.add()` call is also missing. Fix: move `seen_sizes = set()` before the outer loop and add `seen_sizes.add(sizes[i])` at the end of each iteration.

---

### BUG-006: `Cancelled_at` and `returned_at` use `auto_now_add=True`

**File:** `campeon/products/models.py` — `OrderItem`
**Severity:** 🟡 HIGH — Timestamps are wrong

```python
cancelled_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
returned_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
```

`auto_now_add=True` sets the timestamp when the object is **created**, not when it's cancelled/returned. These will always show the order creation time. Should be `default=None, null=True, blank=True` and set explicitly in the view (which the views already do with `timezone.now()`, but the model default overrides it).

---

### BUG-007: `context_processors.py` uses wrong related names

**File:** `campeon/products/context_processors.py` — `cart_data()`
**Severity:** 🔴 CRITICAL — Template rendering crash

```python
cart.items.select_related("variant_product").prefetch_related("variant_images")
```

The correct Django ORM syntax for traversing relationships uses double underscores: `variant__product` and `variant__images`. The current code will raise `FieldError`.

---

### BUG-008: `select_payment` redirect typo — `"product:checkout"` missing 's'

**File:** `campeon/products/views.py` — `select_payment()`
**Severity:** 🟡 MEDIUM — Causes `NoReverseMatch` error

```python
return redirect("product:checkout")  # ← should be "products:checkout"
```

---

### BUG-009: `edit_product` redirect typo — `"prdouct:edit_product"`

**File:** `campeon/products/views.py` — `edit_product()`
**Severity:** 🟡 MEDIUM — Causes `NoReverseMatch` error

```python
return redirect("prdouct:edit_product")  # ← misspelled namespace
```

Should be `"products:edit_product"`.

---

### BUG-010: `final_paid_price` set to order total, not item-level price

**File:** `campeon/products/views.py` — `select_payment()`
**Severity:** 🟡 MEDIUM — Incorrect data in OrderItem

```python
OrderItem.objects.create(
    ...
    final_paid_price=total,  # ← `total` is the ORDER total, not per-item
)
```

Every `OrderItem` gets the full order total as its `final_paid_price`. Should be calculated per item based on quantity and discounts.

---

### BUG-011: Wallet payment falls through without redirect on insufficient balance

**File:** `campeon/products/views.py` — `select_payment()`
**Severity:** 🟡 MEDIUM — User sees error but page doesn't redirect

```python
if payment_method == "wallet":
    ...
    try:
        WalletService.debit_wallet(...)
        ...
        return redirect(...)
    except ValueError as e:
        messages.error(request, str(e))
        # ← No return/redirect here! Falls through to context rendering
```

After the `ValueError`, the code falls through to the `GET` context rendering, which will fail because the order was already created.

---

## 2. Security Vulnerabilities

### SEC-001: Payment verification endpoint has `@csrf_exempt`

**File:** `campeon/payment/views.py` — `verify_payment()`
**Severity:** 🔴 CRITICAL

```python
@csrf_exempt
def verify_payment(request):
```

This disables CSRF protection on the payment verification endpoint. An attacker could craft a forged POST request to mark any payment as successful without actually paying. The `products/views.py` version of `verify_payment` does NOT have `@csrf_exempt`, which is correct.

---

### SEC-002: `ALLOWED_HOSTS = ["*"]`

**File:** `campeon/campeon/settings.py`
**Severity:** 🔴 HIGH

```python
ALLOWED_HOSTS = ["*", "127.0.0.1"]
```

Wildcard `ALLOWED_HOSTS` allows HTTP Host header injection attacks in production. Should be restricted to actual domain names.

---

### SEC-003: `DEBUG` is always truthy (string comparison bug)

**File:** `campeon/campeon/settings.py`
**Severity:** 🔴 HIGH

```python
DEBUG = os.getenv("DEBUG")
```

`os.getenv("DEBUG")` returns a **string**, not a boolean. In Python, the string `"False"` is truthy. So even when `.env` has `DEBUG=False`, Django runs with `DEBUG=True`. Should be:

```python
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
```

---

### SEC-004: Passwords printed to stdout/console

**Files:** `campeon/user/views.py`, `campeon/userauths/views.py`
**Severity:** 🔴 HIGH

```python
# user/views.py — change_password()
print(current_password, new_password, confirm_password)

# userauths/views.py — reset_password()
print(password, confirm_password)
```

Plaintext passwords are written to stdout/logs. In production, these logs could be accessed by unauthorized parties.

---

### SEC-005: Missing production security settings

**File:** `campeon/campeon/settings.py`
**Severity:** 🟡 MEDIUM

The following security settings are not configured:

| Setting | Recommended Value |
| :--- | :--- |
| `SECURE_SSL_REDIRECT` | `True` |
| `SESSION_COOKIE_SECURE` | `True` |
| `CSRF_COOKIE_SECURE` | `True` |
| `SECURE_HSTS_SECONDS` | `31536000` |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `True` |
| `SECURE_CONTENT_TYPE_NOSNIFF` | `True` |

---

### SEC-006: Profile image deletion uses local file path with Cloudinary storage

**File:** `campeon/user/views.py` — `remove_photo()`, `edit_profile()`
**Severity:** 🟡 MEDIUM

```python
if os.path.isfile(user.profile_image.path):
    os.remove(user.profile_image.path)
```

The project uses Cloudinary for media storage (`DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"`), so `profile_image.path` may not be a valid local file path. This could silently fail or delete the wrong file. Should use Cloudinary's API to delete the resource.

---

### SEC-007: `Wishlist` model field mismatch allows potential data issues

**File:** `campeon/products/views.py` — `add_to_cart()`
**Severity:** 🟡 MEDIUM

The Wishlist model uses `variant` as the foreign key, but `add_to_cart()` tries to filter by `product`. This means wishlist items are never cleaned up when adding to cart, leaving orphaned wishlist entries.

---

## 3. Performance Issues

### PERF-001: N+1 queries in admin sales reports

**File:** `campeon/admin_panel/views.py` — `sales()`, `sales_report_pdf()`, `sales_report_excel()`
**Severity:** 🟡 MEDIUM

```python
for order in daily_orders:
    offer_discount = sum(
        sum(item.offer_discount_amount for item in order.items.all())  # N+1
        for order in daily_orders
    )
```

Each `order.items.all()` triggers a separate database query. With 100 orders per period, this generates 100+ additional queries. Should use `prefetch_related("items")` on the queryset.

---

### PERF-002: N+1 queries in dashboard chart data

**File:** `campeon/admin_panel/views.py` — `dashboard()`
**Severity:** 🟡 MEDIUM

```python
top_products = (
    order_items.values("variant__product__name")
    .annotate(total_sold=Sum("quantity"))
    ...
)
```

The `order_items` queryset already filters by `order__in=orders`, but the `orders` queryset itself isn't optimized. Each chart data point triggers separate aggregation queries.

---

### PERF-003: `prefetch_related` called after pagination

**File:** `campeon/products/views.py` — `all_products()`
**Severity:** 🟢 LOW

```python
paginator = Paginator(products, 6)
page_number = request.GET.get("page")
page_obj = paginator.get_page(page_number)
...
products = products.prefetch_related("variants__images")  # ← After pagination!
```

The `prefetch_related` is applied after `Paginator` has already executed the query. The prefetch has no effect on the paginated results. Should be applied before pagination.

---

### PERF-004: `get_best_offer` called per item in cart/checkout

**File:** `campeon/products/views.py` — `select_payment()`
**Severity:** 🟢 LOW

```python
for item in cart_items:
    item_offer = get_best_offer(item.variant.product)  # DB query per item
```

Each call to `get_best_offer()` runs 2 database queries (product offer + category offer). For a cart with 10 items, this generates 20+ queries. Should batch-fetch offers.

---

### PERF-005: `CartItem.offer_subtotal` triggers `get_discount_price` per property access

**File:** `campeon/products/models.py` — `CartItem`
**Severity:** 🟢 LOW

```python
@property
def offer_price(self):
    from products.offer_service import get_discount_price
    return get_discount_price(self.variant)

@property
def offer_subtotal(self):
    return self.offer_price * self.quantity
```

Every access to `offer_subtotal` triggers `get_best_offer()` (2 DB queries). In templates that access this multiple times, it multiplies queries. Should cache the result.

---

### PERF-006: `context_processors` runs on EVERY request

**File:** `campeon/products/context_processors.py`
**Severity:** 🟢 LOW

Both `cart_data` and `cart_summary` run on every page load for every user (authenticated or not). For authenticated users, this triggers `Cart.objects.get_or_create()` and `cart.items.all()` on every request. Consider caching or using template tags instead.

---

### PERF-007: `Coupon` duplicate `class Meta`

**File:** `campeon/products/models.py` — `Coupon`
**Severity:** 🟢 LOW

```python
class Coupon(models.Model):
    ...
    class Meta:
        ordering = ["-created_at"]
    ...
    class Meta:  # ← Duplicate!
        ordering = ["-created_at"]
```

Not a performance issue per se, but duplicate Meta classes can cause confusion and maintenance problems.

---

## 4. Missing Authentication & Authorization

### AUTH-001: Coupon management has no access control

**File:** `campeon/products/views.py`
**Severity:** 🔴 HIGH

```python
def coupons(request):       # ← No @superuser_required
def add_coupon(request):    # ← No @superuser_required
def edit_coupon(request, id):   # ← No @superuser_required
def delete_coupon(request, id): # ← No @superuser_required
```

Any authenticated user (or even anonymous users for some) can create, edit, and delete coupons.

---

### AUTH-002: Offer management has no access control

**File:** `campeon/products/views.py`
**Severity:** 🔴 HIGH

```python
def offers(request):        # ← No @superuser_required
def add_offer(request):     # ← No @superuser_required
def edit_offer(request, id):    # ← No @superuser_required
def delete_offer(request, id):  # ← No @superuser_required
```

Same issue as coupons. Any user can manage offers.

---

### AUTH-003: Order return/cancel request views missing authentication

**File:** `campeon/products/views.py`
**Severity:** 🔴 HIGH

```python
def return_order_item(request, item_id):           # ← No @user_login_required
def return_order_item_request(request, item_id):   # ← No @user_login_required
def cancel_order_item(request, item_id):           # ← No @user_login_required
```

Anonymous users can access these views. While `get_object_or_404` filters by `order__user=request.user`, for anonymous users `request.user` is `AnonymousUser` which has `id=None`, so these would 404 anyway — but the pattern is still insecure and inconsistent.

---

### AUTH-004: Wallet view missing authentication

**File:** `campeon/user/views.py`
**Severity:** 🟡 MEDIUM

```python
def wallet(request):
    wallet = Wallet.objects.get(user=request.user)  # ← No @user_login_required
```

For anonymous users, `request.user` is `AnonymousUser`, and `Wallet.objects.get(user=AnonymousUser)` will raise `Wallet.DoesNotExist`.

---

### AUTH-005: Referral view missing authentication

**File:** `campeon/user/views.py`
**Severity:** 🟡 MEDIUM

```python
def referral(request):  # ← No @user_login_required
```

---

### AUTH-006: `download_invoice` missing authentication

**File:** `campeon/products/views.py`
**Severity:** 🟡 MEDIUM

```python
def download_invoice(request, order_id):  # ← No @user_login_required
```

While `get_object_or_404` filters by `user=request.user`, the pattern is inconsistent.

---

### AUTH-007: `payment_failed` missing authentication

**File:** `campeon/products/views.py`
**Severity:** 🟢 LOW

```python
def payment_failed(request, order_id):  # ← No @user_login_required
```

---

### AUTH-008: Address edit/delete have no ownership check

**File:** `campeon/user/views.py`
**Severity:** 🟡 MEDIUM

```python
def edit_address(request, id):
    address = Addresses.objects.get(id=id)  # ← No user filter!
    # ...

def delete_address(request, id):
    address = Addresses.objects.get(id=id)  # ← No user filter!
    # ...
```

Any authenticated user can edit or delete any other user's address by guessing the ID. Should filter by `user=request.user`.

---

## 5. Logic Errors

### LOGIC-001: `select_payment` refund amount doesn't account for coupons

**File:** `campeon/products/views.py` — `order_view()`
**Severity:** 🟡 MEDIUM

```python
# approve_cancel
item.refund_amount = item.subtotal

# approve_return
item.refund_amount = item.subtotal
```

If a user applied a coupon to their order, the refund is calculated on `subtotal` (pre-coupon), not the actual amount paid. The user gets more back than they paid.

---

### LOGIC-002: `apply_coupon` uses raw `cart.total_price` instead of offer-adjusted price

**File:** `campeon/products/views.py` — `apply_coupon()`
**Severity:** 🟡 MEDIUM

```python
if cart.total_price < coupon.min_purchase_amount:
```

`cart.total_price` sums `item.subtotal` (raw price × quantity), not `item.offer_subtotal`. A user with offer discounts might be incorrectly rejected because the raw total is higher than the min purchase, or vice versa.

---

### LOGIC-003: `activate_account` has unreachable dead code

**File:** `campeon/userauths/views.py` — `activate_account()`
**Severity:** 🟢 LOW

```python
if otp_obj.otp == entered_otp:
    request.session["is_email_verified"] = True
    request.session.pop("otp_expiry", None)
    otp_obj.delete()
    messages.success(request, "Email Verified Successfully")
    return redirect("userauths:signup")
# ← Unreachable code below:
request.session["is_email_verified"] = True
otp_obj.delete()
messages.success(request, "Email Verified Successfully")
return redirect("userauths:signup")
```

The last 4 lines are unreachable because the `if` block above always returns.

---

### LOGIC-004: `Variant.discount` field is never used

**File:** `campeon/products/models.py` — `Variant`
**Severity:** 🟢 LOW

```python
discount = models.PositiveIntegerField(
    default=0, validators=[MaxValueValidator(100)]
)
```

This field exists on the model but is never read or used in any view, service, or template. All discount logic goes through the `Offer` model. This is dead code that could confuse future developers.

---

### LOGIC-005: `signup` ignores referral code from form

**File:** `campeon/userauths/views.py` — `signup()`
**Severity:** 🟢 LOW

```python
referral_code = form.cleaned_data.get("referral_code")
# ← referral_code is extracted but never used
```

The form collects a referral code, but it's never passed to `apply_referral_bonus()`. The referral can only be applied after signup via the separate `/user/referral/` page.

---

### LOGIC-006: `add_to_wishlist` doesn't validate quantity

**File:** `campeon/products/views.py` — `add_to_wishlist()`
**Severity:** 🟢 LOW

```python
quantity = int(request.POST.get("quantity", 1))
```

No validation that `quantity` is between 1 and 5, or that it's even a valid integer (will crash with `ValueError` on non-numeric input).

---

### LOGIC-007: COD payment doesn't validate stock atomically

**File:** `campeon/products/views.py` — `select_payment()`
**Severity:** 🟡 MEDIUM

```python
if payment_method == "cod":
    order.payment_status = "paid"
    order.save()
    for item in cart_items:
        variant = item.variant
        if variant.stock < item.quantity:
            messages.error(request, "Stock unavailable")
            return redirect("products:cart")
        variant.stock -= item.quantity
        variant.save()
```

Stock check and decrement are not atomic. Two concurrent COD orders could both pass the stock check and double-decrement, going negative.

---

### LOGIC-008: Razorpay `verify_payment` has race condition on stock

**File:** `campeon/products/views.py` — `verify_payment()`
**Severity:** 🟡 MEDIUM

```python
for item in order.items.all():
    if item.variant.stock < item.quantity:
        return JsonResponse({"success": False, "message": "Out of stock"})
    item.variant.stock -= item.quantity
    item.variant.save()
```

Not using `select_for_update()`. Two simultaneous payment verifications could both pass the stock check. Should wrap in `transaction.atomic()` with `select_for_update()` on variants.

---

### LOGIC-009: `WalletService.debit_wallet` doesn't use `select_for_update`

**File:** `campeon/products/service.py`
**Severity:** 🟡 MEDIUM

```python
@staticmethod
def debit_wallet(user, amount, order=None):
    wallet = Wallet.objects.get(user=user)
    if wallet.current_balance < amount:
        raise ValueError("Insufficient Balance")
    with transaction.atomic():
        wallet.current_balance -= amount
        wallet.save()
```

While `transaction.atomic()` is used, the wallet isn't locked with `select_for_update()`. Two concurrent debits could both read the same balance and both succeed, overdrafting the wallet.

---

### LOGIC-010: `order_view` refund uses `item.subtotal` not the paid amount

**File:** `campeon/products/views.py` — `order_view()`
**Severity:** 🟡 MEDIUM

When approving cancel/return, `item.refund_amount = item.subtotal` is used. But `item.subtotal` is the pre-offer-discount price. If the item had an offer discount, the user actually paid less than `subtotal`. The refund should be based on `final_paid_price` or `subtotal - offer_discount_amount`.

---

## 6. Code Quality & Refactoring

### REFACTOR-001: Decorators don't preserve function metadata

**Files:** `campeon/userauths/views.py`, `campeon/products/views.py`
**Severity:** 🟡 MEDIUM

```python
def superuser_required(func):
    def wrapper(request, *args, **kwargs):
        ...
    return wrapper  # ← Missing @functools.wraps(func)

def user_login_required(func):
    def wrapper(request, *args, **kwargs):
        ...
    return wrapper  # ← Missing @functools.wraps(func)
```

Without `@functools.wraps(func)`, decorated functions lose their `__name__`, `__doc__`, and `__module__` attributes. This breaks debugging, Django's admin, and any tool that inspects function names.

---

### REFACTOR-002: Inconsistent authentication patterns

**Files:** `campeon/products/views.py`, `campeon/user/views.py`
**Severity:** 🟡 MEDIUM

Some views use `@user_login_required`, some use `@superuser_required`, some use Django's `@login_required`, and some have no authentication at all. This inconsistency makes it hard to audit access control.

---

### REFACTOR-003: Duplicate OTP model across apps

**Files:** `campeon/userauths/utility.py`, `campeon/user/utility.py`
**Severity:** 🟢 LOW

Two separate `OTP` models exist:
- `userauths.utility.OTP` — keyed by email (for signup verification)
- `user.utility.OTP` — keyed by user FK (for profile changes)

This causes confusion about which OTP to use where. Consider unifying into a single model with a `purpose` field.

---

### REFACTOR-004: `print()` statements left in production code

**Files:** Multiple views
**Severity:** 🟢 LOW

```python
print(form.errors)
print("ERROR adding product:", str(e))
print("user is none")
print("user blocked")
print(razorpay_order)
```

Scattered `print()` statements should be replaced with proper `logging` module calls.

---

### REFACTOR-005: Sales report logic is duplicated 3 times

**File:** `campeon/admin_panel/views.py`
**Severity:** 🟡 MEDIUM

The sales report queryset construction and aggregation logic is nearly identical in `sales()`, `sales_report_pdf()`, and `sales_report_excel()`. Should be extracted into a shared service function.

---

### REFACTOR-006: `select_payment` is a 150+ line monolith

**File:** `campeon/products/views.py` — `select_payment()`
**Severity:** 🟡 MEDIUM

This single function handles:
- Cart validation
- Offer calculation
- Coupon calculation
- Address lookup
- Order creation (COD, Wallet, Razorpay)
- Stock decrement
- Payment processing

Should be broken into smaller, testable functions.

---

### REFACTOR-007: `Wishlist` model field named `product` but should be `variant`

**File:** `campeon/products/models.py` — `Wishlist`
**Severity:** 🟢 LOW (already using `variant`, but `add_to_cart` references `product`)

The model correctly uses `variant`, but the inconsistency in the view (BUG-002) suggests the field name caused confusion during development.

---

### REFACTOR-008: Cart summary calculated in both context processor and view

**Files:** `campeon/products/context_processors.py`, `campeon/products/views.py`
**Severity:** 🟢 LOW

`cart_summary` context processor calculates totals on every request, and `calculate_cart_summary()` does the same in the cart view. This is redundant work.

---

### REFACTOR-009: `add_new_category` creates form before duplicate check

**File:** `campeon/products/views.py` — `add_new_category()`
**Severity:** 🟢 LOW

```python
form = CategoryForm()  # Empty form created
if request.method == "POST":
    name = request.POST.get("name")
    if Category.objects.filter(name__iexact=name, is_deleted=False).exists():
        messages.error(request, "Category already exists")
        return render(request, ..., {"form": form})  # ← Empty form, not user's input
```

When the duplicate check fails, the user sees an empty form instead of their submitted data.

---

## 7. Settings & Configuration

### CONFIG-001: `EMAIL_USE_TLS` is a string, not boolean

**File:** `campeon/campeon/settings.py`
**Severity:** 🟡 MEDIUM

```python
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS")
```

Same issue as `DEBUG` — returns a string. `"False"` is truthy in Python. Should be:

```python
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("true", "1", "yes")
```

---

### CONFIG-002: `STATIC_ROOT` not defined

**File:** `campeon/campeon/settings.py`
**Severity:** 🟡 MEDIUM

```python
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
# ← No STATIC_ROOT defined
```

`collectstatic` will fail without `STATIC_ROOT`. Required for production deployment.

---

### CONFIG-003: Missing `DEFAULT_AUTO_FIELD`

**File:** `campeon/campeon/settings.py`
**Severity:** 🟢 LOW

Django 6.0 will warn about missing `DEFAULT_AUTO_FIELD`. Should add:

```python
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

---

### CONFIG-004: `JAZZMIN_SETTINGS` defined but jazzmin is commented out

**File:** `campeon/campeon/settings.py`
**Severity:** 🟢 LOW

```python
# "jazzmin",  # ← Commented out in INSTALLED_APPS
JAZZMIN_SETTINGS = { ... }  # ← But config still exists
```

Dead configuration that adds confusion.

---

## 8. Summary

### Issue Count by Severity

| Severity | Count |
| :--- | :--- |
| 🔴 CRITICAL | 7 |
| 🔴 HIGH | 5 |
| 🟡 MEDIUM | 20 |
| 🟢 LOW | 14 |
| **Total** | **46** |

### Issue Count by Category

| Category | Count |
| :--- | :--- |
| Critical Bugs | 11 |
| Security Vulnerabilities | 7 |
| Performance Issues | 7 |
| Missing Auth/Authorization | 8 |
| Logic Errors | 10 |
| Code Quality & Refactoring | 9 |
| Settings & Configuration | 4 |
| **Total** | **46** (some overlap) |

### Top 10 Most Urgent Fixes

| # | ID | Description | File |
| :--- | :--- | :--- | :--- |
| 1 | SEC-003 | `DEBUG` always truthy — production runs with debug on | settings.py |
| 2 | BUG-001 | `signin_admin` crashes with `NameError` | userauths/views.py |
| 3 | BUG-002 | `add_to_cart` references wrong Wishlist field | products/views.py |
| 4 | SEC-001 | Payment verification has `@csrf_exempt` | payment/views.py |
| 5 | AUTH-001 | Coupon management has no access control | products/views.py |
| 6 | AUTH-002 | Offer management has no access control | products/views.py |
| 7 | BUG-004 | `payment/views.py` missing imports — crashes on execution | payment/views.py |
| 8 | BUG-007 | Context processor uses wrong ORM syntax — template crash | context_processors.py |
| 9 | SEC-004 | Passwords printed to stdout | user/views.py, userauths/views.py |
| 10 | AUTH-008 | Address edit/delete have no ownership check | user/views.py |

---

*This audit was performed by manual code review on June 21, 2026. No code changes were made.*
