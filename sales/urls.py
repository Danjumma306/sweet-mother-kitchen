from django.urls import path
from . import views

urlpatterns = [
    path("new/", views.sales_entry, name="sales_entry"),
    path("list/", views.sales_list, name="sales_list"),
    path("<int:pk>/void/", views.void_sale, name="void_sale"),
    path("report/", views.daily_report, name="daily_report"),
    path("archive/", views.report_archive, name="report_archive"),
    path("archive/export/", views.export_archive_csv, name="export_archive_csv"),
]