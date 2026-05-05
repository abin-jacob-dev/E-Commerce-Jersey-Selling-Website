from django.urls import path
from . import views

app_name = "products"

urlpatterns = [

    #categories
    path("categories/", views.categories, name="categories"),
    path("add-new-category/", views.add_new_category, name="add_new_category"),
    path("edit-category/<id>", views.edit_category, name="edit_category"),
    path("delete-category/<id>", views.delete_category, name="delete_category"),

    #products
    path("products-list/", views.products_list, name="products_list"),
    path("add-product/", views.add_product, name="add_product"),
    path("edit-product/<id>", views.edit_product, name="edit_product"),
    path("delete-product/<id>", views.delete_product, name="delete_product"),

    #colors
    path("colors/", views.colors, name="colors"),
    path("add-color/", views.add_color, name="add_color"),
    path("edit-color/<id>", views.edit_color, name="edit_color"),
    path("delete-color/<id>", views.delete_color, name="delete_color"),

    path('all-products',views.all_products,name='all_products'),
    path('product-detail/<id>',views.product_detail,name='product_detail'),

]
