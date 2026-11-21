"""Staff catalog management: menu items and categories without Django admin."""

from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .constants import CatalogFilter, MenuUnit, PageSize, RoleName
from .forms import CategoryForm, MenuItemForm
from .models import Category, MenuItem
from .pagination import paginate


def can_manage_catalog(user):
    return user.is_superuser or user.groups.filter(
        name__in=[RoleName.MANAGER, RoleName.OWNER]
    ).exists()


def catalog_required(view):
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not can_manage_catalog(request.user):
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


def _status_filter(raw):
    allowed = {value for value, _ in CatalogFilter.CHOICES}
    return raw if raw in allowed else CatalogFilter.ALL


@catalog_required
def menu_list(request):
    status = _status_filter(request.GET.get(CatalogFilter.QUERY_PARAM, CatalogFilter.ALL))
    category_id = request.GET.get("category", "").strip()
    search = request.GET.get("q", "").strip()

    items = MenuItem.objects.select_related("category").order_by("category__name", "name")
    if status == CatalogFilter.ACTIVE:
        items = items.filter(is_active=True)
    elif status == CatalogFilter.INACTIVE:
        items = items.filter(is_active=False)

    if category_id.isdigit():
        items = items.filter(category_id=int(category_id))
    else:
        category_id = ""

    if search:
        items = items.filter(Q(name__icontains=search) | Q(category__name__icontains=search))

    page_obj = paginate(request, items, per_page=PageSize.DEFAULT)
    return render(request, "sales/menu_list.html", {
        "page_obj": page_obj,
        "items": page_obj,
        "categories": Category.objects.order_by("name"),
        "status": status,
        "status_choices": CatalogFilter.CHOICES,
        "status_param": CatalogFilter.QUERY_PARAM,
        "selected_category": category_id,
        "search": search,
        "filter_all": CatalogFilter.ALL,
    })


@catalog_required
def menu_create(request):
    if request.method == "POST":
        form = MenuItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, f"Added “{item.name}” to the menu.")
            return redirect("menu_list")
    else:
        form = MenuItemForm(initial={"is_active": True, "unit": MenuUnit.PORTION})

    return render(request, "sales/menu_form.html", {
        "form": form,
        "page_title": "Add menu item",
        "submit_label": "Save item",
    })


@catalog_required
def menu_edit(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == "POST":
        form = MenuItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            messages.success(request, f"Updated “{item.name}”.")
            return redirect("menu_list")
    else:
        form = MenuItemForm(instance=item)

    return render(request, "sales/menu_form.html", {
        "form": form,
        "item": item,
        "page_title": f"Edit {item.name}",
        "submit_label": "Save changes",
    })


@catalog_required
@require_POST
def menu_toggle(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    item.is_active = not item.is_active
    item.save(update_fields=["is_active"])
    if item.is_active:
        messages.success(request, f"“{item.name}” is now available for sale.")
    else:
        messages.success(request, f"“{item.name}” is hidden from New Sale.")
    next_url = request.POST.get("next") or reverse("menu_list")
    return redirect(next_url)


@catalog_required
def category_list(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Category “{category.name}” created.")
            return redirect("category_list")
    else:
        form = CategoryForm()

    categories = (
        Category.objects.annotate(item_count=Count("items"))
        .order_by("name")
    )
    page_obj = paginate(request, categories, per_page=PageSize.DEFAULT)
    return render(request, "sales/category_list.html", {
        "form": form,
        "page_obj": page_obj,
        "categories": page_obj,
    })


@catalog_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Category renamed to “{category.name}”.")
            return redirect("category_list")
    else:
        form = CategoryForm(instance=category)

    return render(request, "sales/category_form.html", {
        "form": form,
        "category": category,
        "page_title": f"Edit category",
        "submit_label": "Save category",
    })


@catalog_required
@require_POST
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if category.items.exists():
        messages.error(
            request,
            f"Cannot delete “{category.name}” while it still has menu items. "
            "Move or hide those items first.",
        )
        return redirect("category_list")
    try:
        name = category.name
        category.delete()
        messages.success(request, f"Deleted category “{name}”.")
    except ProtectedError:
        messages.error(request, f"Cannot delete “{category.name}” because it is still in use.")
    return redirect("category_list")
