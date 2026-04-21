from django.shortcuts import render, redirect
from userauths.models import Account
from django.db.models import Q
from django.core.paginator import Paginator


# Create your views here.
def user_management_search(request):
    search_user = request.GET.get("search_user")
    sort_by = request.GET.get('sort_by','full_name')
    if search_user:
        users = Account.objects.filter(
            Q(full_name__icontains=search_user) | Q(email__icontains=search_user)
        )
    else:
        users = Account.objects.all()
        # users = Account.objects.filter(is_active=True)
        # users = Account.objects.filter(is_superadmin=False)
    # if sort_by in ['full_name','email','date_joined']:
    #     sort_by = users.order_by(sort_by)
    # else:
    #     sort_by=user.order_by('-full_name')
    users_paginator = Paginator(users, 100)
    page = request.GET.get("page")
    users = users_paginator.get_page(page)
    return render(request, "admin/user_management.html", {"users": users,'sort_by':sort_by})


def user_management(request):
    users = Account.objects.all()
    return render(request, "admin/user_management.html", {"users": users})


def block_user(request, pk):
    user = Account.objects.get(id=pk)
    return redirect("user-management")

