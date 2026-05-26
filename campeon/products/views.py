from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from products.forms import CategoryForm, ProductForm
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
)
from user.models import Addresses
from django.db.models import Prefetch
from django.db.models import Min, Q
from datetime import timedelta, datetime
from django.utils import timezone
from django.template.loader import get_template
from django.http import HttpResponse
from userauths.views import superuser_required, user_login_required
from django.urls import reverse


# Create your views here.
@superuser_required
def categories(request):
    categories_list = Category.objects.filter(is_deleted=False).order_by("-created_at")
    search_query = request.GET.get("search")

    if search_query:
        categories_list = categories_list.filter(name__icontains=search_query)

    paginator = Paginator(categories_list, 6)  # Show 5 categories per page.

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


@superuser_required
def add_new_category(request):
    form = CategoryForm()
    if request.method == "POST":

        form = CategoryForm(request.POST, request.FILES)

        if form.is_valid():
            name = form.cleaned_data.get("name")
            if Category.objects.filter(name__iexact=name, is_deleted=False).exists():
                messages.error(request, "Category already exists")
                return render(
                    request,
                    "admin/products/categories/add_new_category.html",
                    {"form": form},
                )
            form.save()
            messages.success(request, "New Category Added")
            return redirect("products:categories")
        else:
            print(form.errors)
            messages.error(request, "Please include all the values ")
    return render(
        request, "admin/products/categories/add_new_category.html", {"form": form}
    )


@superuser_required
def edit_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES, instance=category)
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


@superuser_required
def delete_category(request, slug):
    category = Category.objects.get(slug=slug)
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

    paginator = Paginator(products_queryset, 2)  # Show 1 products per page.
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

    if request.method == "POST":
        try:
            with transaction.atomic():

                is_active = request.POST.get("is_active", "true") == "true"

                product = Product.objects.create(
                    name=request.POST.get("name"),
                    category_id=request.POST.get("category"),
                    description=request.POST.get("description"),
                    highlights=request.POST.get("highlights"),
                    is_active=is_active,
                )

                sizes = request.POST.getlist("size")

                # skus = request.POST.getlist("sku")
                prices = request.POST.getlist("price")
                discounts = request.POST.getlist("discount")
                stocks = request.POST.getlist("stock")
                variant_status = request.POST.getlist("variant_is_active")

                for i in range(len(sizes)):

                    discount = discounts[i] if i < len(discounts) else 0
                    stock = stocks[i] if i < len(stocks) else 0
                    variant_active = (
                        variant_status[i] == "true" if i < len(variant_status) else True
                    )
                    seen_sizes = set()
                    for size in sizes:
                        if size in seen_sizes:
                            messages.error(request, f"Duplicate size:{size}")
                            return redirect("prdouct:add_product")

                    variant = Variant.objects.create(
                        product=product,
                        size=sizes[i],
                        # sku=skus[i],
                        price=prices[i],
                        discount=discount,
                        stock=stock,
                        is_active=variant_active,
                    )

                    # Standard file handling from request.FILES
                    images = request.FILES.getlist(f"images_{i}[]")
                    for image in images:
                        VariantImage.objects.create(variant=variant, image=image)

            messages.success(request, "Product created successfully")
            return redirect("products:products_list")

        except Exception as e:

            print("ERROR adding product:", str(e))
            messages.error(request, f"Failed to save product: {e}")
            return redirect("products:add_product")

    categories = Category.objects.filter(is_active=True)

    return render(
        request,
        "admin/products/products/add_product.html",
        {
            "categories": categories,
            "slot_numbers": range(3),
        },
    )


@superuser_required
def edit_product(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.method == "POST":
        try:
            with transaction.atomic():
                # Update main product
                product.name = request.POST.get("name")
                product.category_id = request.POST.get("category")
                product.description = request.POST.get("description")
                product.highlights = request.POST.get("highlights")
                product.is_active = request.POST.get("is_active") == "true"
                product.save()

                # Process variants
                variant_ids = request.POST.getlist("variant_id")
                sizes = request.POST.getlist("size")

                # skus = request.POST.getlist("sku")
                prices = request.POST.getlist("price")
                discounts = request.POST.getlist("discount")
                stocks = request.POST.getlist("stock")
                variant_statuses = request.POST.getlist("variant_is_active")

                # Image deletions
                delete_image_ids = request.POST.getlist("delete_images")
                if delete_image_ids:
                    VariantImage.objects.filter(id__in=delete_image_ids).delete()

                processed_variant_ids = []

                for i in range(len(sizes)):

                    variant_id = variant_ids[i] if i < len(variant_ids) else None
                    seen_sizes = set()
                    for size in sizes:
                        if size in seen_sizes:
                            messages.error(request, f"Duplicate size:{size}")
                            return redirect("prdouct:edit_product")

                    variant_data = {
                        "size": sizes[i],
                        # "sku": skus[i],
                        "price": prices[i],
                        "discount": discounts[i] if i < len(discounts) else 0,
                        "stock": stocks[i] if i < len(stocks) else 0,
                        "is_active": (
                            variant_statuses[i] == "true"
                            if i < len(variant_statuses)
                            else True
                        ),
                    }

                    if variant_id:
                        # Update existing
                        variant = Variant.objects.get(id=variant_id, product=product)
                        for attr, value in variant_data.items():
                            setattr(variant, attr, value)
                        variant.save()
                    else:
                        # Create new
                        variant = Variant.objects.create(
                            product=product, **variant_data
                        )

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
            print(f"ERROR editing product: {str(e)}")
            messages.error(request, f"Failed to update product: {str(e)}")
            return redirect("products:edit_product", slug=product.slug)

    categories = Category.objects.filter(is_active=True)
    variants = product.variants.all()
    return render(
        request,
        "admin/products/products/edit_product.html",
        {
            "product": product,
            "categories": categories,
            "variants": variants,
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
    products = Product.objects.filter(
        is_deleted=False,
        is_active=True,
        variants__is_active=True,
        variants__stock__gt=0,
    ).annotate(min_price=Min("variants__price"))

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

    paginator = Paginator(products, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Preserve other query parameters for pagination links
    query_params = request.GET.copy()
    if "page" in query_params:
        del query_params["page"]

    category = Category.objects.filter(is_deleted=False, is_active=True)
    products = products.prefetch_related("variants__images")
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

    # Check if product has any active variants with stock
    has_stock = any(
        variant.stock > 0 and variant.is_active for variant in product.variants.all()
    )
    if not has_stock:
        messages.warning(request, "This product is currently out of stock.")
        return redirect("products:all_products")

    # Find default variant (lowest price with stock)
    active_variants = [v for v in product.variants.all() if v.stock > 0 and v.is_active]
    default_variant = (
        min(active_variants, key=lambda v: v.price)
        if active_variants
        else product.variants.first()
    )

    context = {
        "product": product,
        "default_variant": default_variant,
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

    context = {"cart": cart_obj, "items": items, "checkout_disabled": checkout_disabled}
    return render(request, "products/cart.html", context)


@user_login_required
def add_to_cart(request):
    if request.method == "POST":
        variant_id = request.POST.get("variant_id")
        quantity = int(request.POST.get("quantity", 1))

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
        return JsonResponse(
            {
                "status": "success",
                "quantity": cart_item.quantity,
                "subtotal": float(cart_item.subtotal),
                "total_price": float(cart_item.cart.total_price),
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
def select_payment(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_items = cart.items.select_related(
        "variant__product",
    ).prefetch_related("variant__images")
    if not cart_items.exists():
        messages.error(request, "Your cart is empty")
        return redirect("products:cart")
    subtotal = cart.total_price
    shipping = 0
    total = subtotal + shipping

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        request.session["payment_method"] = payment_method
        if not payment_method:
            messages.error(request, "Please select the payment method.")
            return redirect("products:select_payment")

        address_id = request.session.get("address_id")
        if not address_id:
            messages.error(request, "Please select an address.")
            return redirect("product:checkout")
        address = get_object_or_404(Addresses, id=address_id, user=request.user)
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
                subtotal=subtotal,
                shipping=shipping,
                total_amount=total,
            )

            for item in cart_items:

                OrderItem.objects.create(
                    order=order,
                    variant=item.variant,
                    product_name=item.variant.product.name,
                    size=item.variant.size,
                    price=item.variant.price,
                    quantity=item.quantity,
                    subtotal=item.subtotal,
                )

                # REDUCE STOCK
                item.variant.stock -= item.quantity
                item.variant.save()
            if payment_method == "cod":
                order.payment_status = "pending"
            elif payment_method == "wallet":
                # make the validattion if the ruppes is there or not

                order.payment_status = "paid"
            elif payment_method == "razorpay":
                # payment integration with razorpay

                order.payment_status = "pending"
            order.save()
            cart.items.all().delete()
            messages.success(request, "Order placed Successfully")
            return redirect("products:payment_successful", order_id=order.order_id)
    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
    }

    return render(request, "products/select_payment.html", context)


@user_login_required
def payment_successful(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    context = {
        "order": order,
        "order_items": order.items.all(),
        "payment_method": request.session.get("payment_method"),
    }
    return render(request, "products/payment_successful.html", context)


@user_login_required
def orders(request):

    orders_list = Order.objects.filter(user=request.user).order_by("-created_at")
    search_query = request.GET.get("search")
    if search_query:
        orders_list = orders_list.filter(order_id__icontains=search_query)
    paginator = Paginator(orders_list, 5)

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


def return_order(request):

    pass


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

    if item.status in ["cancelled", "delivered"]:
        messages.error(request, "This item cannot be cancelled.")
        return redirect("products:order_details", order_id=item.order.order_id)

    if item.variant:
        item.variant.stock += item.quantity
        item.variant.save()

    item.status = "cancelled"
    # item.is_cancelled = True
    item.cancelled_at = timezone.now()

    reason = request.POST.get("reason", "")
    if reason == "other":
        reason = request.POST.get("other_reason", "Other")
    item.cancel_reason = reason
    item.save()

    order = item.order
    active_items = order.items.exclude(status="cancelled")
    if not active_items.exists():
        order.order_status = "cancelled"
    else:
        order.order_status = "partially_cancel"
    order.save()
    messages.success(request, "Item cancelled successfully")
    return redirect("products:order_details", order_id=order.order_id)


# @user_login_required
# def download_invoice(request, order_id):
#     order = get_object_or_404(Order, order_id=order_id, user=request.user)

#     return response


def view_invoice(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    context = {"order": order}
    return render(request, "user/orders/order_invoice.html", context)


def download_invoice(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__variant__images").select_related("user"),
        order_id=order_id,
        user=request.user,
    )
    items = order.items.select_related("variant__product__category").prefetch_related(
        "variant__images"
    )
    context = {
        "order": order,
        "items": items,
    }
    return render(request, "user/orders/order_invoice_pdf.html", context)


@superuser_required
def all_orders(request):
    orders_list = Order.objects.all().order_by("-created_at")
    search_query = request.GET.get("search")
    if search_query:
        orders_list = orders_list.filter(order_id__icontains=search_query)
    paginator = Paginator(orders_list, 5)
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
            order_status = request.POST.get("order_status")
            if order_status:
                order.order_status = order_status
                order.save()

                order.items.all().update(status=order_status)

                messages.success(
                    request,
                    f"Order status updated to {order.get_order_status_display()}",
                )
                return redirect("products:order_view", order_id=order.order_id)

        elif "update_item_status" in request.POST:
            item_id = request.POST.get("item_id")
            item_status = request.POST.get("status")
            if item_id and item_status:
                item = get_object_or_404(OrderItem, id=item_id, order=order)
                item.status = item_status
                item.save()

                messages.success(
                    request, f"Item status updated to {item.get_status_display()}"
                )
                return redirect("products:order_view", order_id=order.order_id)

    context = {"order": order}
    return render(request, "admin/orders/order_view.html", context)
