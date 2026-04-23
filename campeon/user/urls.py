from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    path("profile/", views.profile, name="profile"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("remove-photo/", views.remove_photo, name="remove_photo"),
    path("change_email/", views.change_email, name="change_email"),
    path("change-password/", views.change_password, name="change_password"),
    path("address/", views.address, name="address"),
    path("add-address/", views.add_address, name="add_address"),
    path("edit-address/<id>", views.edit_address, name="edit_address"),
    path("delete-address/<id>", views.delete_address, name="delete_address"),
]
