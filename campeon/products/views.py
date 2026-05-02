from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib import messages
from products.forms import CategoryForm, ProductForm, ColorForm
from .models import Category, Product, Variant, Color, VariantImage


# Create your views here.
def categories(request):
    categories = Category.objects.filter(is_deleted=False).order_by("-created_at")
    search_query = request.GET.get("search")

    if search_query:
        categories = categories.filter(name__icontains=search_query).order_by(
            "-created_at"
        )
    paginator = Paginator(categories, 1)  # Show 25 contacts per page.

    page_number = request.GET.get("page")
    categories = paginator.get_page(page_number)
    return render(
        request, "admin/products/categories/categories.html", {"categories": categories}
    )


def add_new_category(request):
    form = CategoryForm()
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect("products:categories")
        else:
            print(form.errors)
    return render(
        request, "admin/products/categories/add_new_category.html", {"form": form}
    )


def edit_category(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect("products:categories")
    else:
        form = CategoryForm(instance=category)
    return render(
        request,
        "admin/products/categories/edit_category.html",
        {"form": form, "category": category},
    )


def delete_category(request, id):
    category = Category.objects.get(id=id)
    if request.method == "POST":
        category.is_deleted = True
        category.save()
        return redirect("products:categories")
    return render(
        request,
        "admin/products/categories/delete_category.html",
        {"category": category},
    )


def colors(request):
    colors_list = Color.objects.all().order_by("name")
    return render(
        request, "admin/products/colors/colors.html", {"colors": colors_list}
    )


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
    products = Product.objects.all()
    return render(request, "admin/products/products/products_list.html",{'products':products})




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
                variant_statuses = request.POST.getlist("variant_is_active")

                for i in range(len(sizes)):
                    
                    discount = discounts[i] if i < len(discounts) else 0
                    stock = stocks[i] if i < len(stocks) else 0
                    variant_active = (
                        variant_statuses[i] == "true"
                        if i < len(variant_statuses)
                        else True
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


def edit_product(request):
    return render(request, "admin/products/products/edit_product.html")
