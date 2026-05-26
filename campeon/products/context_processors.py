from .models import Cart


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
