from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from userauths.models import Account
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from .utility import OTP
from django.http import HttpResponse
from .forms import AddressesForm
from user.models import Addresses
import os
from django.shortcuts import get_object_or_404


# Create your views here.
@never_cache
@login_required(login_url="userauths:signin")
def profile(request):
    try:
        address = Addresses.objects.get(user=request.user, is_default=True)
    except:
        address = None
    return render(request, "user/profile.html", {"address": address})


def edit_profile(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name", "")
        phone_number = request.POST.get("phone_number", "")
        user = Account.objects.get(id=request.user.id)
        if "photo" in request.FILES:
            if user.profile_image:
                if os.path.isfile(user.profile_image.path):
                    os.remove(user.profile_image.path)
            user.profile_image = request.FILES["photo"]
        user.full_name = full_name
        user.phone_number = phone_number
        user.save()
        return redirect("user:profile")
    return render(request, "user/edit_profile.html")


def remove_photo(request):
    user = request.user

    if user.profile_image:
        if os.path.isfile(user.profile_image.path):
            os.remove(user.profile_image.path)

        user.profile_image = None
        user.save()

    return redirect("user:edit_profile")


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
            otp = OTP.objects.create(user=request.user)
            otp.generate_otp()
            otp.send_otp_email(email)
            request.session["pending_email"] = (
                email  # store temporarily to link with otp
            )

            messages.success(request, "OTP sent to your email.")

            return redirect("user:change_email")
        elif "verify_otp" in request.POST:
            entered_otp = request.POST.get("otp", "").strip()
            email = request.session.get("pending_email")
            if last_otp and not last_otp.is_expired():
                messages.warning(request,'OTP already sent. Plesase wait. ')
                return redirect('userauths:change_email')
            if not email:
                messages.error(request, "Session expired.Please request OTP again.")
                return redirect("user:change_email")
            otp_obj = OTP.objects.filter(user=user).last()
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
            messages.success(request, "Email updated successfully")
            return redirect("user:profile")

    return render(request, "user/change_email.html")

def set_default_address(request,address_id):
    address = get_object_or_404(Addresses,id =address_id,user = request.user)
    Addresses.objects.filter(user = request.user).update(is_default=False)
    address.is_default = True
    address.save()
    return redirect('user:address')

# def edit_profile(request):
#     if request.method == "POST":

#         full_name = request.POST.get("full_name", "")
#         email = request.POST.get("email", "")
#         phone_number = request.POST.get("phone_number", "")
#         print(full_name, email, phone_number)
#         otp = OTP.objects.filter(
#             user=request.user, otp=request.POST.get("otp", "")
#         ).first()
#         if "send_otp" in request.POST:
#             if otp and not otp.is_expired():
#                 messages.info(
#                     request,
#                     "You have already requested an OTP. Please verify the previous one.",
#                 )
#                 return redirect("user:edit_profile")

#             otp = OTP.objects.create(user=request.user)
#             otp.generate_otp()
#             otp.send_otp_email(email)
#             messages.info(request, "OTP has successfully send to your email")
#             return redirect("user:edit_profile")
#         elif "otp" in request.POST:
#             if otp and otp.otp == request.POST.get("otp", "") and not otp.is_expired():

#                 request.user.full_name = full_name
#                 request.user.email = email
#                 request.user.username = email.split("@")[0]
#                 request.user.phone_number = phone_number
#                 request.user.save()
#                 messages.success(request, "Your profile has been updated Successfully")
#                 return redirect("user:profile")
#             elif otp and otp.is_expired():
#                 messages.error(request, "Your OTP has expired")
#                 return redirect("user:edit_profile")
#             else:
#                 messages.error(request, "Invalid OTP. Please try again")

#     return render(request, "user/edit_profile.html")


@login_required
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        print(current_password, new_password, confirm_password)
        email = request.user.email
        user = Account.objects.get(email=email)
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


def address(request):
    user_id = request.user.id
    # user_account = Account.objects.get(id = user_id)
    address_list = Addresses.objects.filter(user=request.user.id)
    return render(request, "user/address.html", {"address_list": address_list})


def add_address(request):
    if request.method == "POST":
        form = AddressesForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)

            address.user_id = request.user.id
            if form.cleaned_data.get("is_default"):
                Addresses.objects.filter(user=request.user, is_default=True).update(
                    is_default=False
                )

            address.save()
            return redirect("user:address")
        # full_name = request.POST.get("full_name", "")
        # phone_number = request.POST.get("phone_number", "")
        # address_line_1 = request.POST.get("address_line_1", "")
        # address_line_2 = request.POST.get("address_line_2", "")
        # state = request.POST.get("state", "")
        # city = request.POST.get("city", "")
        # postal_code = request.POST.get("postal_code", "")
        # address_label = request.POST.get("address_label", "")
        # is_default = request.POST.get("is_default", "")
        # is_default = True if is_default == "on" else False
        # print(full_name, address_line_1, is_default)
        # print(request.user.id)
    else:
        form = AddressesForm()
    return render(request, "user/add_address.html", {"form": form})


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


def delete_address(request, id):
    address = Addresses.objects.get(id=id)
    if request.method == "POST":
        address.delete()
        return redirect("user:address")
    return render(request, "user/delete_address.html", {"address": address})
