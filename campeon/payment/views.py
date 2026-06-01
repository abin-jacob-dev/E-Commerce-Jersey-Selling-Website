from django.shortcuts import render
from django.conf import settings
from .services import create_order
from .models import Payment

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import razorpay

# Create your views here.


def payment_page(request):
    order = create_order(50000)
    print(order)
    Payment.objects.create(razorpay_order_id=order["id"], amount=50000)
    context = {
        "razorpay_order_id": order["id"],
        "amount": 50000,
        "key_id": settings.RAZORPAY_KEY_ID,
    }
    return render(request, "payments/payment.html", context)


@csrf_exempt
def verify_payment(request):
    data = json.loads(request.body)
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )
    params = {
        "razorpay_order_id": data["razorpay_order_id"],
        "razorpay_payment_id": data["razorpay_payment_id"],
        "razorpay_signature": data["razorpay_signature"],
    }
    try:
        client.utility.verify_payment_signature(params)
        payment = Payment.objects.get(razorpay_order_id=data["razorpay_order_id"])

        payment.razorpay_payment_id = data["razorpay_payment_id"]
        payment.razorpay_signature = data['razorpay_signature']
        payment.status = "Paid"
        payment.save()
        return JsonResponse({"success": True})
    except Exception:
        return JsonResponse({"success": False})

