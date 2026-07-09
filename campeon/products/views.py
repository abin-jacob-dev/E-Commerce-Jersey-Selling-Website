from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from products.forms import (
    CategoryForm,
    ProductForm,
    CouponForm,
    ReviewForm,
    OfferForm,
    VariantForm,
)
from products.models import (
    Category,
    Product,
    Variant,
    VariantImage,
    Cart,
    CartItem,
    Wishlist,
    Order,
    OrderItem,
    Coupon,
    Offer,
    Wallet,
    Review,
)
from payment.models import Payment
from user.models import Addresses
from django.db.models import Prefetch
from django.db.models import Min, Q
from datetime import timedelta, datetime
from django.utils import timezone
from django.template.loader import get_template
from django.http import HttpResponse
from userauths.views import superuser_required, user_login_required
from django.urls import reverse
from django.template.loader import render_to_string
from weasyprint import HTML
from decimal import Decimal
from datetime import datetime
from django.core.exceptions import ValidationError
from payment.services import create_order
from django.conf import settings
import razorpay
from .service import WalletService
from .offer_service import get_best_offer, get_discount_price
from django.views.decorators.cache import never_cache
import logging

logger = logging.getLogger(__name__)
# Create your views here.

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@never_cache
@superuser_required
def categories(request):
    categories = Category.objects.filter(is_deleted=False).order_by("-created_at")
    search_query = request.GET.get("search")

    if search_query:
        categories = categories.filter(name__icontains=search_query)

    paginator = Paginator(categories, 3)  # Show 5 categories per page.

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()

    if "page" in query_params:
        del query_params["page"]

    return render(
        request,
        "admin/products/categories/categories.html",
        {
            "categories": page_obj,
            "search_query": search_query,
            "query_params": query_params.urlencode(),
        },
    )


@never_cache
@superuser_required
def add_new_category(request):
    form = CategoryForm()
    if request.method == "POST":

        name = request.POST.get("name")
        if Category.objects.filter(name__iexact=name, is_deleted=False).exists():
            messages.error(request, "Category already exists")
            return render(
                request,
                "admin/products/categories/add_new_category.html",
                {"form": form},
            )
        form = CategoryForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "New Category Added")
            return redirect("products:categories")
        else:
            print(form.errors)
            messages.error(request, "Please include all the values ")
    return render(
        request, "admin/products/categories/add_new_category.html", {"form": form}
    )


@never_cache
@superuser_required
def edit_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if request.method == "POST":

        form = CategoryForm(request.POST, request.FILES, instance=category)
        name = request.POST.get("name")
        if (
            Category.objects.filter(name__iexact=name, is_deleted=False)
            .exclude(id=category.id)
            .exists()
        ):
            messages.error(request, "Category already exists")
            return render(
                request,
                "admin/products/categories/edit_category.html",
                {"form": form, "category": category},
            )
        if form.is_valid():
            form.save()
            messages.success(request, "Updated the Category")
            return redirect("products:categories")
    else:
        form = CategoryForm(instance=category)
    return render(
        request,
        "admin/products/categories/edit_category.html",
        {"form": form, "category": category},
    )


@never_cache
@superuser_required
def delete_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if request.method == "POST":
        category.is_deleted = True
        category.save()
        messages.error(request, "You have deleted the Category")
        return redirect("products:categories")
    return render(
        request,
        "admin/products/categories/delete_category.html",
        {"category": category},
    )


@superuser_required
def products_list(request):
    products_queryset = (
        Product.objects.select_related("category")
        .prefetch_related("variants")
        .filter(is_deleted=False)
        .order_by("-updated_at")
    )

    search_query = request.GET.get("search")
    category_id = request.GET.get("category")
    status = request.GET.get("status")

    if search_query:
        products_queryset = products_queryset.filter(name__icontains=search_query)

    if category_id and category_id.isdigit():
        products_queryset = products_queryset.filter(category_id=category_id)

    if status == "Active":
        products_queryset = products_queryset.filter(is_active=True)
    elif status == "Inactive":
        products_queryset = products_queryset.filter(is_active=False)

    paginator = Paginator(products_queryset, 3)  # Show 1 products per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(is_deleted=False)

    query_params = request.GET.copy()
    if "page" in query_params:
        del query_params["page"]

    context = {
        "products": page_obj,
        "categories": categories,
        "query_params": query_params.urlencode(),
        "selected_category": category_id,
        "selected_status": status,
        "search_query": search_query,
    }
    return render(request, "admin/products/products/products_list.html", context)


@superuser_required
def add_product(request):
    form = ProductForm()
    variant_forms = []
    image_errors = []
    if request.method == "POST":
        form = ProductForm(request.POST)
        sizes = request.POST.getlist("size")
        prices = request.POST.getlist("price")
        stocks = request.POST.getlist("stock")
        variant_status = request.POST.getlist("variant_is_active")
        seen_sizes = set()
        variant_forms = []
        errors = []
        valid = True

        # Validate product form first
        if not form.is_valid():
            valid = False

        # Validate variants
        for i in range(len(sizes)):
            variant_data = {
                "size": sizes[i],
                "price": prices[i] if i < len(prices) else 0,
                "stock": stocks[i] if i < len(stocks) else 0,
                "is_active": (
                    variant_status[i] == "true" if i < len(variant_status) else True
                ),
            }
            variant_form = VariantForm(variant_data)
            variant_forms.append(variant_form)

            if not variant_form.is_valid():
                valid = False

            # Check for duplicate sizes
            if sizes[i] in seen_sizes:
                errors.append(f"Duplicate size '{sizes[i]}'")
                valid = False
            seen_sizes.add(sizes[i])

            # Check image count
            images = request.FILES.getlist(f"images_{i}[]")
            if len(images) < 3:
                image_errors.append(i)
                valid = False

        if valid and form.is_valid():
            try:
                with transaction.atomic():
                    product = form.save()
                    for i in range(len(sizes)):
                        variant = variant_forms[i].save(commit=False)
                        variant.product = product
                        variant.save()
                        images = request.FILES.getlist(f"images_{i}[]")
                        for image in images:
                            VariantImage.objects.create(
                                variant=variant,
                                image=image,
                            )
                    messages.success(request, "Product created successfully")
                    return redirect("products:products_list")

            except Exception as e:
                messages.error(request, str(e))
        else:
            # Show a single generic error message
            messages.error(request, "Please fix all the errors below")

    categories = Category.objects.filter(is_active=True, is_deleted=False)
    size_choices = Variant.SIZE_CHOICES

    return render(
        request,
        "admin/products/products/add_product.html",
        {
            "form": form,
            "variant_forms": variant_forms,
            "size_choices": size_choices,
            "categories": categories,
            "slot_numbers": range(3),
            "post_data": request.POST if request.method == "POST" else None,
            "image_errors": image_errors,
        },
    )


@superuser_required
def edit_product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    form = ProductForm(instance=product)
    variant_forms = []
    errors = []
    image_errors = []

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        # Count how many variants we have (by checking size_0, size_1, etc.)
        variant_count = 0
        while True:
            if f"size_{variant_count}" in request.POST:
                variant_count += 1
            else:
                break

        seen_sizes = set()
        variant_forms = []
        valid = True

        # Validate product form first
        if not form.is_valid():
            valid = False

        # Validate variants
        for i in range(variant_count):
            variant_data = {
                "size": request.POST.get(f"size_{i}"),
                "price": request.POST.get(f"price_{i}"),
                "stock": request.POST.get(f"stock_{i}"),
                "is_active": (request.POST.get(f"variant_is_active_{i}") == "true"),
            }
            variant_id = request.POST.get(f"variant_id_{i}")
            if variant_id is not None and variant_id.isdigit():
                variant = Variant.objects.filter(
                    id=int(variant_id), product=product
                ).first()
                if variant:
                    variant_form = VariantForm(variant_data, instance=variant)
                else:
                    variant_form = VariantForm(variant_data)
            else:
                variant_form = VariantForm(variant_data)
            variant_forms.append(variant_form)

            if not variant_form.is_valid():
                valid = False

            # Check for duplicate sizes
            size = request.POST.get(f"size_{i}")
            if size in seen_sizes:
                errors.append(f"Duplicate size '{size}'")
                valid = False
            seen_sizes.add(size)

            # Check image count
            images = request.FILES.getlist(f"images_{i}[]")
            # If it's an existing variant, we only need to check if new images are added
            # If it's a new variant, we need at least 3 images
            if not variant_id:
                if len(images) < 3:
                    image_errors.append(i)
                    valid = False

        if valid and form.is_valid():
            try:
                with transaction.atomic():
                    product = form.save()
                    processed_variant_ids = []

                    for i in range(variant_count):
                        variant = variant_forms[i].save(commit=False)
                        variant.product = product
                        variant.save()
                        processed_variant_ids.append(variant.id)

                        # Handle new image uploads for this variant
                        new_images = request.FILES.getlist(f"images_{i}[]")
                        for img in new_images:
                            VariantImage.objects.create(variant=variant, image=img)

                    # Delete variants not present in the form
                    Variant.objects.filter(product=product).exclude(
                        id__in=processed_variant_ids
                    ).delete()

                    messages.success(request, "Product updated successfully")
                    return redirect("products:products_list")

            except Exception as e:
                messages.error(request, str(e))
        else:
            # Show a single generic error message
            messages.error(request, "Please fix all the errors below")

    categories = Category.objects.filter(is_active=True, is_deleted=False)
    variants = product.variants.all()
    # Combine variants and variant_forms
    combined_variants = []
    for i, variant in enumerate(variants):
        variant_form = variant_forms[i] if i < len(variant_forms) else None
        combined_variants.append((variant, variant_form, i))
    # Add remaining variant_forms as new variants
    for i in range(len(variants), len(variant_forms)):
        combined_variants.append((None, variant_forms[i], i))
    return render(
        request,
        "admin/products/products/edit_product.html",
        {
            "product": product,
            "categories": categories,
            "variants": variants,
            "size_choices": Variant.SIZE_CHOICES,
            "slot_numbers": range(3),
            "empty_slots": range(3),
            "form": form,
            "variant_forms": variant_forms,
            "combined_variants": combined_variants,
            "post_data": request.POST if request.method == "POST" else None,
            "image_errors": image_errors,
        },
    )


@superuser_required
def delete_product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == "POST":
        product.is_deleted = True
        product.save()
        messages.success(request, f"Product '{product.name}' deleted successfully.")
        return redirect("products:products_list")

    return render(
        request, "admin/products/products/delete_product.html", {"product": product}
    )


def all_products(request):
    products = (
        Product.objects.filter(
            is_deleted=False,
            is_active=True,
            variants__is_active=True,
            variants__stock__gt=0,
        )
        .annotate(min_price=Min("variants__price"))
        .prefetch_related("variants__images")
    )
    search_query = request.GET.get("search_query")
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(category__name__icontains=search_query)
        )
    selected_categories = request.GET.getlist("category")
    if selected_categories:
        products = products.filter(category__slug__in=selected_categories)

    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    # normalize first
    try:
        if min_price and max_price:
            if float(min_price) > float(max_price):
                min_price, max_price = max_price, min_price
    except ValueError:
        pass

    # apply filters after normalization
    if min_price:
        try:
            products = products.filter(min_price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            products = products.filter(min_price__lte=float(max_price))
        except ValueError:
            pass
    sort = request.GET.get("sort")
    if sort == "name_asc":
        products = products.order_by("name")

    elif sort == "name_desc":
        products = products.order_by("-name")

    elif sort == "price_asc":
        products = products.order_by("min_price")

    elif sort == "price_desc":
        products = products.order_by("-min_price")

    else:
        products = products.order_by("-created_at")

    paginator = Paginator(products, 3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Preserve other query parameters for pagination links
    query_params = request.GET.copy()
    if "page" in query_params:
        del query_params["page"]

    category = Category.objects.filter(is_deleted=False, is_active=True)
    # products = products.prefetch_related("variants__images")
    context = {
        "products": page_obj,
        "category": category,
        "search_query": search_query,
        "selected_categories": selected_categories,
        "page_obj": page_obj,
        "query_params": query_params.urlencode(),
    }
    return render(request, "core/shop.html", context)


def product_detail(request, slug):
    product = (
        Product.objects.filter(slug=slug, is_deleted=False, is_active=True)
        .prefetch_related(
            Prefetch(
                "variants",
                queryset=Variant.objects.filter(is_active=True).prefetch_related(
                    "images"
                ),
            )
        )
        .first()
    )

    if not product:
        messages.warning(request, "Product not found or unavailable.")
        return redirect("products:all_products")

    active_variants = [v for v in product.variants.all() if v.stock > 0 and v.is_active]
    if not active_variants:
        messages.warning(request, "This product is out of stock")
        return redirect("products:all_products")
    default_variant = min(active_variants, key=lambda v: v.price)
    offer = get_best_offer(product, variant=default_variant)
    discount_price = get_discount_price(default_variant)
    similar_products = Product.objects.filter(category=product.category,is_active=True,is_deleted=False).exclude(
        pk=product.id
    )[:4]
    print(similar_products)
    if request.user.is_authenticated:
        wishlist_variant_ids = set(
            Wishlist.objects.filter(
                user=request.user, variant__product=product
            ).values_list("variant_id", flat=True)
        )
    else:
        wishlist_variant_ids = set()
    variant_data = []
    for v in product.variants.all():
        discounted = get_discount_price(v)
        variant_data.append(
            {
                "id": v.id,
                "size": v.size,
                "price": v.price,
                "discount_price": discounted,
                "saved": v.price - discounted,
                "stock": v.stock,
                "in_wishlist": v.id in wishlist_variant_ids,
            }
        )
    saved_amount = default_variant.price - discount_price

    from .models import Review

    reviews = Review.objects.filter(product=product).select_related("user")
    user_review = None
    has_purchased = False

    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        from .models import OrderItem

        has_purchased = OrderItem.objects.filter(
            order__user=request.user, variant__product=product, status="delivered"
        ).exists()

    context = {
        "product": product,
        "default_variant": default_variant,
        "offer": offer,
        "discount_price": discount_price,
        "saved_amount": saved_amount,
        "variant_data": variant_data,
        "similar_products": similar_products,
        "reviews": reviews,
        "user_review": user_review,
        "has_purchased": has_purchased,
    }
    return render(request, "products/product_detail.html", context)


@user_login_required
def cart(request):
    cart_obj, created = Cart.objects.get_or_create(user=request.user)
    items = (
        cart_obj.items.select_related("variant__product")
        .prefetch_related("variant__images")
        .all()
    )

    # Check for unavailable or out of stock items
    checkout_disabled = False
    for item in items:
        if (
            item.variant.stock < item.quantity
            or not item.variant.is_active
            or not item.variant.product.is_active
            or item.variant.product.is_deleted
        ):
            item.error = "Unavailable or Out of stock"
            checkout_disabled = True

    coupons = Coupon.objects.filter(is_active=True)
    summary = calculate_cart_summary(cart_obj, request)
    context = {
        "cart": cart_obj,
        "items": items,
        "checkout_disabled": checkout_disabled,
        "coupons": coupons,
        "cart_subtotal": summary["subtotal"],
        "coupon_discount": summary["coupon_discount"],
        "applied_coupon": summary["applied_coupon"],
        "final_total": summary["final_total"],
    }
    return render(request, "products/cart.html", context)


@user_login_required
def add_to_cart(request):
    if request.method == "POST":
        variant_id = request.POST.get("variant_id")
        try:
            quantity = int(request.POST.get("quantity", 1))
        except (ValueError, TypeError):
            return JsonResponse({"status": "error", "message": "Invalid quantity."})

        variant = get_object_or_404(Variant, id=variant_id)

        # Prevent adding blocked/unlisted products
        if (
            not variant.product.is_active
            or variant.product.is_deleted
            or not variant.is_active
        ):
            return JsonResponse(
                {"status": "error", "message": "This product is currently unavailable."}
            )

        # Max quantity limit
        if quantity > 5:
            return JsonResponse(
                {"status": "error", "message": "Maximum 5 items allowed per product."}
            )

        # Stock validation
        if variant.stock < quantity:
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"Only {variant.stock} items left in stock.",
                }
            )

        cart_obj, created = Cart.objects.get_or_create(user=request.user)
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart_obj, variant=variant
        )

        if not item_created:
            # Increase quantity if already in cart
            new_quantity = cart_item.quantity + quantity
            if new_quantity > 5:
                cart_item.quantity = 5
                cart_item.save()
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Total quantity in cart reached the limit of 5.",
                    }
                )

            if variant.stock < new_quantity:
                return JsonResponse(
                    {"status": "error", "message": "Not enough stock to add more."}
                )

            cart_item.quantity = new_quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()

        # Remove from wishlist if added to cart
        Wishlist.objects.filter(user=request.user, product=variant.product).delete()

        return JsonResponse({"status": "success", "message": "Product added to cart!"})
    return JsonResponse({"status": "error", "message": "Invalid request."})


@user_login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Product removed from cart.")
    return redirect("products:cart")


def calculate_cart_summary(cart, request=None):
    subtotal = sum(
        get_discount_price(item.variant) * item.quantity for item in cart.items.all()
    )
    coupon_discount = Decimal("0.00")
    applied_coupon = None
    coupon_id = request.session.get("coupon_id") if request else None
    if coupon_id:
        try:
            applied_coupon = Coupon.objects.get(id=coupon_id, is_active=True)
            if applied_coupon and subtotal >= applied_coupon.min_purchase_amount:
                if applied_coupon.discount_type == "percentage":
                    coupon_discount = round(
                        (subtotal * applied_coupon.discount_value) / 100, 2
                    )
                elif applied_coupon.discount_type == "fixed":
                    coupon_discount = applied_coupon.discount_value
            else:
                coupon_discount = 0
        except Coupon.DoesNotExist:
            pass
    final_total = max(subtotal - coupon_discount, 0)
    return {
        "subtotal": subtotal,
        "coupon_discount": coupon_discount,
        "applied_coupon": applied_coupon,
        "final_total": final_total,
    }


@user_login_required
def update_cart_quantity(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        action = request.POST.get("action")

        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

        if action == "inc":
            if cart_item.quantity < 5:
                if cart_item.variant.stock > cart_item.quantity:
                    cart_item.quantity += 1
                else:
                    return JsonResponse(
                        {"status": "error", "message": "No more stock available."}
                    )
            else:
                return JsonResponse(
                    {"status": "error", "message": "Maximum limit of 5 reached."}
                )
        elif action == "dec":
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                return JsonResponse(
                    {"status": "error", "message": "Minimum quantity is 1."}
                )
        cart_item.save()
        summary = calculate_cart_summary(cart_item.cart, request)
        offer_price = get_discount_price(cart_item.variant)
        return JsonResponse(
            {
                "status": "success",
                "quantity": cart_item.quantity,
                "item_subtotal": float(offer_price * cart_item.quantity),
                "cart_subtotal": float(summary["subtotal"]),
                "coupon_discount": float(summary["coupon_discount"]),
                "final_total": float(summary["final_total"]),
                "has_coupon": request.session.get("coupon_id") is not None,
                "coupon_code": (
                    summary["applied_coupon"].code if summary["applied_coupon"] else ""
                ),
            }
        )
    return JsonResponse({"status": "error", "message": "Invalid request."})


@user_login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related(
        "variant", "variant__product", "variant__product__category"
    )
    context = {
        "wishlist_items": wishlist_items,
    }
    return render(request, "products/wishlist.html", context)


@user_login_required
def add_to_wishlist(request, slug):
    if request.method == "POST":
        action = request.POST.get("action")
        variant_id = request.POST.get("variant_id")
        quantity = int(request.POST.get("quantity", 1))
        variant = get_object_or_404(Variant, id=variant_id)

        if action == "cart":
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, variant=variant, defaults={"quantity": quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            messages.success(request, "Added to Cart")
            return redirect("products:cart")

        elif action == "wishlist":
            wishlist, created = Wishlist.objects.get_or_create(
                user=request.user, variant=variant
            )
            if created:
                messages.success(request, "Added to wishlist")
            else:
                messages.info(request, "Already in wishlist")
            return redirect("products:wishlist")

    return redirect("products:product_detail", slug=slug)


@user_login_required
def remove_from_wishlist(request, id):
    item = get_object_or_404(Wishlist, id=id, user=request.user)
    item.delete()
    return redirect("products:wishlist")


@user_login_required
def clear_wishlist(request):
    Wishlist.objects.filter(user=request.user).delete()
    messages.error(request, "Cleared all from wishlist")
    return redirect("products:wishlist")


@user_login_required
def wishlist_item_to_cart(request, variant_id):
    wishlist_item = get_object_or_404(
        Wishlist, user=request.user, variant_id=variant_id
    )
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, variant_id=variant_id, defaults={"quantity": 1}
    )
    if not created:  # item alread in cart exist
        if cart_item.quantity >= 5:
            messages.warning(request, "Maximum Item quantity reached.")
            return redirect("products:wishlist")
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, "Item quantity updated")
    else:
        messages.success(request, "Item moved to Cart Successfully")
        cart_item.quantity = 1
        cart_item.save()

    Wishlist.objects.filter(user=request.user, variant_id=variant_id).delete()

    return redirect("products:cart")


@user_login_required
def wishlist_to_cart(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    if not wishlist_items.exists():
        messages.error(request, "Wishlist is empty")
        return redirect("products:wishlist")
    added_count = 0
    skipped_count = 0
    for item in wishlist_items:
        variant = item.variant
        if not variant.is_active:
            skipped_count += 1
            continue
        if variant.stock <= 0:
            skipped_count += 1
            continue
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items, created = CartItem.objects.get_or_create(
            cart=cart, variant=variant, defaults={"quantity": 1}
        )
        if not created:
            if cart_items.quantity >= 5:
                skipped_count += 1
                continue
            else:
                cart_items.quantity += 1
        else:
            cart_items.quantity = 1
        cart_items.save()
        added_count += 1
        item.delete()

    if added_count > 0:
        messages.success(request, f"{added_count} item(s) moved to cart")
    if skipped_count > 0:
        messages.warning(request, f"{skipped_count} item(s) not added to cart")

    return redirect("products:cart")


@user_login_required
def checkout(request):

    cart, _ = Cart.objects.get_or_create(user=request.user)

    items = cart.items.select_related(
        "variant__product",
    ).prefetch_related("variant__images")

    addresses = Addresses.objects.filter(user=request.user).order_by(
        "-is_default", "-created_at"
    )
    # if items.filter(Q(variant__stock__lte=0) or Q(variant__is_active=FalseK)).exists():
    #     print('product not  found ')
    #     return redirect('products:cart')
    if not items.exists():
        messages.error(request, "Your Cart is empty.")
        return redirect("products:cart")
    if not addresses.exists():
        next_url = request.path
        add_address_url = reverse("user:add_address")
        return redirect(f"{add_address_url}?next={next_url}")

    if request.method == "POST":
        address_id = request.POST.get("selected_address")
        if not address_id:
            messages.error(request, "Please select a shipping addresses.")
            return redirect("products:checkout")
        address = get_object_or_404(Addresses, id=address_id, user=request.user)
        request.session["address_id"] = address.id
        messages.success(request, "Address selected successfully.")
        return redirect("products:select_payment")

    context = {"items": items, "addresses": addresses, "cart": cart}
    return render(request, "products/checkout.html", context)


@user_login_required
@transaction.atomic
def verify_payment(request):

    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_signature = request.POST.get("razorpay_signature")

    # payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
    try:
        payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
    except Payment.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "Payment record not found."}, status=404
        )
    order = payment.order
    if order is None:
        return JsonResponse(
            {"success": False, "message": "Order not found."}, status=404
        )

    if payment.status == "paid":
        return JsonResponse({"success": True, "order_id": order.order_id})

    try:

        client.utility.verify_payment_signature(
            {
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_order_id": razorpay_order_id,
                "razorpay_signature": razorpay_signature,
            }
        )

        for item in order.items.all():

            if item.variant.stock < item.quantity:
                return JsonResponse({"success": False, "message": "Out of stock"})

            item.variant.stock -= item.quantity
            item.variant.save()

        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = "paid"
        payment.save()

        order.payment_status = "paid"
        order.save()

        CartItem.objects.filter(cart__user=order.user).delete()

        return JsonResponse({"success": True, "order_id": order.order_id})

    except Exception:

        payment.status = "failed"
        payment.save()

        order.payment_status = "failed"
        order.save()

        return JsonResponse(
            {
                "success": False,
                "redirect_url": reverse(
                    "products:payment_failed", args=[order.order_id]
                ),
            },
            status=400,
        )


@user_login_required
def select_payment(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_items = cart.items.select_related("variant__product").prefetch_related(
        "variant__images"
    )

    if not cart_items.exists():
        messages.error(request, "Your cart is empty")
        return redirect("products:cart")
    if cart_items.filter(
        Q(variant__stock__lte=0) or Q(variant__is_active=False)
    ).exists():
        return redirect("products:cart")

    raw_subtotal = sum(item.subtotal for item in cart_items)
    offer_subtotal = sum(item.offer_subtotal for item in cart_items)
    offer_discount = raw_subtotal - offer_subtotal

    offer = True if offer_discount > 0 else None

    # ---------------- COUPON ----------------
    coupon = None
    coupon_discount = Decimal("0.00")
    coupon_id = request.session.get("coupon_id")

    if coupon_id:
        coupon = Coupon.objects.filter(id=coupon_id, is_active=True).first()
        if coupon and offer_subtotal >= coupon.min_purchase_amount:
            if coupon.is_valid:
                if coupon.discount_type == "percentage":
                    coupon_discount = (
                        offer_subtotal * coupon.discount_value
                    ) / Decimal("100")
                else:
                    coupon_discount = coupon.discount_value
            else:
                coupon = None

    shipping = Decimal("0.00")

    # ---------------- FINAL TOTAL ----------------
    total = max(offer_subtotal - coupon_discount + shipping, Decimal("0.00"))

    address_id = request.session.get("address_id")
    if not address_id:
        messages.error(request, "Select address first")
        return redirect("products:checkout")

    address = get_object_or_404(Addresses, id=address_id, user=request.user)

    if request.method == "POST":

        payment_method = request.POST.get("payment_method")

        if not payment_method:
            messages.error(request, "Select payment method")
            return redirect("products:select_payment")
        try:
            with transaction.atomic():

                order = Order.objects.create(
                    user=request.user,
                    full_name=address.full_name,
                    phone_number=address.phone_number,
                    address_line_1=address.address_line_1,
                    address_line_2=address.address_line_2,
                    city=address.city,
                    place=address.place,
                    state=address.state,
                    postal_code=address.postal_code,
                    payment_method=payment_method,
                    subtotal=raw_subtotal,
                    coupon=coupon,
                    coupon_name=coupon.code if coupon else None,
                    coupon_discount_type=coupon.discount_type if coupon else None,
                    coupon_discount_value=coupon_discount,
                    shipping=shipping,
                    total_amount=total,
                    payment_status="pending",
                )

                # save items
                for item in cart_items:
                    item_offer = get_best_offer(
                        item.variant.product, variant=item.variant
                    )
                    OrderItem.objects.create(
                        order=order,
                        variant=item.variant,
                        product_name=item.variant.product.name,
                        size=item.variant.size,
                        price=item.variant.price,
                        quantity=item.quantity,
                        subtotal=item.subtotal,
                        offer=item_offer,
                        offer_name=item_offer.name if item_offer else None,
                        offer_discount_type=(
                            item_offer.discount_type if item_offer else None
                        ),
                        offer_discount_value=(
                            item_offer.discount_value if item_offer else None
                        ),
                        offer_discount_amount=item.subtotal - item.offer_subtotal,
                        final_paid_price=(item.subtotal / order.subtotal)
                        * order.total_amount,
                    )

                # COD
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

                    cart.items.all().delete()
                    request.session.pop("coupon_id", None)
                    return redirect(
                        "products:payment_successful", order_id=order.order_id
                    )
                # WALLET
                if payment_method == "wallet":
                    wallet = Wallet.objects.select_for_update().get(user=request.user)
                    try:
                        WalletService.debit_wallet(
                            request.user, order.total_amount, order
                        )

                        cart.items.all().delete()
                        for item in order.items.all():
                            variant = item.variant

                            if variant.stock < item.quantity:
                                messages.error(request, "Stock unavailable")
                                return redirect("products:cart")

                            variant.stock -= item.quantity
                            variant.save()
                        order.payment_status = "paid"
                        order.save()
                        messages.success(request, "Payment Successful")
                        return redirect(
                            "products:payment_successful", order_id=order.order_id
                        )
                    except ValueError as e:
                        messages.error(request, str(e))

                # RAZORPAY
                if payment_method == "razorpay":

                    razorpay_order = client.order.create(
                        {
                            "amount": int(total * 100),
                            "currency": "INR",
                            "payment_capture": 1,
                        }
                    )
                    print(razorpay_order)
                    Payment.objects.create(
                        order=order,
                        amount=int(total * 100),
                        status="created",
                        razorpay_order_id=razorpay_order["id"],
                    )

                    request.session["order_id"] = order.order_id
                    request.session["razorpay_order_id"] = razorpay_order["id"]

                    return JsonResponse(
                        {
                            "success": True,
                            "razorpay_order_id": razorpay_order["id"],
                            "amount": int(total * 100),
                            "key": settings.RAZORPAY_KEY_ID,
                            "order_id": order.order_id,
                        }
                    )
        except Exception as e:
            print("Order Creation Failed : ", e)
            messages.error(
                request,
                "Something went wrong while placing your order. Please try again.",
            )
            return redirect("products:select_payment")
    context = {
        "cart_items": cart_items,
        "subtotal": raw_subtotal,
        "total": total,
        "coupon_discount": coupon_discount,
        "offer_discount": offer_discount,
        "coupon": coupon,
        "offer": offer,
    }
    return render(request, "products/select_payment.html", context)


@user_login_required
def payment_successful(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    request.session.pop("coupon_id", None)
    if order.payment_status != "paid":
        messages.error(request, "Payment not completed")
        return redirect("products:select_payment")
    context = {
        "order": order,
        "order_items": order.items.all(),
        "payment_method": request.session.get("payment_method"),
    }
    return render(request, "products/payment_successful.html", context)


@user_login_required
def payment_failed(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    context = {"order": order}
    return render(request, "products/payment_failed.html", context)


@user_login_required
def orders(request):

    orders_list = Order.objects.filter(
        user=request.user, payment_status="paid"
    ).order_by("-created_at")
    search_query = request.GET.get("search")
    if search_query:
        orders_list = orders_list.filter(order_id__icontains=search_query)
    paginator = Paginator(orders_list, 3)

    page_number = request.GET.get("page")
    orders = paginator.get_page(page_number)
    context = {"orders": orders}
    return render(request, "user/orders/orders.html", context)


@user_login_required
def order_details(request, order_id):
    order = get_object_or_404(Order, user=request.user, order_id=order_id)
    expected_delivery = order.created_at + timedelta(days=5)
    context = {"order": order, "expected_delivery": expected_delivery}
    return render(request, "user/orders/order_details.html", context)


@user_login_required
def return_order_item(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
    context = {"item": item, "order": item.order}
    return render(request, "user/orders/return_request.html", context)


@user_login_required
def return_order_item_request(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
    if request.method != "POST":
        return redirect("products:order_details", order_id=item.order.order_id)
    if item.status not in ["delivered"]:
        messages.error(request, "Return allowed only after delivery")
        return redirect("products:order_details", order_id=item.order.order_id)
    if item.status in [
        "cancelled",
        "partially_cancelled",
        "returned",
        "partially_returned",
    ]:
        return redirect("products:order_details", order_id=item.order.order_id)
    # if item.variant:
    # item.variant.stock += item.quantity
    # item.variant.save()
    item.status = "partially_returned"
    item.returned_at = timezone.now()
    reason = request.POST.get("reason", "")
    if reason == "other":
        reason = request.POST.get("other_reason", "Other")
    item.returned_reason = reason
    item.save()

    order = item.order
    active_items = order.items.exclude(status="partially_returned")
    if not active_items:
        order.order_status = "returned"
    else:
        order.order_status = "partially_returned"
    order.save()
    return redirect("products:order_details", order_id=order.order_id)


@user_login_required
def cancel_order_item(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
    context = {"item": item, "order": item.order}
    return render(request, "user/orders/cancel_request.html", context)


@user_login_required
@transaction.atomic
def cancel_order_item_request(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)

    if request.method != "POST":
        return redirect("products:order_details", order_id=item.order.order_id)

    if item.status in ["delivered"]:  # shipped
        messages.error(request, "Cannot cancel now")
        return redirect("products:order_details", order_id=item.order.order_id)

    if item.status in [
        "cancelled",
        "partially_cancelled",
        "returned",
        "partially_returned",
    ]:
        return redirect("products:order_details", order_id=item.order.order_id)

    # if item.variant:
    #     item.variant.stock += item.quantity
    #     item.variant.save()

    item.status = "partially_cancelled"
    item.cancelled_at = timezone.now()

    reason = request.POST.get("reason", "")
    if reason == "other":
        reason = request.POST.get("other_reason", "Other")
    item.cancel_reason = reason
    item.save()
    order = item.order

    # WalletService.credit_wallet(
    #     user=order.user,
    #     amount=item.final_paid_price,
    #     order=order,
    #     source="refund",
    # )

    active_items = order.items.exclude(status="cancelled")
    if not active_items.exists():
        order.order_status = "cancelled"
    else:
        order.order_status = "partially_cancelled"
    order.save()
    messages.success(request, "Item cancelled successfully")
    return redirect("products:order_details", order_id=order.order_id)


def download_invoice(request, order_id):

    order = get_object_or_404(
        Order.objects.prefetch_related("items__variant").select_related("user"),
        order_id=order_id,
        user=request.user,
    )

    context = {
        "order": order,
        "items": order.items.all(),
    }

    html_string = render_to_string(
        "user/orders/order_invoice_pdf.html", context, request=request
    )

    pdf = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf, content_type="application/pdf")

    response["Content-Disposition"] = f'attachment; filename="invoice_{order_id}.pdf"'
    return response


@superuser_required
def all_orders(request):
    orders_list = Order.objects.all().order_by("-created_at")
    search_query = request.GET.get("search")
    if search_query:
        orders_list = orders_list.filter(order_id__icontains=search_query)
    paginator = Paginator(orders_list, 3)
    page_number = request.GET.get("page")
    orders = paginator.get_page(page_number)
    context = {"orders": orders}
    return render(request, "admin/orders/all_orders.html", context)


@superuser_required
def order_view(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related("user").prefetch_related(
            "items__variant__product", "items__variant__images"
        ),
        order_id=order_id,
    )

    if request.method == "POST":

        if "update_order" in request.POST:

            if order.order_status == "cancelled":
                messages.error(request, "Cancelled orders cannot be modified.")
                return redirect(
                    "products:order_view",
                    order_id=order.order_id,
                )

            order_status = request.POST.get("order_status")

            if order_status:
                order.order_status = order_status

                order.save()

                order.items.all().update(status=order_status)

                messages.success(
                    request,
                    f"Order status updated to {order.get_order_status_display()}",
                )

                return redirect(
                    "products:order_view",
                    order_id=order.order_id,
                )

        elif "update_item_status" in request.POST:

            item_id = request.POST.get("item_id")
            item_status = request.POST.get("status")

            if item_id and item_status:

                item = get_object_or_404(
                    OrderItem,
                    id=item_id,
                    order=order,
                )

                if item.status == "cancelled":
                    messages.error(request, "Cancelled items cannot be modified.")

                    return redirect(
                        "products:order_view",
                        order_id=order.order_id,
                    )

                item.status = item_status
                item.save()

                statuses = set(order.items.values_list("status", flat=True))
                if len(statuses) == 1:
                    order.order_status = statuses.pop()
                    order.save()

                messages.success(
                    request,
                    f"Item status updated to {item.get_status_display()}",
                )

                return redirect(
                    "products:order_view",
                    order_id=order.order_id,
                )
        elif "approve_return" in request.POST:

            item_id = request.POST.get("item_id")

            if item_id:

                item = get_object_or_404(
                    OrderItem,
                    id=item_id,
                    order=order,
                )

                item.status = "returned"
                item.refund_amount = item.final_paid_price
                item.save()

                if item.variant:
                    item.variant.stock += item.quantity
                    item.variant.save()

                all_returned = order.items.exclude(status="returned").exists()

                if not all_returned:
                    order.order_status = "returned"

                order.total_refund_amount = sum(
                    item.refund_amount for item in order.items.all()
                )

                order.save()
                if order.payment_method != "cod":
                    WalletService.credit_wallet(
                        order.user,
                        item.refund_amount,
                        order,
                        source="refund",
                    )
                messages.success(
                    request,
                    f"Item status updated to {item.get_status_display()}",
                )

                return redirect(
                    "products:order_view",
                    order_id=order.order_id,
                )
        elif "approve_cancel" in request.POST:

            item_id = request.POST.get("item_id")

            if item_id:

                item = get_object_or_404(
                    OrderItem,
                    id=item_id,
                    order=order,
                )

                item.status = "cancelled"
                item.refund_amount = item.final_paid_price
                item.save()
                if item.variant:
                    item.variant.stock += item.quantity
                    item.variant.save()

                all_returned = order.items.exclude(status="cancelled").exists()

                if not all_returned:
                    order.order_status = "cancelled"

                order.total_refund_amount = sum(
                    item.refund_amount for item in order.items.all()
                )

                order.save()
                if order.payment_method != "cod":
                    WalletService.credit_wallet(
                        order.user,
                        item.refund_amount,
                        order,
                        source="refund",
                    )
                messages.success(
                    request,
                    f"Item status updated to {item.get_status_display()}",
                )

                return redirect(
                    "products:order_view",
                    order_id=order.order_id,
                )

    context = {"order": order}
    return render(request, "admin/orders/order_view.html", context)


@superuser_required
def coupons(request):
    coupons = Coupon.objects.order_by("-created_at")

    search_query = request.GET.get("search")

    if search_query:
        coupons = coupons.filter(code__icontains=search_query)

    paginator = Paginator(coupons, 3)  # Show 5 categories per page.

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()

    if "page" in query_params:
        del query_params["page"]

    context = {
        "coupons": page_obj,
        "page_obj": page_obj,
        "search_query": search_query,
        "query_params": query_params.urlencode(),
    }
    return render(request, "admin/coupons/coupons.html", context)


@superuser_required
def add_coupon(request):
    form = CouponForm()
    if request.method == "POST":
        data = request.POST.copy()
        if data.get("code"):
            data["code"] = data.get("code").upper()
        data["is_active"] = data.get("is_active") == "on"

        form = CouponForm(data)
        if form.is_valid():
            form.save()
            messages.success(request, "New Coupon Created Successfully")
            return redirect("products:coupons")
    return render(request, "admin/coupons/add_coupon.html", {"form": form})


@superuser_required
def edit_coupon(request, id):
    coupon = get_object_or_404(
        Coupon,
        id=id,
    )
    form = CouponForm(instance=coupon)
    if request.method == "POST":
        data = request.POST.copy()
        if data.get("code"):
            data["code"] = data.get("code").upper()
        data["is_active"] = data.get("is_active") == "on"

        form = CouponForm(data, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, "Coupon Updated Successfully")
            return redirect("products:coupons")

    return render(
        request, "admin/coupons/edit_coupon.html", {"coupon": coupon, "form": form}
    )


@superuser_required
def delete_coupon(request, id):
    coupon = get_object_or_404(Coupon, id=id)
    if request.method == "POST":
        coupon.delete()
        messages.success(request, "Coupon Deleted Successfully")
        return redirect("products:coupons")

    return render(request, "admin/coupons/delete_coupon.html", {"coupon": coupon})


def apply_coupon(request):
    if request.method == "POST":
        code = request.POST.get("code", "").strip().upper()
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
            cart = Cart.objects.get(user=request.user)
            if cart.total_price < coupon.min_purchase_amount:
                messages.error(
                    request, f"Minimum purchase ₹{coupon.min_purchase_amount}"
                )
                return redirect("products:cart")
            if not coupon.is_valid:
                messages.error(request, "Coupon expired")
                return redirect("products:cart")
            request.session["coupon_id"] = coupon.id
            messages.success(request, f"Coupon {coupon.code} applied")
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid Coupon")

    return redirect("products:cart")


def remove_coupon(request):
    request.session.pop("coupon_id", None)
    messages.success(request, "Coupon removed")
    return redirect("products:cart")


@superuser_required
def offers(request):
    offers = Offer.objects.all().order_by("-created_at")

    search_query = request.GET.get("search")

    if search_query:
        offers = offers.filter(name__icontains=search_query)

    paginator = Paginator(offers, 3)  # Show 5 categories per page.

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()

    if "page" in query_params:
        del query_params["page"]

    return render(
        request,
        "admin/offers/offers.html",
        {
            "offers": offers,
            "page_obj": page_obj,
        },
    )


@superuser_required
def add_offer(request):
    if request.method == "POST":
        form = OfferForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Offer has been Created Successfully")
            return redirect("products:offers")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = OfferForm()

    context = {
        "form": form,
        "products": Product.objects.filter(is_active=True, is_deleted=False),
        "categories": Category.objects.filter(is_active=True, is_deleted=False),
    }
    return render(request, "admin/offers/add_offer.html", context)


@superuser_required
def edit_offer(request, id):
    offer = get_object_or_404(Offer, id=id)

    if request.method == "POST":
        form = OfferForm(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            messages.success(request, "Offer Updated Successfully")
            return redirect("products:offers")
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = OfferForm(instance=offer)
    context = {
        "form": form,
        "offer": offer,
        "products": Product.objects.filter(is_active=True, is_deleted=False),
        "categories": Category.objects.filter(is_active=True, is_deleted=False),
    }

    return render(request, "admin/offers/edit_offer.html", context)


@superuser_required
def delete_offer(request, id):
    offer = get_object_or_404(Offer, id=id)
    if request.method == "POST":
        offer.delete()
        messages.success(request, "Offer has been deleted Successfully")
        return redirect("products:offers")
    return render(request, "admin/offers/delete_offer.html", {"offer": offer})


@user_login_required
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug, is_deleted=False)

    has_purchased = OrderItem.objects.filter(
        order__user=request.user, variant__product=product, status="delivered"
    ).exists()

    if not has_purchased:
        messages.error(
            request, "You can only review products you have purchased and received."
        )
        return redirect("products:product_detail", slug=slug)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, "Review added successfully.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Failed to add review. {error}")

    return redirect("products:product_detail", slug=slug)


@user_login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review updated successfully.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Failed to update review. {error}")

    return redirect("products:product_detail", slug=review.product.slug)


@user_login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_slug = review.product.slug
    review.delete()
    messages.success(request, "Review deleted successfully.")
    return redirect("products:product_detail", slug=product_slug)
