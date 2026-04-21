from django.urls import path
from . import views

app_name = "admin_panel"

urlpatterns = [
    path("user-management/", views.user_management, name="user_management"),
    path("user-management-search/", views.user_management_search, name="user_management_search"),
    path('block-user/<pk>/',views.block_user,name='block_user')
]
