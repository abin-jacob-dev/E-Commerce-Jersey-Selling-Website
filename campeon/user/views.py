from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache


# Create your views here.
@never_cache
@login_required(login_url='userauths:signin')
def profile(request):
    return render(request, "user/profile.html")


def edit_profile(request):
    return render(request, "user/edit_profile.html")


def change_password(request):
    return render(request, "user/change_password.html")


def address(request):
    return render(request, "user/address.html")


def add_address(request):
    return render(request, "user/add_address.html")


def edit_address(request):
    return render(request, "user/edit_address.html")
