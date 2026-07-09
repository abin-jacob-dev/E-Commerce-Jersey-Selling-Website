from django.shortcuts import render
from products.models import Category, Product
import logging

logger = logging.getLogger(__name__)


# Create your views here.
def home(request):
    categories = Category.objects.filter(is_deleted=False, is_active=True)
    products = (
        Product.objects.filter(
            is_deleted=False,
            is_active=True,
            variants__is_active=True,
            variants__stock__gt=0,
        )
        .distinct()
        .prefetch_related("variants")[:4]
    )
    context = {
        "categories": categories,
        "products": products,
    }
    return render(request, "core/home.html", context)


def shop(request):
    return render(request, "core/shop.html")


def contact(request):
    return render(request, "core/contact.html")


def about(request):
    return render(request, "core/about.html")


def page_not_found(request, exception):
    return render(request, "core/404.html", status=404)

def server_error(request):
    return render(request, "core/500.html", status=500)


def permission_denied(request, exception):
    return render(request, "core/403.html", status=403)


def bad_request(request, exception):
    return render(request, "core/400.html", status=400)