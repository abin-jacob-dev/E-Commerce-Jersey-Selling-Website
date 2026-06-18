from django.urls import path
from . import views
from userauths.views import signin

app_name = "admin_panel"

urlpatterns = [
    
    path("", views.dashboard, name="dashboard"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("users/", views.users, name="users"),
    path(
        "user-management-search/",
        views.user_management_search,
        name="user_management_search",
    ),
    path("block-user/<id>/", views.block_user, name="block_user"),
    path("delete-user/<id>/", views.delete_user, name="delete_user"),

    path("sales/", views.sales, name="sales"),
    path("sales-report-pdf/", views.sales_report_pdf, name="sales_report_pdf"),
    path("sales-report-excel/", views.sales_report_excel, name="sales_report_excel"),

    
]
