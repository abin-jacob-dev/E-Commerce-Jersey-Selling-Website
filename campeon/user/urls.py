from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    path("profile/", views.profile, name="profile"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("change-password/", views.change_password, name="change_password"),
    path("address/", views.address, name="address"),
    path("add-address/", views.add_address, name="add_address"),
    path("edit-address/", views.edit_address, name="edit_address"),
]
