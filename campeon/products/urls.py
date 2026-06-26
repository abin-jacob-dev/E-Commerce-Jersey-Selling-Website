from django.urls import path
from . import views

# from .offer_service import variant_price

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
        "wishlist-item-to-cart/<int:variant_id>/",
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
        "verify-payment/",
        views.verify_payment,
        name="verify_payment",
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
    path(
        "payment-failed/<str:order_id>",
        views.payment_failed,
        name="payment_failed",
    ),
    # user orders
    path(
        "orders",
        views.orders,
        name="orders",
    ),
    path(
        "order-details/<str:order_id>",
        views.order_details,
        name="order_details",
    ),
    path(
        "return-order-item/<int:item_id>/",
        views.return_order_item,
        name="return_order_item",
    ),
    path(
        "return-order-item-request/<int:item_id>/",
        views.return_order_item_request,
        name="return_order_item_request",
    ),
    path(
        "cancel-order-item/<int:item_id>/",
        views.cancel_order_item,
        name="cancel_order_item",
    ),
    path(
        "cancel-order-item-request/<int:item_id>/",
        views.cancel_order_item_request,
        name="cancel_order_item_request",
    ),

    path(
        "download-invoice/<str:order_id>/",
        views.download_invoice,
        name="download_invoice",
    ),
    # admin panel side
    path(
        "all-orders",
        views.all_orders,
        name="all_orders",
    ),
    path(
        "order-view/<str:order_id>",
        views.order_view,
        name="order_view",
    ),
    # ---------------------------------coupons ------------------------------------------
    # admin side
    path(
        "coupons/",
        views.coupons,
        name="coupons",
    ),
    path(
        "add-coupon/",
        views.add_coupon,
        name="add_coupon",
    ),
    path(
        "edit-coupon/<int:id>",
        views.edit_coupon,
        name="edit_coupon",
    ),
    path(
        "delete-coupon/<int:id>",
        views.delete_coupon,
        name="delete_coupon",
    ),
    # userside
    path(
        "apply-coupon/",
        views.apply_coupon,
        name="apply_coupon",
    ),
    path(
        "remove-coupon/",
        views.remove_coupon,
        name="remove_coupon",
    ),
    # -------------------------------offer-------------------------
    path(
        "offers",
        views.offers,
        name="offers",
    ),
    path(
        "add-offer/",
        views.add_offer,
        name="add_offer",
    ),
    path(
        "edit-offer/<int:id>/",
        views.edit_offer,
        name="edit_offer",
    ),
    path(
        "delete-offer/<int:id>/",
        views.delete_offer,
        name="delete_offer",
    ),

    # ---------------------------Wallet-------------------------------------------------
]
