from django.contrib import admin
from .models import Category, MenuItem, Sale, SaleLine


class SaleLineInline(admin.TabularInline):
    model = SaleLine
    extra = 1


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    inlines = [SaleLineInline]
    list_display = ("id", "date", "cashier", "payment_method", "status")


admin.site.register(Category)
admin.site.register(MenuItem)