from .models import Cart
from products.models import Coupon


def cart_data(request):
    user = request.user
    if user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return {
            "global_cart": cart,
            "global_cart_items": cart.items.select_related(
                "variant_product"
            ).prefetch_related("variant_images"),
            "global_cart_count": cart.items.count(),
        }
    return {
        "global_cart": None,
        "global_cart_items": [],
        "global_cart_count": 0,
    }


def cart_summary(request):
    if not request.user.is_authenticated:
        return {
            "cart_subtotal": 0,
            "cart_total": 0,
            "count": 0,
            "coupon_discount": 0,
            "applied_coupon": None,
        }
        
    cart, created = Cart.objects.get_or_create(user=request.user)

    subtotal = sum(item.offer_subtotal for item in cart.items.all())
    
    coupon_discount = 0
    applied_coupon = None
    coupon_id = request.session.get("coupon_id")
    if coupon_id:
        try:
            applied_coupon = Coupon.objects.get(id=coupon_id, is_active=True)
            if subtotal >= applied_coupon.min_purchase_amount:
                if applied_coupon.discount_type == "percentage":
                    from decimal import Decimal
                    coupon_discount = (subtotal * applied_coupon.discount_value) / Decimal('100')
                else:
                    coupon_discount = applied_coupon.discount_value
        except Coupon.DoesNotExist:
            request.session.pop("coupon_id", None)

    final_total = max(subtotal - coupon_discount, 0)
    
    return {
        "cart_subtotal": subtotal,
        "cart_total": final_total,
        "count": cart.items.count(),
        "coupon_discount": coupon_discount,
        "applied_coupon": applied_coupon,
    }
