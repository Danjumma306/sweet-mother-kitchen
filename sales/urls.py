from django.urls import path
from . import views

urlpatterns = [
    path("new/", views.sales_entry, name="sales_entry"),
    path("list/", views.sales_list, name="sales_list"),
    path("<int:pk>/void/", views.void_sale, name="void_sale"),
    path("report/", views.daily_report, name="daily_report"),
    path("archive/", views.report_archive, name="report_archive"),
    path("archive/export/", views.export_archive_csv, name="export_archive_csv"),
    path("kitchen/", views.kitchen_log, name="kitchen_log"),
    path("closing/", views.shop_closing, name="shop_closing"),
    path("menu/", views.menu_list, name="menu_list"),
    path("menu/new/", views.menu_create, name="menu_create"),
    path("menu/<int:pk>/edit/", views.menu_edit, name="menu_edit"),
    path("menu/<int:pk>/toggle/", views.menu_toggle, name="menu_toggle"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/<int:pk>/edit/", views.category_edit, name="category_edit"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
]