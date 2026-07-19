# Standard Library Imports
import logging

# Django Imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.cache import never_cache
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# Local Application Imports
from userauths.forms import UserSignupForm
from userauths.models import Account
from userauths.utility import OTP

logger = logging.getLogger(__name__)


def superuser_required(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return func(request, *args, **kwargs)
        return redirect("userauths:signin")

    return wrapper


def user_login_required(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_blocked:
            logout(request)
            messages.error(request, "Your Account is blocked!")
            return redirect("userauths:signin")
        # if request.user.is_authenticated and request.user.is_superuser:
        #     return redirect('admin_panel:dashboard')
        if request.user.is_authenticated and not request.user.is_blocked:
            return func(request, *args, **kwargs)
        return redirect("userauths:signin")

    return wrapper


def signup(request):
    if not request.session.get("is_email_verified"):
        return redirect("userauths:activate_account")
    verified_email = request.session.get("verified_email")
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data.get("full_name")
            email = verified_email
            username = email.split("@")[0]
            password = form.cleaned_data.get("password")
            referral_code = form.cleaned_data.get("referral_code")
            if Account.objects.filter(email=verified_email).exists():
                messages.error(request, "Email already Registered")
                return redirect("userauths:activate_account")
            user = Account.objects.create_user(
                full_name=full_name, email=email, password=password, username=username
            )
            user.is_active = True  # Active when sigin
            user.save()

            del request.session["is_email_verified"]
            del request.session["verified_email"]
            messages.success(request, "Account Created successfully")
            return redirect("userauths:signin")
    else:
        form = UserSignupForm()

    return render(request, "userauths/signup.html", {"form": form})


def activate_account(request):

    if request.method == "POST":

        if "send_otp" in request.POST:
            email = request.POST.get("email")
            request.session["verified_email"] = email
            if Account.objects.filter(email=email).exists():
                messages.error(request, "Email already Registered")
                del request.session["verified_email"]
                return redirect("userauths:activate_account")
            existing_otp = (
                OTP.objects.filter(email=email).order_by("-created_at").first()
            )
            if existing_otp and not existing_otp.is_expired():
                messages.warning(request, "OTP already sent. Please wait.")
                return redirect("userauths:activate_account")
            otp = OTP.objects.create(email=email)
            otp.generate_otp()
            otp.send_otp_email(email)
            request.session["otp_expiry"] = int(otp.expires_at.timestamp())
            messages.success(request, "OTP has been sent to your email")
            return redirect("userauths:activate_account")
        if "verify_otp" in request.POST:
            email = request.session.get("verified_email")
            entered_otp = request.POST.get("otp", "")

            otp_obj = OTP.objects.filter(email=email).order_by("-created_at").first()

            if not otp_obj:
                messages.error(request, "No OTP found!")
                return redirect("userauths:activate_account")
            if otp_obj.is_expired():
                messages.error(request, "OTP expired!")
                return redirect("userauths:activate_account")
            if otp_obj.otp != entered_otp:
                messages.error(request, "Invalid OTP")
                return redirect("userauths:activate_account")
            if otp_obj.otp == entered_otp:
                request.session["is_email_verified"] = True

                request.session.pop("otp_expiry", None)

                otp_obj.delete()
                messages.success(request, "Email Verified Successfully")
                return redirect("userauths:signup")
            request.session["is_email_verified"] = True
            otp_obj.delete()
            messages.success(request, "Email Verified Successfully")
            return redirect("userauths:signup")

    return render(
        request,
        "userauths/activate_account.html",
        {"otp_expiry": request.session.get("otp_expiry")},
    )


@never_cache
def signin(request):
    if request.user.is_authenticated:
        return redirect("core:shop")  # dashboard
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(email=email, password=password)

        if user is None:
            messages.error(request, "Invalid Credentials")

            return redirect("userauths:signin")
        if user.is_blocked:
            messages.error(request, "Your acccount has been blocked")

            return redirect("userauths:signin")

        login(request, user)

        messages.success(request, "You are now logged in.")
        if user.is_superuser:
            return redirect("admin_panel:dashboard")
        return redirect("user:profile")  # dashboard
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

        reset_path = reverse(
            "userauths:reset_password_validate",
            kwargs={
                "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            },
        )
        reset_url = f"{settings.SITE_URL.rstrip('/')}{reset_path}"

        mail_subject = "Reset your Password"
        message = render_to_string(
            "userauths/reset_password_email.html",
            {
                "user": user,
                "reset_url": reset_url,
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


def reset_password(request):
    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("userauths:reset_password")

        try:
            validate_password(password)
        except ValidationError as e:
            messages.error(request, e.messages[0])
            return redirect("userauths:reset_password")

        uid = request.session.get("uid")
        if not uid:
            messages.error(request, "Reset session has expired.")
            return redirect("userauths:forgot_password")

        user = Account.objects.get(pk=uid)
        user.set_password(password)
        user.save()

        request.session.pop("uid", None)

        messages.success(request, "Password reset successfully.")
        return redirect("userauths:signin")

    return render(request, "userauths/reset_password.html")


# def reset_password(request):  # only works with verification link because of uid
#     if request.method == "POST":
#         password = request.POST.get("password")
#         confirm_password = request.POST.get("confirm_password")

#         if password == confirm_password:
#             uid = request.session.get("uid")

#             user = Account.objects.get(pk=uid)
#             user.set_password(password)
#             user.save()
#             messages.success(request, "Your Password set Succesfully")
#             return redirect("userauths:signin")
#         else:
#             messages.error(request, "Passwords does not match")
#             return redirect("userauths:reset_password")

#     else:
#         return render(request, "userauths/reset_password.html")


@never_cache
def signin_admin(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            login(request, user)
            return redirect("admin_panel:dashboard")
        else:
            messages.error(request, "You do not have admin access.")
            return redirect("userauths:signin")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(email=email, password=password)

        if user is None:
            messages.error(request, "Invalid Credentials")
            return render(request, "userauths/signin_admin.html")
        if user.is_superuser:
            login(request, user)
            return redirect("admin_panel:dashboard")
        else:
            messages.error(request, "You do not have admin access.")
            return redirect("userauths:signin")
    return render(request, "userauths/signin_admin.html")


@never_cache
@login_required()
def signout_admin(request):
    logout(request)
    return redirect("userauths:signin")
