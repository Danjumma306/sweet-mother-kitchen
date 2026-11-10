from datetime import date
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from .models import Category, MenuItem, Sale, SaleLine


@login_required
def sales_entry(request):
    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        item_ids = request.POST.getlist("item")
        quantities = request.POST.getlist("quantity")

        valid_methods = [value for value, _ in Sale.PaymentMethod.choices]
        if payment_method not in valid_methods:
            messages.error(request, "Please choose a payment method.")
            return redirect("sales_entry")

        # Collect the lines that have an item and a quantity of at least 1
        wanted = []
        for item_id, qty in zip(item_ids, quantities):
            if not item_id:
                continue
            try:
                qty = int(qty)
            except ValueError:
                continue
            if qty >= 1:
                wanted.append((item_id, qty))

        items = MenuItem.objects.filter(
            is_active=True, id__in=[item_id for item_id, _ in wanted]
        )
        item_map = {str(item.id): item for item in items}
        valid_lines = [(item_map[i], q) for i, q in wanted if i in item_map]

        if not valid_lines:
            messages.error(request, "Add at least one item with a quantity.")
            return redirect("sales_entry")

        with transaction.atomic():
            sale = Sale.objects.create(
                cashier=request.user, payment_method=payment_method
            )
            for item, qty in valid_lines:
                SaleLine.objects.create(
                    sale=sale,
                    item=item,
                    quantity=qty,
                    unit_price=item.price,  # price taken from the database, not the browser
                )

        messages.success(request, f"Sale #{sale.pk} saved. Total: GH₵ {sale.net_total:.2f}")
        return redirect("sales_entry")

    categories = Category.objects.prefetch_related(
        Prefetch(
            "items",
            queryset=MenuItem.objects.filter(is_active=True).order_by("name"),
            to_attr="active_items",
        )
    ).order_by("name")

    return render(request, "sales/sales_entry.html", {
        "categories": categories,
        "payment_methods": Sale.PaymentMethod.choices,
    })


@login_required
def home(request):
    groups = set(request.user.groups.values_list("name", flat=True))
    is_manager = "Manager" in groups or request.user.is_superuser
    is_owner = "Owner" in groups or request.user.is_superuser

    # A cashier who is not also a manager or owner goes straight to the sales form
    if "Cashier" in groups and not (is_manager or is_owner):
        return redirect("sales_entry")

    return render(request, "sales/home.html", {
        "is_manager": is_manager,
        "is_owner": is_owner,
    })

def is_manager(user):
        return user.is_superuser or user.groups.filter(name="Manager").exists()


def manager_required(view):
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not is_manager(request.user):
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


@manager_required
def sales_list(request):
    day = parse_date(request.GET.get("date", "")) or date.today()
    sales = list(
        Sale.objects.filter(date=day)
        .select_related("cashier", "approved_by")
        .prefetch_related("lines__item")
        .order_by("-created_at")
    )
    completed = [s for s in sales if s.status == Sale.Status.COMPLETED]
    return render(request, "sales/sales_list.html", {
        "day": day,
        "sales": sales,
        "day_total": sum(s.gross_total for s in completed),
        "completed_count": len(completed),
    })


@manager_required
@require_POST
def void_sale(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    reason = request.POST.get("void_reason", "").strip()

    if sale.status == Sale.Status.VOIDED:
        messages.error(request, f"Sale #{sale.pk} is already voided.")
    elif not reason:
        messages.error(request, "Please enter a reason to void a sale.")
    else:
        sale.status = Sale.Status.VOIDED
        sale.void_reason = reason[:200]
        sale.approved_by = request.user
        sale.save()
        messages.success(request, f"Sale #{sale.pk} voided.")

    return redirect(f"{reverse('sales_list')}?date={sale.date.isoformat()}")