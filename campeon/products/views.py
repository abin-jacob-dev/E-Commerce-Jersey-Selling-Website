from django.shortcuts import render, redirect
from products.forms import CategoryForm
from .models import Category
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator


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


def search(request):

    return render(
        request, "admin/products/categories/categories.html", {"categories": categories}
    )
