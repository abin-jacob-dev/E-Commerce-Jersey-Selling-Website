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


@csrf_exempt
def verify_payment(request):
    if request.method == "POST":

        data = json.loads(request.body.decode("utf-8"))

        payment_id = data.get("razorpay_payment_id")
        razorpay_order_id = data.get("razorpay_order_id")
        signature = data.get("razorpay_signature")

        order_id = request.session.get("order_id")

        order = get_object_or_404(Order, id=order_id)

        payment = get_object_or_404(Payment, razorpay_order_id=razorpay_order_id)
        payment.razorpay_payment_id = payment_id
        payment.razorpay_signature = signature
        payment.status = "paid"
        payment.save()

        order.payment_status = "paid"
        order.save()

        cart = Cart.objects.get(user=request.user)
        cart.items.all().delete()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False})