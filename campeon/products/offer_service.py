from .models import Offer, Variant
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


def get_best_offer(product):
    product_offer = Offer.objects.filter(product=product, is_active=True).first()
    category_offer = Offer.objects.filter(
        category=product.category, is_active=True
    ).first()

    if product_offer and not product_offer.is_valid:
        product_offer = None
    if category_offer and not category_offer.is_valid:
        category_offer = None
    if not product_offer and not category_offer:
        return None
    if product_offer and not category_offer:
        return product_offer
    if not product_offer and category_offer:
        return category_offer
        
    # Both exist. Which one gives a better discount?
    variant = product.variants.first()
    if not variant:
        return product_offer
        
    price = variant.price
    
    def calculate_saving(offer, price):
        if offer.discount_type == "percentage":
            return (price * offer.discount_value) / Decimal("100")
        return offer.discount_value
        
    product_offer_saving = calculate_saving(product_offer, price)
    category_offer_saving = calculate_saving(category_offer, price)
    
    if product_offer_saving > category_offer_saving:
        return product_offer
    else:
        return category_offer


def get_discount_price(variant):
    price = variant.price
    product = variant.product
    offer = get_best_offer(product)

    if not offer:
        return price
    if offer.discount_type == "percentage":
        discount_amount = (price * offer.discount_value) / Decimal("100")
        return price - discount_amount
    return max(Decimal("0"), price - offer.discount_value)


# def variant_price(request):
#     variant_id = request.GET.get("variant_id")
#     variant = get_object_or_404(Variant, id=variant_id, is_active=True)
#     discount_price = get_discount_price(variant)
#     offer = get_best_offer(variant.product)
#     return JsonResponse(
#         {
#             "price": str(variant.price),
#             "discount_price": discount_price,
#             "saved_amount": str(variant_price - discount_price),
#             "has_offer": bool(offer),
#             "offer_name": offer.name if offer else "",
#         }
#     )
