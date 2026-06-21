# Campeón — Review & Interview Preparation Questions

> **Purpose:** Prepare for code review / viva voce / live coding sessions
> **Scope:** Variants, cart flow, cancellation, wallet, referrals, and edge-case handling
> **Tip:** For each question, I've included the answer pattern and which file to reference

---

## 1. Variants System

### Q1.1: How does the variant system work? What is the relationship between Product, Variant, and VariantImage?

**Answer Pattern:**
- A `Product` (e.g., "Manchester Jersey") has multiple `Variant` objects, one per size (S/M/L/XL/XXL)
- Each `Variant` has its own `price`, `stock`, `sku`, and `is_active` flag
- Each `Variant` can have multiple `VariantImage` objects
- The relationship is: `Product → 1:N → Variant → 1:N → VariantImage`
- `unique_together = ["product", "size"]` prevents duplicate sizes per product

**Files:** `products/models.py` — `Product`, `Variant`, `VariantImage`

---

### Q1.2: How is the SKU generated for a variant?

**Answer Pattern:**
- SKUs are auto-generated in `Variant.save()` using the format: `CAT{category_id}-P{product_id}-{size}`
- Example: `CAT1-P5-XL` means Category 1, Product 5, size XL
- Only generated for new variants (`is_new = self.pk is None`)
- The `sku` field has `unique=True` and `db_index=True` for fast lookups

**Files:** `products/models.py` — `Variant.save()`

---

### Q1.3: What happens when a user selects a different size on the product detail page?

**Answer Pattern:**
- The `product_detail` view pre-computes `variant_data` — a list of dicts with `id`, `size`, `price`, `discount_price`, `saved`, and `stock` for each active variant
- The frontend uses JavaScript to swap the displayed price/stock/image when a size is clicked
- The `add-to-cart` form sends the selected `variant_id` to the backend
- No separate API call is needed for size selection — it's all client-side

**Files:** `products/views.py` — `product_detail()`, templates/products/product_detail.html

---

### Q1.4: How does the system handle out-of-stock variants?

**Answer Pattern:**
- In `product_detail()`, only variants with `stock > 0` and `is_active=True` are shown
- If no active variants have stock, the user is redirected with a warning
- In `add_to_cart()`, there's a stock check: `if variant.stock < quantity` → error response
- In `cart()` view, items with insufficient stock get `item.error = "Unavailable or Out of stock"` and `checkout_disabled = True`

**Files:** `products/views.py` — `product_detail()`, `add_to_cart()`, `cart()`

---

## 2. Cart Flow

### Q2.1: What happens when a user decrements cart quantity to 1 and tries to decrement again?

**Answer Pattern:**
- In `update_cart_quantity()`, when `action == "dec"`:
  ```python
  if cart_item.quantity > 1:
      cart_item.quantity -= 1
  else:
      return JsonResponse({"status": "error", "message": "Minimum quantity is 1."})
  ```
- The item is NOT removed from cart — it stays at quantity 1
- If you want to remove it, the user must use the "Remove" button (`remove_from_cart`)
- **Follow-up question:** "Should quantity 1 decrement remove the item?" → Currently no, but you could add that logic

**Files:** `products/views.py` — `update_cart_quantity()`

---

### Q2.2: How is the cart total calculated? Does it consider offers and coupons?

**Answer Pattern:**
- **Raw subtotal:** `sum(item.subtotal for item in cart.items.all())` where `item.subtotal = variant.price * quantity`
- **Offer-adjusted subtotal:** `sum(item.offer_subtotal for item in cart.items.all())` where `item.offer_subtotal = get_discount_price(variant) * quantity`
- **Coupon discount:** Calculated in `calculate_cart_summary()` — applies percentage or fixed discount on the offer-adjusted subtotal
- **Final total:** `max(offer_subtotal - coupon_discount, 0)`
- The context processor `cart_summary` recalculates this on every request for the navbar display

**Files:** `products/views.py` — `calculate_cart_summary()`, `products/context_processors.py`

---

### Q2.3: What prevents a user from adding more than 5 items of the same variant?

**Answer Pattern:**
- `CartItem.quantity` has `MaxValueValidator(5)` at the model level
- `add_to_cart()` checks: `if new_quantity > 5` → returns error JSON
- `update_cart_quantity()` checks: `if cart_item.quantity < 5` before incrementing
- `wishlist_to_cart()` checks: `if cart_items.quantity >= 5` → skip
- The max is enforced at 3 layers: model validator, view logic, and wishlist transfer

**Files:** `products/models.py` — `CartItem`, `products/views.py` — multiple functions

---

### Q2.4: What happens if a user adds a variant to cart, then the admin deactivates that variant?

**Answer Pattern:**
- The `CartItem` still references the variant (FK), so it remains in the cart
- In the `cart()` view, there's a check:
  ```python
  if not item.variant.is_active or not item.variant.product.is_active or item.variant.product.is_deleted:
      item.error = "Unavailable or Out of stock"
      checkout_disabled = True
  ```
- The user sees the error message and cannot proceed to checkout
- The item stays in cart but is flagged as unavailable

**Files:** `products/views.py` — `cart()`

---

## 3. Cancellation & Return Flow

### Q3.1: Walk me through the complete cancellation flow from user request to admin approval.

**Answer Pattern:**
1. **User requests cancel** → `cancel_order_item()` renders the cancel form
2. **User submits reason** → `cancel_order_item_request()`:
   - Validates item status (can't cancel shipped/delivered items)
   - Restores variant stock: `item.variant.stock += item.quantity`
   - Sets `item.status = "partially_cancelled"`
   - Updates order status: if all items cancelled → `"cancelled"`, else → `"partially_cancelled"`
3. **Admin approves** → `order_view()` with `approve_cancel`:
   - Sets `item.status = "cancelled"`
   - Calculates `item.refund_amount = item.subtotal`
   - Credits wallet via `WalletService.credit_wallet(order.user, item.subtotal, order, source="refund")`
   - Updates `order.total_refund_amount`

**Files:** `products/views.py` — `cancel_order_item()`, `cancel_order_item_request()`, `order_view()`

---

### Q3.2: What's the difference between "partially_cancelled" and "cancelled" on an order?

**Answer Pattern:**
- **`partially_cancelled`:** Some items are cancelled, but others are still active (pending/processing/shipped)
- **`cancelled`:** ALL items in the order are cancelled
- The transition happens in `cancel_order_item_request()`:
  ```python
  active_items = order.items.exclude(status="partially_cancelled")
  if not active_items.exists():
      order.order_status = "cancelled"
  else:
      order.order_status = "partially_cancelled"
  ```
- Same logic applies for returns (`partially_returned` → `returned`)

**Files:** `products/views.py` — `cancel_order_item_request()`, `return_order_item_request()`

---

### Q3.3: When stock is restored during cancellation, what happens if the variant was deleted?

**Answer Pattern:**
- `OrderItem.variant` uses `on_delete=models.SET_NULL` — if the variant is deleted, the FK becomes `NULL`
- In `cancel_order_item_request()`: `if item.variant:` — checks for None before restoring stock
- If variant is None, stock restoration is skipped (the stock is lost)
- This is a design trade-off — soft-deleting variants would preserve the reference

**Files:** `products/models.py` — `OrderItem.variant`, `products/views.py` — `cancel_order_item_request()`

---

### Q3.4: Can a user cancel a delivered order? What about return?

**Answer Pattern:**
- **Cancel:** Blocked for `shipped` and `delivered` statuses:
  ```python
  if item.status in ["shipped", "delivered"]:
      messages.error(request, "Cannot cancel now")
  ```
- **Return:** Only allowed for `delivered` items:
  ```python
  if item.status not in ["delivered"]:
      messages.error(request, "Return allowed only after delivery")
  ```
- Already cancelled/returned items are also blocked from re-processing

**Files:** `products/views.py` — `cancel_order_item_request()`, `return_order_item_request()`

---

## 4. Wallet System

### Q4.1: How does the wallet work? When is it created and how are transactions recorded?

**Answer Pattern:**
- **Creation:** Wallet is auto-created via `post_save` signal on `Account`:
  ```python
  @receiver(post_save, sender=Account)
  def create_wallet(sender, instance, created, **kwargs):
      if created:
          Wallet.objects.create(user=instance)
  ```
- **Balance:** `Wallet.current_balance` — Decimal field, starts at 0
- **Transactions:** `WalletTransaction` records every debit/credit with:
  - `amount` — transaction amount
  - `source` — `"order_payment"` or `"refund"` (or `"referral_bonus"`)
  - `transaction_type` — `"credit"` or `"debit"`
  - `order` — linked order (nullable)
- **Atomic operations:** `WalletService.debit_wallet()` and `credit_wallet()` use `transaction.atomic()`

**Files:** `products/signals.py`, `products/service.py`, `products/models.py`

---

### Q4.2: What happens if a user tries to pay with wallet but has insufficient balance?

**Answer Pattern:**
- `WalletService.debit_wallet()` checks: `if wallet.current_balance < amount: raise ValueError("Insufficient Balance")`
- In `select_payment()`, the ValueError is caught:
  ```python
  except ValueError as e:
      messages.error(request, str(e))
  ```
- The order is already created at this point but remains in `"pending"` payment status
- **Known issue (from AUDIT):** After the error, there's no redirect — the code falls through

**Files:** `products/service.py`, `products/views.py` — `select_payment()`

---

### Q4.3: How is the wallet credited when a refund is approved?

**Answer Pattern:**
- Admin clicks "Approve Cancel" or "Approve Return" in `order_view()`
- The code calls:
  ```python
  WalletService.credit_wallet(
      order.user,
      item.subtotal,  # ← refund amount
      order,
      source="refund",
  )
  ```
- This atomically: increases `wallet.current_balance`, creates a `WalletTransaction` with `source="refund"` and `transaction_type="credit"`
- The wallet history page shows all transactions with date, amount, type, and source

**Files:** `products/views.py` — `order_view()`, `products/service.py`

---

### Q4.4: Can a user use wallet balance to partially pay for an order?

**Answer Pattern:**
- **Currently no.** The wallet payment is all-or-nothing:
  ```python
  WalletService.debit_wallet(request.user, order.total_amount, order)
  ```
- If `current_balance < order.total_amount`, it raises `ValueError` and the payment fails
- To support partial payment, you'd need to split the order total between wallet and another payment method

**Files:** `products/views.py` — `select_payment()`

---

## 5. Referral System

### Q5.1: How does the referral bonus system work end-to-end?

**Answer Pattern:**
1. **User A signs up** → gets a unique 8-character referral code (auto-generated in `Account.save()`)
2. **User B signs up** → goes to `/user/referral/` and enters User A's code
3. **`apply_referral_bonus()`** is called:
   - Validates the code exists and isn't self-referral
   - Checks `user.referred_by_id` is None (not already referred)
   - Atomically: sets `user.referred_by = referred_user`, increments `referred_user.referral_count`, adds ₹10 to wallet
4. **Wallet credit:** `WalletService` isn't used directly — instead, the wallet balance is updated manually:
   ```python
   wallet.current_balance += referral_code_amount
   wallet.save()
   WalletTransaction.objects.create(source="referral_bonus", ...)
   ```
5. **Note:** The referral code from signup form is NOT applied during signup — only via the separate referral page

**Files:** `user/referral.py`, `user/views.py` — `referral()`, `userauths/models.py`

---

### Q5.2: What prevents a user from referring themselves?

**Answer Pattern:**
- In `referral()`: `if ref_user == request.user: return redirect('user:referral')`
- In `apply_referral_bonus()`: `if referred_user == user: return`
- Double protection: both the view and the service function check for self-referral

**Files:** `user/views.py`, `user/referral.py`

---

### Q5.3: Can a user be referred by multiple people?

**Answer Pattern:**
- **No.** `referred_by` is a single ForeignKey (not M2M):
  ```python
  referred_by = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
  ```
- In `apply_referral_bonus()`: `if user.referred_by_id: return` — already has a referrer, skip
- A user can only be referred once

**Files:** `userauths/models.py`, `user/referral.py`

---

### Q5.4: How is the referral bonus amount tracked?

**Answer Pattern:**
- `Account.referral_count` — number of people referred (incremented on each successful referral)
- `Account.total_referral_amount` — total ₹ earned from referrals (incremented by `referral_code_amount` = ₹10)
- `Wallet.current_balance` — actual spendable balance
- `WalletTransaction` — detailed ledger with `source="referral_bonus"`
- These are separate from wallet balance — the referral amount goes into the wallet

**Files:** `userauths/models.py`, `products/models.py`

---

## 6. Offer & Coupon System

### Q6.1: How does the system decide between a product offer and a category offer?

**Answer Pattern:**
- `get_best_offer(product)` checks both:
  1. `Offer.objects.filter(product=product, is_active=True)` — product-level offer
  2. `Offer.objects.filter(category=product.category, is_active=True)` — category-level offer
- Validates both with `.is_valid` (checks date range and `is_active`)
- If only one exists → use it
- If both exist → compare **actual monetary savings**:
  ```python
  def calculate_saving(offer, price):
      if offer.discount_type == "percentage":
          return (price * offer.discount_value) / Decimal("100")
      return offer.discount_value
  ```
- The offer with higher saving wins (not higher percentage)

**Files:** `products/offer_service.py`

---

### Q6.2: Can a user stack a coupon on top of an offer discount?

**Answer Pattern:**
- **Yes.** The calculation order is:
  1. Apply offer discount to each item → `offer_subtotal`
  2. Apply coupon discount on the offer-adjusted subtotal
  3. Final total = `offer_subtotal - coupon_discount`
- Example: Item price ₹1000, 20% offer → ₹800. Coupon ₹100 off → ₹700 final
- The coupon is stored in `request.session["coupon_id"]` and validated at checkout

**Files:** `products/views.py` — `calculate_cart_summary()`, `select_payment()`

---

### Q6.3: What happens to the coupon if the user's cart total drops below the minimum purchase amount?

**Answer Pattern:**
- In `calculate_cart_summary()`:
  ```python
  if subtotal >= applied_coupon.min_purchase_amount:
      # apply discount
  ```
- If subtotal < min_purchase_amount, the coupon discount is 0
- The coupon remains in session but has no effect
- In `apply_coupon()`, there's also a check:
  ```python
  if cart.total_price < coupon.min_purchase_amount:
      messages.error(request, f"Minimum purchase ₹{coupon.min_purchase_amount}")
  ```

**Files:** `products/views.py` — `calculate_cart_summary()`, `apply_coupon()`

---

## 7. Edge Cases & "What If" Questions

### Q7.1: What happens if a user adds an item to cart, then the admin changes the variant price?

**Answer Pattern:**
- The `CartItem` stores a FK to `Variant`, not a snapshot of the price
- The cart recalculates totals on every request using the current `variant.price`
- If the price increases, the user pays the new price
- If the price decreases, the user benefits
- This is a design choice — some e-commerce systems snapshot the price at checkout time

**Files:** `products/models.py` — `CartItem.subtotal`

---

### Q7.2: What happens if two users try to buy the last item simultaneously?

**Answer Pattern:**
- **Known race condition (AUDIT-008):** The stock check and decrement are not atomic
- Both requests could read `stock = 1`, both pass the check, both decrement → `stock = -1`
- **Fix needed:** Use `select_for_update()` inside `transaction.atomic()`:
  ```python
  with transaction.atomic():
      variant = Variant.objects.select_for_update().get(id=variant_id)
      if variant.stock < quantity:
          return error
      variant.stock -= quantity
      variant.save()
  ```
- Currently only `WalletService` uses `select_for_update()` — payment flows don't

**Files:** `products/views.py` — `verify_payment()`, `select_payment()`

---

### Q7.3: What happens if a user applies a coupon, then removes items from cart so the total is below the minimum?

**Answer Pattern:**
- The coupon stays in `request.session["coupon_id"]`
- In `calculate_cart_summary()`, the coupon is validated:
  ```python
  if subtotal >= applied_coupon.min_purchase_amount:
      # apply
  else:
      coupon_discount = 0  # coupon exists but doesn't apply
  ```
- The coupon silently has no effect — the user sees `coupon_discount: 0`
- The coupon is only removed when: explicitly removed by user, checkout completes, or session expires

**Files:** `products/views.py` — `calculate_cart_summary()`

---

### Q7.4: What happens if a user completes payment via Razorpay but closes the browser before `verify_payment` is called?

**Answer Pattern:**
- The order is created with `payment_status = "pending"`
- A `Payment` object is created with `status = "created"`
- Stock is NOT decremented (only decremented in `verify_payment`)
- The order sits in limbo — paid on Razorpay's side but not confirmed in the app
- **This is a known issue.** In production, you'd need a webhook or cron job to reconcile Razorpay payments with your database

**Files:** `products/views.py` — `select_payment()`, `verify_payment()`

---

### Q7.5: What happens if the wallet is debited but the order creation fails?

**Answer Pattern:**
- In `select_payment()`, the order is created FIRST, then wallet is debited:
  ```python
  order = Order.objects.create(...)  # ← Order created
  ...
  WalletService.debit_wallet(request.user, order.total_amount, order)  # ← Then debited
  ```
- If `debit_wallet` raises `ValueError` (insufficient balance), the order exists with `payment_status = "pending"`
- The `ValueError` is caught but the order is NOT rolled back (it's outside the `try` block for wallet)
- **Fix needed:** Move order creation inside the wallet debit try block, or use a single `transaction.atomic()`

**Files:** `products/views.py` — `select_payment()`

---

### Q7.6: How does the system handle the case where a product has no active variants?

**Answer Pattern:**
- In `all_products()`: products are filtered with `variants__is_active=True, variants__stock__gt=0`
- A product with no active variants won't appear in the shop
- In `product_detail()`: `active_variants = [v for v in product.variants.all() if v.stock > 0 and v.is_active]`
- If `active_variants` is empty → redirect with warning "This product is out of stock"
- In `home()`: products are filtered with the same variant conditions

**Files:** `products/views.py` — `all_products()`, `product_detail()`, `core/views.py`

---

### Q7.7: What happens to order items when the admin changes the order status to "cancelled"?

**Answer Pattern:**
- In `order_view()` with `update_order`:
  ```python
  order.order_status = order_status
  order.save()
  order.items.all().update(status=order_status)
  ```
- ALL items get the same status as the order
- **But stock is NOT restored** — only `cancel_order_item_request()` restores stock per-item
- **This is a potential issue:** Admin bulk-cancel doesn't restore stock

**Files:** `products/views.py` — `order_view()`

---

### Q7.8: What happens if a user tries to use the same coupon twice?

**Answer Pattern:**
- Coupons don't have a "used" tracking mechanism
- The same coupon code can be applied to multiple orders
- `apply_coupon()` only checks: code exists, is_active, and cart meets min_purchase_amount
- There's no `usage_count` or `used_by` field on the `Coupon` model
- **This means a coupon can be reused infinitely** — this might be intentional (e.g., seasonal codes) or a gap

**Files:** `products/models.py` — `Coupon`, `products/views.py` — `apply_coupon()`

---

## 8. Architecture & Design Questions

### Q8.1: Why did you use two separate OTP models instead of one?

**Answer Pattern:**
- `userauths.utility.OTP` — keyed by `email` (for signup verification, before user exists)
- `user.utility.OTP` — keyed by `user` FK (for profile changes, user already exists)
- The signup OTP can't use a FK because the user hasn't been created yet
- **Improvement:** Could unify with a nullable `user` FK and an `email` field, plus a `purpose` field

**Files:** `userauths/utility.py`, `user/utility.py`

---

### Q8.2: Why is the payment flow duplicated in `products/views.py` and `payment/views.py`?

**Answer Pattern:**
- `products/views.py` `verify_payment()` — handles Razorpay signature verification, stock decrement, cart cleanup
- `payment/views.py` `verify_payment()` — simpler version, no stock management, has `@csrf_exempt`
- This is technical debt — the `payment/` app version appears to be an earlier implementation that was superseded
- Only one should exist in production

**Files:** `products/views.py`, `payment/views.py`

---

### Q8.3: Why do you use session-based coupon tracking instead of storing it on the Cart model?

**Answer Pattern:**
- Coupons are stored in `request.session["coupon_id"]` rather than on the `Cart` model
- **Pros:** No database writes when applying/removing coupons; coupon is temporary and should expire with session
- **Cons:** Coupon is lost if session expires; can't track coupon usage analytics
- The old Cart model had a `coupon` FK that was removed in migration `0016`

**Files:** `products/views.py`, `products/context_processors.py`

---

### Q8.4: Explain the checkout flow from cart to payment confirmation.

**Answer Pattern:**
1. **Cart** → User reviews items, applies coupon
2. **Checkout** (`/products/checkout/`) → Select shipping address
3. **Select Payment** (`/products/select_payment/`) → Choose COD/Wallet/Razorpay
4. **Order Creation** → `Order` + `OrderItem` objects created atomically
5. **Payment Processing:**
   - **COD:** Mark as paid, decrement stock, clear cart
   - **Wallet:** Debit wallet, decrement stock, clear cart
   - **Razorpay:** Create Razorpay order, return JSON for frontend SDK
6. **Razorpay Verify** (`/products/verify-payment/`) → Verify signature, decrement stock, clear cart
7. **Success** (`/products/payment-successful/<order_id>/`) → Show confirmation

**Files:** `products/views.py` — `checkout()`, `select_payment()`, `verify_payment()`, `payment_successful()`

---

## 9. Quick-Fire Questions (for live coding)

| # | Question | Key Point |
| :--- | :--- | :--- |
| 1 | "What's the max quantity per cart item?" | 5 (enforced at model + view level) |
| 2 | "How does the offer engine decide which offer to apply?" | Compares actual ₹ savings, not percentages |
| 3 | "What happens to stock when an order is cancelled?" | Restored via `item.variant.stock += item.quantity` |
| 4 | "How is the refund amount calculated?" | Currently `item.subtotal` (known issue: ignores coupons) |
| 5 | "Why is `transaction.atomic()` used in WalletService?" | Prevents race conditions on concurrent debits |
| 6 | "What's the difference between `is_deleted` and `is_active`?" | `is_deleted` = soft delete (hides from catalog), `is_active` = temporarily disabled |
| 7 | "How does the system prevent duplicate variant sizes?" | `unique_together = ["product", "size"]` at DB level |
| 8 | "What signal creates the wallet?" | `post_save` on `Account` → `Wallet.objects.create()` |
| 9 | "How are Razorpay payments verified?" | Backend calls `client.utility.verify_payment_signature()` |
| 10 | "What's stored in `OrderItem` vs `Order`?" | Order: user, address, totals. OrderItem: variant, quantity, price, status, refund |

---

*Generated for Campeón e-commerce project review preparation — June 2026*
