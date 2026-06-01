from django.conf import settings
import razorpay

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def create_order(amount):
    return client.order.create(
        {
            "amount": amount,
            "currency": "INR",
            # 'reciept' : 'receipt__001'
        }
    )
