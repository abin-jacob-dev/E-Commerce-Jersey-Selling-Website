from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from userauths.models import Account
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from .utility import OTP
from django.http import HttpResponse
from .forms import AddressesForm, EditProfileForm, ReferralForm
from user.models import Addresses
import os
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .referral import apply_referral_bonus

from user.utility import validate_password
from user.utility import validate_name
from userauths.views import user_login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import razorpay
from products.models import Wallet, WalletTransaction
from payment.models import Payment
from userauths.models import Account
import logging

logger = logging.getLogger(__name__)


# Create your views here.
@never_cache
@user_login_required
def profile(request):
    try:
        address = Addresses.objects.get(user=request.user, is_default=True)

    except:
        address = None
    return render(
        request, "user/profile.html", {"address": address, "account": request.user}
    )


@never_cache
@user_login_required
def edit_profile(request):
    user = request.user
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Profile saved successfully.")
                return redirect("user:profile")
            except Exception as e:
                logger.error(f"Profile save failed: {e}")
                messages.error(request, "Failed to save profile. Please try again.")

        messages.error(request, "Please Correct the errors below")
    else:
        form = EditProfileForm(instance=user)
    return render(request, "user/edit_profile.html", {"form": form})


@never_cache
@user_login_required
def remove_photo(request):
    user = request.user

    if user.profile_image:
        if os.path.isfile(user.profile_image.url):
            os.remove(user.profile_image.url)

        user.profile_image = None
        user.save()

    return redirect("user:edit_profile")


@never_cache
@user_login_required
def change_email(request):
    user = request.user
    if request.method == "POST":
        if "send_otp" in request.POST:
            email = request.POST.get("email", "")
            if user.email == email:
                messages.error(request, "Please Enter a new mail")
                return redirect("user:change_email")

            if Account.objects.exclude(id=user.id).filter(email=email).exists():
                messages.error(request, "Email is already in use.")
                return redirect("user:change_email")
            last_otp = OTP.objects.filter(user=user).order_by("-created_at").first()
            if last_otp and not last_otp.is_expired():
                messages.error(request, "Please wait before requesting another OTP.")
                return redirect("user:change_email")

            otp = OTP.objects.create(user=user)
            otp.generate_otp()
            otp.send_otp_email(email)
            request.session["pending_email"] = email  # temporarily to link with otp
            request.session["otp_expiry"] = (
                timezone.now() + timedelta(minutes=5)
            ).timestamp()

            messages.success(request, "OTP sent to your email.")

            return redirect("user:change_email")
        elif "verify_otp" in request.POST:
            entered_otp = request.POST.get("otp", "").strip()
            email = request.session.get("pending_email")

            if not email:
                messages.error(request, "Session expired.Please request OTP again.")
                return redirect("user:change_email")
            otp_obj = OTP.objects.filter(user=user).order_by("-created_at").first()

            if not otp_obj:
                messages.error(request, "No OTP found. Please request again.")
                return redirect("user:change_email")
            if otp_obj.is_expired():
                messages.error(request, "Your OTP has expired,Please request a new one")
                return redirect("user:change_email")
            if otp_obj.otp != entered_otp:
                messages.error(request, "Invalid OTP.")
                return redirect("user:change_email")
            user.email = email
            user.username = email.split("@")[0]
            user.save()
            otp_obj.delete()
            request.session.pop("pending_email", None)
            request.session.pop("otp_expiry", None)
            messages.success(request, "Email updated successfully")
            return redirect("user:profile")

    return render(
        request,
        "user/change_email.html",
        {"otp_expiry": request.session.get("otp_expiry")},
    )


@never_cache
@user_login_required
def set_default_address(request, address_id):
    address = get_object_or_404(Addresses, id=address_id, user=request.user)
    Addresses.objects.filter(user=request.user).update(is_default=False)
    address.is_default = True
    address.save()
    return redirect("user:address")


@never_cache
@user_login_required
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        print(current_password, new_password, confirm_password)
        email = request.user.email
        user = Account.objects.get(email=email)
        error = validate_password(new_password)
        if error:
            messages.error(request, error)
            return redirect("user:change_password")
        if new_password != confirm_password:
            messages.error(request, "New Passwords donot match")
            return redirect("user:change_password")
        else:
            if not check_password(current_password, user.password):
                messages.error(request, "You have Entered the wrong password")
                return redirect("user:change_password")
            else:
                user.set_password(new_password)
                user.save()
                messages.success(request, "New Password set Successfully")
                return redirect("user:change_password")
    return render(request, "user/change_password.html")


@never_cache
@user_login_required
def address(request):
    user_id = request.user.id
    address_list = Addresses.objects.filter(user=request.user.id)
    return render(request, "user/address.html", {"address_list": address_list})


@never_cache
@user_login_required
def add_address(request):
    next_url = request.GET.get("next") or reverse("user:address")
    if request.method == "POST":
        form = AddressesForm(request.POST)
        next_url = request.POST.get("next") or reverse("user:address")
        if form.is_valid():
            address = form.save(commit=False)

            address.user_id = request.user.id
            if form.cleaned_data.get("is_default"):
                Addresses.objects.filter(user=request.user, is_default=True).update(
                    is_default=False
                )

            address.save()
            return redirect(next_url)
    else:
        form = AddressesForm()
    return render(
        request, "user/add_address.html", {"form": form, "next_url": next_url}
    )


@never_cache
@user_login_required
def edit_address(request, id):
    address = Addresses.objects.get(id=id)
    if request.method == "POST":
        form = AddressesForm(request.POST, instance=address)
        if form.is_valid():
            if form.cleaned_data["is_default"]:
                Addresses.objects.filter(user=request.user, is_default=True).exclude(
                    id=address.id
                ).update(is_default=False)
            form.save()
            return redirect("user:address")
    else:
        form = AddressesForm(instance=address)
    return render(request, "user/edit_address.html", {"form": form, "address": address})


@never_cache
@user_login_required
def delete_address(request, id):
    address = Addresses.objects.get(id=id)
    if request.method == "POST":
        if not address.is_default:
            address.delete()
            messages.success(request, "Address deleted Successfully")
        else:
            # address.delete()
            messages.error(request, "Default Address cannot be deleted")
        return redirect("user:address")
    return render(request, "user/delete_address.html", {"address": address})


@never_cache
@user_login_required
def wallet(request):
    wallet = Wallet.objects.get(user=request.user)
    wallet_transactions = WalletTransaction.objects.filter(wallet=wallet).order_by(
        "-created_at"
    )
    context = {"wallet": wallet, "wallet_transactions": wallet_transactions}
    return render(request, "user/wallet/wallet.html", context)


@never_cache
@user_login_required
def referral(request):
    if request.method == "POST":
        form = ReferralForm(request.user, request.POST)

        if form.is_valid():
            apply_referral_bonus(request.user, form.cleaned_data["referral_code"])

            messages.success(request, "Referral applied successfully!")
            return redirect("user:referral")

    else:
        form = ReferralForm(request.user)

    return render(request, "user/referral.html", {"form": form})
