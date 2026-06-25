from django.urls import path
from . import views

app_name = "payment"

urlpatterns = [
    path("", views.payment_page, name="payment_page"),
    # path("verify/", views.verify_payment, name="verify_payment"),
]

