from django.urls import path
from . import views

urlpatterns = [
    path("new/", views.sales_entry, name="sales_entry"),
]