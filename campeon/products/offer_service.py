from .models import Offer, Variant
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


def get_best_offer(product, variant=None):
    if not product:
        return None

    # Fetch all active offers targeting the product or its category
    product_offers = Offer.objects.filter(product=product, is_active=True)
    category_offers = Offer.objects.filter(category=product.category, is_active=True)

    valid_offers = []
    for offer in list(product_offers) + list(category_offers):
        if offer.is_valid:
            valid_offers.append(offer)

    #no valid offers return none
    if not valid_offers:
        return None

    if len(valid_offers) == 1:
        return valid_offers[0]

    # Determine reference price for calculations
    if variant:
        price = variant.price
    else:
        # Fallback if no variant is provided
        cheapest_variant = product.variants.filter(is_active=True, stock__gt=0).order_by("price").first()
        if not cheapest_variant:
            cheapest_variant = product.variants.filter(is_active=True).first()
        if not cheapest_variant:
            cheapest_variant = product.variants.first()
        
        price = cheapest_variant.price if cheapest_variant else Decimal("1000")

    def calculate_saving(offer, price):
        if offer.discount_type == "percentage":
            saving = (price * offer.discount_value) / Decimal("100")
        else:
            saving = offer.discount_value
        return min(saving, price)

    best_offer = None
    max_saving = Decimal("-1")

    for offer in valid_offers:
        saving = calculate_saving(offer, price)
        if saving > max_saving:
            max_saving = saving
            best_offer = offer

    return best_offer

#product detail page offer calculation
def get_discount_price(variant):
    price = variant.price
    product = variant.product
    offer = get_best_offer(product, variant=variant)

    if not offer:
        return price
    if offer.discount_type == "percentage":
        discount_amount = (price * offer.discount_value) / Decimal("100")
        return price - discount_amount
    return max(Decimal("0"), price - offer.discount_value)


