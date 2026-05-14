from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from products.forms import CategoryForm, ProductForm, ColorForm
from products.models import (
    Category,
    Product,
    Variant,
    Color,
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


# Create your views here.
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


def add_new_category(request):
    form = CategoryForm()
    if request.method == "POST":
        name = request.POST.get("name")
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


def colors(request):
    colors_list = Color.objects.all().order_by("name")
    return render(request, "admin/products/colors/colors.html", {"colors": colors_list})


def add_color(request):
    form = ColorForm()
    if request.method == "POST":
        form = ColorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Color added successfully")
            return redirect("products:colors")
    return render(request, "admin/products/colors/add_color.html", {"form": form})


def edit_color(request, id):
    color = get_object_or_404(Color, id=id)
    if request.method == "POST":
        form = ColorForm(request.POST, instance=color)
        if form.is_valid():
            form.save()
            messages.success(request, "Color updated successfully")
            return redirect("products:colors")
    else:
        form = ColorForm(instance=color)
    return render(
        request, "admin/products/colors/edit_color.html", {"form": form, "color": color}
    )


def delete_color(request, id):
    color = get_object_or_404(Color, id=id)
    if request.method == "POST":
        color.delete()
        messages.success(request, "Color deleted successfully")
        return redirect("products:colors")
    return render(request, "admin/products/colors/delete_color.html", {"color": color})


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

    paginator = Paginator(products_queryset, 6)  # Show 1 products per page.
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
                colors = request.POST.getlist("color")
                skus = request.POST.getlist("sku")
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

                    color = Color.objects.get(id=colors[i])

                    variant = Variant.objects.create(
                        product=product,
                        size=sizes[i],
                        color=color,
                        sku=skus[i],
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
    colors = Color.objects.all()
    return render(
        request,
        "admin/products/products/add_product.html",
        {
            "categories": categories,
            "colors": colors,
            "slot_numbers": range(3),
        },
    )


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
                colors = request.POST.getlist("color")
                skus = request.POST.getlist("sku")
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
                    # Get or create color
                    color_id = colors[i] if i < len(colors) else None
                    color = (
                        Color.objects.filter(id=color_id).first() if color_id else None
                    )

                    variant_id = variant_ids[i] if i < len(variant_ids) else None

                    variant_data = {
                        "size": sizes[i],
                        "color": color,
                        "sku": skus[i],
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
            return redirect("products:edit_product", id=id)

    categories = Category.objects.filter(is_active=True)
    colors = Color.objects.all()
    variants = product.variants.all()
    return render(
        request,
        "admin/products/products/edit_product.html",
        {
            "product": product,
            "categories": categories,
            "colors": colors,
            "variants": variants,
        },
    )


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
    has_stock = any(variant.stock > 0 for variant in product.variants.all())
    if not has_stock:
        messages.warning(request, "This product is currently out of stock.")
        return redirect("products:all_products")

    # Get unique colors for the UI selection
    unique_colors = []
    seen_color_ids = set()
    for variant in product.variants.all():
        if variant.color and variant.color.id not in seen_color_ids:
            unique_colors.append(variant.color)
            seen_color_ids.add(variant.color.id)

    context = {
        "product": product,
        "unique_colors": unique_colors,
    }
    return render(request, "products/product_detail.html", context)


def cart(request):
    cart_obj, created = Cart.objects.get_or_create(user=request.user)
    items = (
        cart_obj.items.select_related("variant__product", "variant__color")
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


def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Product removed from cart.")
    return redirect("products:cart")


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


def wishlist(request):
    wishlist_items = (
        Wishlist.objects.filter(
            user=request.user,
            product__is_active=True,
            product__is_deleted=False,
            product__variants__is_active=True,
        )
        .select_related("product", "product__category")
        .prefetch_related("product__variants__images")
        .distinct()
    )
    total_price = sum(
        item.product.variants.filter(is_active=True).first().price
        for item in wishlist_items
        if item.product.variants.filter(is_active=True).first()
    )
    context = {
        "wishlist_items": wishlist_items,
        "wishlist_count": wishlist_items.count(),
        "total_price": total_price,
    }
    return render(request, "products/wishlist.html", context)


def add_to_wishlist(request, slug):
    product = get_object_or_404(Product, slug=slug)

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user, product=product
    )

    if created:
        messages.success(request, "Product added to wishlist")
    else:
        messages.info(request, "Product already in wishlist")
    return redirect("products:all_products")


def remove_from_wishlist(request, id):
    item = get_object_or_404(Wishlist, id=id, user=request.user)
    item.delete()
    return redirect("products:wishlist")


def clear_wishlist(request):
    Wishlist.objects.filter(user=request.user).delete()
    return redirect("products:wishlist")


def wishlist_item_to_cart(request, wishlist_id):
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    product = wishlist_item.product
    variant = product.variants.filter(is_active=True, stock__gt=0).first()
    if not variant:
        messages.error(request, "Prodcut is unavailable.")
        return redirect("products:wishlist")
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        variant=variant,
        defaults={"quantity": 1},
    )
    if not created:
        if cart_item.quantity >= 5:
            messages.error(request, "Maximum quantity limit reached.")
        return redirect("products:wishlist")
        if variant.stock <= cart_item.quantity:
            messages.error(request, "Not enough stock available.")
            return redirect("products:wishlist")
        cart_item.quantity += 1
        cart_item.save()
    wishlist_item.delete()
    messages.success(request, "Item moved to Cart.")
    return redirect("products:cart")


def wishlist_to_cart(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    if not wishlist_items.exists():
        messages.error(request, "Wishlist is empty")
        return redirect("products:wishlist")
    cart, _ = Cart.objects.get_or_create(user=request.user)
    moved_count = 0
    with transaction.atomic():
        for item in wishlist_items:
            product = item.product
            variant = product.variants.filter(is_active=True, stock__gt=0).first()

            if not variant:
                continue

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                variant=variant,
                defaults={"quantity": 1},
            )

            if not created:
                if cart_item.quantity >= 5:
                    continue
                if variant.stock <= cart_item.quantity:
                    continue
                cart_item.quantity += 1
                cart_item.save()
            moved_count += 1

        wishlist_items.delete()
    messages.success(request, f"{moved_count} item(s) moved to cart successfully.")

    return redirect("products:cart")


def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)

    items = cart.items.select_related(
        "variant__product", "variant__color"
    ).prefetch_related("variant__images")

    addresses = Addresses.objects.filter(user=request.user)
    if not items.exists():
        messages.error(request, "Your Cart is empty.")
        return redirect("products:cart")

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


def select_payment(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_items = cart.items.select_related(
        "variant__product", "variant__color"
    ).prefetch_related("variant__images")
    if not cart_items.exists():
        messages.error(request, "Your cart is empty")
        return redirect("products:cart")
    subtotal = cart.total_price
    shipping = 0
    total = subtotal + shipping

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
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
                address=address,
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
                    color=item.variant.color.name if item.variant.color else "",
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
            return redirect("products:payment_successful")
    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
    }

    return render(request, "products/select_payment.html", context)


def payment_successful(request):
    cart , _ = Cart.objects.get_or_create(user=request.user)
    
    return render(request, "products/payment_successful.html")
