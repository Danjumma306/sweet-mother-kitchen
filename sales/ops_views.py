"""Kitchen production log and shop closing views."""

from datetime import date
from decimal import Decimal, InvalidOperation
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.shortcuts import redirect, render
from django.urls import reverse

from .constants import PageSize
from .models import CashCount, ClosingEntry, KitchenEntry, MenuItem, Sale, SaleLine
from .pagination import group_rows_by_category, paginate


def can_log_kitchen(user):
    return user.is_superuser or user.groups.filter(name__in=["Kitchen", "Manager"]).exists()


def kitchen_required(view):
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not can_log_kitchen(request.user):
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


@kitchen_required
def kitchen_log(request):
    today = date.today()
    items_qs = (
        MenuItem.objects.filter(is_active=True)
        .select_related("category")
        .order_by("category__name", "name")
    )
    page_obj = paginate(request, items_qs, per_page=PageSize.DEFAULT)
    page_items = list(page_obj.object_list)

    if request.method == "POST":
        saved = 0
        with transaction.atomic():
            for item in page_items:
                raw = request.POST.get(f"qty_{item.id}", "").strip()
                if raw == "":
                    KitchenEntry.objects.filter(date=today, item=item).delete()
                    continue
                try:
                    qty = int(raw)
                except ValueError:
                    continue
                if qty < 0:
                    continue
                KitchenEntry.objects.update_or_create(
                    date=today,
                    item=item,
                    defaults={"quantity_prepared": qty, "recorded_by": request.user},
                )
                saved += 1
        messages.success(request, f"Saved {saved} item{'s' if saved != 1 else ''} on this page.")
        return redirect(f"{reverse('kitchen_log')}?{PageSize.QUERY_PARAM}={page_obj.number}")

    existing = {
        e.item_id: e
        for e in KitchenEntry.objects.filter(date=today, item_id__in=[i.id for i in page_items])
    }
    rows = [
        {
            "item": item,
            "qty": existing[item.id].quantity_prepared if item.id in existing else "",
        }
        for item in page_items
    ]

    return render(request, "sales/kitchen_log.html", {
        "today": today,
        "groups": group_rows_by_category(rows),
        "page_obj": page_obj,
    })


def can_log_closing(user):
    return user.is_superuser or user.groups.filter(name__in=["Cashier", "Manager"]).exists()


def closing_required(view):
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not can_log_closing(request.user):
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


@closing_required
def shop_closing(request):
    today = date.today()
    items_qs = (
        MenuItem.objects.filter(is_active=True)
        .select_related("category")
        .order_by("category__name", "name")
    )
    page_obj = paginate(request, items_qs, per_page=PageSize.DEFAULT)
    page_items = list(page_obj.object_list)
    page_item_ids = [item.id for item in page_items]

    if request.method == "POST":
        cash_error = False
        with transaction.atomic():
            for item in page_items:
                raw = request.POST.get(f"left_{item.id}", "").strip()
                sold_out = f"soldout_{item.id}" in request.POST

                if raw == "" and not sold_out:
                    ClosingEntry.objects.filter(date=today, item=item).delete()
                    continue
                try:
                    left = int(raw) if raw else 0
                except ValueError:
                    continue
                if left < 0 or left > 100000:
                    continue

                ClosingEntry.objects.update_or_create(
                    date=today,
                    item=item,
                    defaults={
                        "quantity_left": left,
                        "sold_out": sold_out,
                        "recorded_by": request.user,
                    },
                )

            raw_cash = request.POST.get("cash_counted", "").strip()
            note = request.POST.get("note", "").strip()[:200]
            if raw_cash == "":
                CashCount.objects.filter(date=today).delete()
            else:
                try:
                    cash = Decimal(raw_cash)
                except InvalidOperation:
                    cash = None
                if cash is None or not cash.is_finite() or cash < 0 or cash >= Decimal("100000000"):
                    cash_error = True
                else:
                    CashCount.objects.update_or_create(
                        date=today,
                        defaults={
                            "cash_counted": cash.quantize(Decimal("0.01")),
                            "note": note,
                            "recorded_by": request.user,
                        },
                    )

        if cash_error:
            messages.error(
                request,
                "Items on this page were saved, but the cash counted is not a valid amount.",
            )
        else:
            messages.success(request, "Closing report page saved.")
        return redirect(f"{reverse('shop_closing')}?{PageSize.QUERY_PARAM}={page_obj.number}")

    sold = {
        row["item_id"]: row["total"]
        for row in SaleLine.objects.filter(
            sale__date=today,
            sale__status=Sale.Status.COMPLETED,
            item_id__in=page_item_ids,
        ).values("item_id").annotate(total=Sum("quantity"))
    }
    existing = {
        e.item_id: e
        for e in ClosingEntry.objects.filter(date=today, item_id__in=page_item_ids)
    }
    rows = [
        {
            "item": item,
            "sold": sold.get(item.id, 0),
            "left": existing[item.id].quantity_left if item.id in existing else "",
            "sold_out": existing[item.id].sold_out if item.id in existing else False,
        }
        for item in page_items
    ]

    expected_cash = SaleLine.objects.filter(
        sale__date=today,
        sale__status=Sale.Status.COMPLETED,
        sale__payment_method=Sale.PaymentMethod.CASH,
    ).aggregate(
        total=Sum(
            ExpressionWrapper(
                F("quantity") * F("unit_price"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
    )["total"] or Decimal("0")

    cash_count = CashCount.objects.filter(date=today).first()
    difference = (cash_count.cash_counted - expected_cash) if cash_count else None

    return render(request, "sales/shop_closing.html", {
        "today": today,
        "groups": group_rows_by_category(rows),
        "page_obj": page_obj,
        "expected_cash": expected_cash,
        "cash_count": cash_count,
        "difference": difference,
    })
