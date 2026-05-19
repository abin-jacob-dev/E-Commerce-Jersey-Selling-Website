from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    # categories
    path("categories/", views.categories, name="categories"),
    path("add-new-category/", views.add_new_category, name="add_new_category"),
    path("edit-category/<slug:slug>", views.edit_category, name="edit_category"),
    path("delete-category/<slug:slug>", views.delete_category, name="delete_category"),
    # products
    path("products-list/", views.products_list, name="products_list"),
    path("add-product/", views.add_product, name="add_product"),
    path("edit-product/<slug:slug>", views.edit_product, name="edit_product"),
    path("delete-product/<slug:slug>", views.delete_product, name="delete_product"),
    # colors
    path("colors/", views.colors, name="colors"),
    path("add-color/", views.add_color, name="add_color"),
    path("edit-color/<id>", views.edit_color, name="edit_color"),
    path("delete-color/<id>", views.delete_color, name="delete_color"),
    path("all-products", views.all_products, name="all_products"),
    path("product-detail/<slug:slug>/", views.product_detail, name="product_detail"),
    # Cart
    path("cart/", views.cart, name="cart"),
    path("add-to-cart/", views.add_to_cart, name="add_to_cart"),
    path(
        "remove-from-cart/<item_id>/", views.remove_from_cart, name="remove_from_cart"
    ),
    path(
        "update-cart-quantity/", views.update_cart_quantity, name="update_cart_quantity"
    ),
    # Wishlist
    path("wishlist/", views.wishlist, name="wishlist"),
    path("add-to-wishlist/<slug:slug>", views.add_to_wishlist, name="add_to_wishlist"),
    path(
        "remove-from-wishlist/<int:id>/",
        views.remove_from_wishlist,
        name="remove_from_wishlist",
    ),
    path(
        "clear-wishlist/",
        views.clear_wishlist,
        name="clear_wishlist",
    ),
    path(
        "wishlist-to-cart/",
        views.wishlist_to_cart,
        name="wishlist_to_cart",
    ),
    path(
        "wishlist-item-to-cart/<int:wishlist_id>/",
        views.wishlist_item_to_cart,
        name="wishlist_item_to_cart",
    ),
    # checkout
    path(
        "checkout/",
        views.checkout,
        name="checkout",
    ),
    path(
        "select-payment/",
        views.select_payment,
        name="select_payment",
    ),
    path(
        "payment-successful/<str:order_id>",
        views.payment_successful,
        name="payment_successful",
    ),
    # user orders
    path(
        "orders",
        views.orders,
        name="orders",
    ),
    path(
        "order-view-details/<str:order_id>",
        views.order_details,
        name="order_view_details",
    ),
    path(
        "return-order",
        views.return_order,
        name="return_order",
    ),
    path(
        "cancel-order",
        views.cancel_order,
        name="cancel_order",
    ),
]
