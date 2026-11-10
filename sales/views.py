import csv
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from .models import Category, KitchenEntry, MenuItem, Sale, SaleLine


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
    manager = "Manager" in groups or request.user.is_superuser
    owner = "Owner" in groups or request.user.is_superuser
    kitchen = "Kitchen" in groups

    # Cashiers and kitchen staff go straight to their own page
    if not (manager or owner):
        if "Cashier" in groups:
            return redirect("sales_entry")
        if kitchen:
            return redirect("kitchen_log")

    return render(request, "sales/home.html", {
        "is_manager": manager,
        "is_owner": owner,
        "is_kitchen": kitchen or manager,
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

def can_view_reports(user):
    return user.is_superuser or user.groups.filter(name__in=["Manager", "Owner"]).exists()


def report_required(view):
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not can_view_reports(request.user):
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


def day_net(day):
    """Net sales (completed sales only) for one day."""
    sales = Sale.objects.filter(date=day, status=Sale.Status.COMPLETED).prefetch_related("lines")
    return sum(s.gross_total for s in sales)


@report_required
def daily_report(request):
    day = parse_date(request.GET.get("date", "")) or date.today()
    sales = list(
        Sale.objects.filter(date=day)
        .select_related("cashier", "approved_by")
        .prefetch_related("lines__item__category")
        .order_by("created_at")
    )
    completed = [s for s in sales if s.status == Sale.Status.COMPLETED]
    voided = [s for s in sales if s.status == Sale.Status.VOIDED]

    gross = sum(s.gross_total for s in sales)
    voided_total = sum(s.gross_total for s in voided)
    net = gross - voided_total

    payments = {
        value: {"label": label, "count": 0, "total": Decimal("0")}
        for value, label in Sale.PaymentMethod.choices
    }
    categories = defaultdict(lambda: Decimal("0"))
    items = defaultdict(lambda: {"qty": 0, "revenue": Decimal("0")})

    for sale in completed:
        payments[sale.payment_method]["count"] += 1
        payments[sale.payment_method]["total"] += sale.gross_total
        for line in sale.lines.all():
            categories[line.item.category.name] += line.line_total
            items[line.item.name]["qty"] += line.quantity
            items[line.item.name]["revenue"] += line.line_total

    best_sellers = sorted(items.items(), key=lambda pair: pair[1]["qty"], reverse=True)[:5]
    category_rows = sorted(categories.items(), key=lambda pair: pair[1], reverse=True)

    prev_day = day - timedelta(days=1)
    prev_net = day_net(prev_day)
    change_pct = ((net - prev_net) / prev_net * 100) if prev_net else None

    return render(request, "sales/daily_report.html", {
        "day": day,
        "gross": gross,
        "voided_total": voided_total,
        "net": net,
        "sale_count": len(completed),
        "voided": voided,
        "payments": list(payments.values()),
        "category_rows": category_rows,
        "best_sellers": best_sellers,
        "prev_day": prev_day,
        "prev_net": prev_net,
        "change_pct": change_pct,
        "has_sales": bool(sales),
    })

def archive_range(request):
    today = date.today()
    start = parse_date(request.GET.get("start", "")) or today - timedelta(days=29)
    end = parse_date(request.GET.get("end", "")) or today
    if start > end:
        start, end = end, start
    return start, end


def day_summaries(start, end):
    """One summary row per day that has sales, newest first."""
    sales = Sale.objects.filter(date__range=(start, end)).prefetch_related("lines")
    days = {}
    for sale in sales:
        row = days.setdefault(sale.date, {
            "date": sale.date,
            "completed": 0,
            "gross": Decimal("0"),
            "voids": Decimal("0"),
            "cash": Decimal("0"),
            "momo": Decimal("0"),
            "card": Decimal("0"),
        })
        total = sale.gross_total
        row["gross"] += total
        if sale.status == Sale.Status.VOIDED:
            row["voids"] += total
        else:
            row["completed"] += 1
            row[sale.payment_method.lower()] += total

    rows = sorted(days.values(), key=lambda r: r["date"], reverse=True)
    for row in rows:
        row["net"] = row["gross"] - row["voids"]
    return rows


@report_required
def report_archive(request):
    start, end = archive_range(request)
    rows = day_summaries(start, end)
    return render(request, "sales/report_archive.html", {
        "start": start,
        "end": end,
        "rows": rows,
        "day_count": len(rows),
        "total_net": sum(r["net"] for r in rows),
    })


@report_required
def export_archive_csv(request):
    start, end = archive_range(request)
    rows = day_summaries(start, end)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="sales_{start}_to_{end}.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "Date", "Completed sales", "Gross", "Voids", "Net",
        "Cash", "Mobile Money", "Card",
    ])
    for r in reversed(rows):  # oldest first in the file
        writer.writerow([
            r["date"].isoformat(), r["completed"],
            f"{r['gross']:.2f}", f"{r['voids']:.2f}", f"{r['net']:.2f}",
            f"{r['cash']:.2f}", f"{r['momo']:.2f}", f"{r['card']:.2f}",
        ])
    return response

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
    items = (
        MenuItem.objects.filter(is_active=True)
        .select_related("category")
        .order_by("category__name", "name")
    )

    if request.method == "POST":
        saved = 0
        with transaction.atomic():
            for item in items:
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
        messages.success(request, f"Saved {saved} item{'s' if saved != 1 else ''} for today.")
        return redirect("kitchen_log")

    existing = {e.item_id: e for e in KitchenEntry.objects.filter(date=today)}
    groups = {}
    for item in items:
        entry = existing.get(item.id)
        groups.setdefault(item.category.name, []).append({
            "item": item,
            "qty": entry.quantity_prepared if entry else "",
        })

    return render(request, "sales/kitchen_log.html", {
        "today": today,
        "groups": list(groups.items()),
    })