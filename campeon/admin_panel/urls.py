from django.urls import path
from . import views

app_name = "admin_panel"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("users/", views.users, name="users"),
    path("user-management-search/", views.user_management_search, name="user_management_search"),
    path('block-user/<pk>/',views.block_user,name='block_user')
]
