from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("categories/", views.categories, name="categories"),
    path("add-new-category/", views.add_new_category, name="add_new_category"),
    path("edit-category/<id>", views.edit_category, name="edit_category"),
    path("delete-category/<id>", views.delete_category, name="delete_category"),
]
