from django.urls import path
from . import views

app_name = "userauths"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("signin/", views.signin, name="signin"),
    path("signout/", views.signout, name="signout"),
    # path("dashboard/", views.dashboard, name="dashboard"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("reset-password-validate/<uidb64>/<token>/",views.reset_password_validate,name="reset_password_validate",),
    path("reset-password/", views.reset_password, name="reset_password"),
    path("signin-admin/", views.signin_admin, name="signin_admin"),
    path("signout-admin/", views.signout_admin, name="signout_admin"),
]
