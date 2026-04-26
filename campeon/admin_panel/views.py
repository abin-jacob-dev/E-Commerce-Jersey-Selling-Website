from django.shortcuts import render, redirect
from userauths.models import Account
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.sessions.models import Session
from django.utils.timezone import now


# Create your views here.
def user_management_search(request):
    search_user = request.GET.get("search_user")
    sort_by = request.GET.get("sort_by", "full_name")
    users = Account.objects.filter(is_superadmin=False)
    if search_user:
        users = Account.objects.filter(
            Q(full_name__icontains=search_user) | Q(email__icontains=search_user)
        )
    if sort_by in ['full_name','email','date_joined'] :
        users = users.order_by(sort_by)   
    else:

        # users = Account.objects.filter(is_active=True)
        users = users.order_by('-full_name')
    # if sort_by in ['full_name','email','date_joined']:
    #     sort_by = users.order_by(sort_by)
    # else:
    #     sort_by=user.order_by('-full_name')
    paginator = Paginator(users, 1)  # Show 25 contacts per page.

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request, "admin/user_management.html", {"users": page_obj, "sort_by": sort_by,'page_obj':page_obj}
    )


def users(request):
    users = Account.objects.filter(is_superadmin=False).order_by('full_name')

    paginator = Paginator(users, 10)  # same as search view
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "admin/user_management.html",
        {
            "users": page_obj,
            "page_obj": page_obj,
            "sort_by": "full_name"
        }
    )

def block_user(request, id):
    user = Account.objects.get(id=id)
    if "block_user_confimed" in request.POST:
        user.is_blocked = not user.is_blocked
        user.save()
        for session in Session.objects.filter(expire_date__gte=now()):
            data = session.get_decoded()
            # print(data)
            if data.get("_auth_user_id") == str(user.id):
                # print(data.get('_auth_user_id'))
                session.delete()
        return redirect("admin_panel:users")
    return render(request, "admin/block_user.html", {"user": user})


def delete_user(request, id):
    user = Account.objects.get(id=id)
    if "delete_user_confirmed" in request.POST:
        user.delete()
        return redirect("admin_panel:users")
    return render(request, "admin/delete_user.html")


@login_required
def dashboard(request):
    return render(request, "admin/dashboard.html")
