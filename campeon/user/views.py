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
    if request.method == 'POST':
        full_name = request.POST.get("full_name", "")
        phone_number = request.POST.get("phone_number", "")
        user = Account.objects.get(id = request.user.id)
        # username
        user.full_name = full_name
        user.phone_number=phone_number
        
        print(user)
    return render(request,'user/edit_profile.html')
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
