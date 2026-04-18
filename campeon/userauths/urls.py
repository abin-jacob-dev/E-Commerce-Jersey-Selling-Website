from django.urls import path
from . import views

app_name = 'userauths'

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("signin/", views.signin, name="signin"),
    path("dashboard/", views.dashboard, name="dashboard"),


]
