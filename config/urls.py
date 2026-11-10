from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from sales import views as sales_views

urlpatterns = [
    path("", sales_views.home, name="home"),
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("sales/", include("sales.urls")),
]