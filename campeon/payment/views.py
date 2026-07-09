from django.shortcuts import render
from django.conf import settings
from .services import create_order
from .models import Payment
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import razorpay
from products.models import Cart, Order
import logging

logger = logging.getLogger(__name__)
# Create your views here.


def payment_page(request):
    order_id = request.session.get("order_id")
    razorpay_order_id = request.session.get("razorpay_order_id")

    if not razorpay_order_id:
        return redirect("products:cart")

    order = Order.objects.get(id=order_id)

    context = {
        "razorpay_order_id": razorpay_order_id,
        "amount": int(order.total_amount * 100),
        "key_id": settings.RAZORPAY_KEY_ID,
    }

    return render(request, "payments/payment.html", context)

