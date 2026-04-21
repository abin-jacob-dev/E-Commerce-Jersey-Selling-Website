from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import UserSignupForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Account
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.cache import never_cache


# verification email import
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


# Create your views here.
# @never_cache
# @login_required(login_url="userauths:signin")
# def dashboard(request):
#     print(request.user.is_authenticated, request.user.is_active)
#     return render(request, "userauths/dashboard.html")


def signup(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data.get("full_name")
            email = form.cleaned_data.get("email")
            username = email.split("@")[0]
            password = form.cleaned_data.get("password")
            referral_code = form.cleaned_data.get("referral_code")
            user = Account.objects.create_user(
                full_name=full_name, email=email, password=password, username=username
            )
            user.referral_code = referral_code
            user.save()

            # User Activation
            current_site = get_current_site(request)
            mail_subject = "Please Activate your account"
            message = render_to_string(
                "userauths/account_verificaton_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(
                        force_bytes(user.pk)
                    ),  # encoding the pk
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # messages.success(request,'Thank you for registering with us . We have send the Verification email to your email address.Please Verify it.')
            return redirect(
                f"{reverse('userauths:signin')}?command=verification&email={email}"
            )
    else:
        form = UserSignupForm()
    context = {"form": form}
    return render(request, "userauths/signup.html", context)


@never_cache
def signin(request):
    if request.user.is_authenticated:
        return redirect('user:profile')#dashboard
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        print(email, password)
        user = authenticate(email=email, password=password)
        print(user)
        if user is None:
            messages.error(request, "Invalid Credentials")
            print("user is none")
            return redirect("userauths:signin")
        if user.is_blocked:
            messages.error(request, "Your acccount has been blocked")
            print("user blocked")
            return redirect("userauths:signin")

        login(request, user)
        print("user logged in")
        messages.success(request, "You are now logged in.")
        # if user.is_staff or user.role == "admin":
        #     return redirect("userauths:dashboard")

        return redirect("user:profile") #dashboard
    return render(request, "userauths/signin.html")


@never_cache
@login_required()
def signout(request):
    logout(request)
    messages.success(request, "You have Signed Out!")
    return redirect("userauths:signin")


@never_cache
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        messages.error(request, "Invalid Link")
        return redirect("userauths:signup")

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account Activated")
        return redirect("userauths:signin")
    else:
        messages.error(request, "Invalid Link")
        return redirect("userauths:signup")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = Account.objects.get(email__iexact=email)
        except Account.DoesNotExist:
            messages.error(request, "Account with this email does not exist.")
            return redirect("userauths:forgot_password")
        # Reset Password Email
        current_site = get_current_site(request)
        mail_subject = "Reset your Password"
        message = render_to_string(
            "userauths/reset_password_email.html",
            {
                "user": user,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),  # encoding the pk
                "token": default_token_generator.make_token(user),
            },
        )
        to_email = email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()
        messages.success(
            request, "Password reset email has been sent to your email address."
        )
        return redirect("userauths:signin")
    return render(request, "userauths/forgot_password.html")


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        messages.error(request, "This link has been Expired !")
        return redirect("userauths:signin")
    if default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "Please Reset Your Password")
        return redirect("userauths:reset_password")
    else:
        messages.error(request, "This link has been Expired !")
        return redirect("userauths:signin")


def reset_password(request):  # only works with verification link because of uid
    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        print(password, confirm_password)
        if password == confirm_password:
            uid = request.session.get("uid")
            print(uid)
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Your Password set Succesfully")
            return redirect("userauths:signin")
        else:
            messages.error(request, "Passwords does not match")
            return redirect("userauths:reset_password")

    else:
        return render(request, "userauths/reset_password.html")

@never_cache
def signin_admin(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            login(request,user)
            return redirect('admin_panel:dashboard')
        else:
            messages.error(request, 'You do not have admin access.')
            return redirect('userauths:signin')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email =email,password = password)
        print(user)
        if user is None:
            messages.error(request,'Invalid Credentials')
            return render(request,'userauths/signin_admin.html')
        if user.is_superuser:
            login(request,user)
            return redirect('admin_panel:dashboard')
        else:
            messages.error(request, 'You do not have admin access.')
            return redirect('userauths:signin')
    return render(request,'userauths/signin_admin.html')

@never_cache
def signout_admin(request):
    logout(request)
    return redirect('userauths:signin_admin')