from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from userauths.models import Account
from django.contrib.auth.hashers import check_password
from django.contrib import messages


# Create your views here.
@never_cache
@login_required(login_url="userauths:signin")
def profile(request):
    return render(request, "user/profile.html")


def edit_profile(request):
    return render(request, "user/edit_profile.html")


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
    return render(request, "user/address.html")


def add_address(request):
    return render(request, "user/add_address.html")


def edit_address(request):
    return render(request, "user/edit_address.html")
