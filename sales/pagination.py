"""Shared list pagination helpers."""

from django.core.paginator import Paginator

from .constants import PageSize


def page_number_from(request):
    raw = request.POST.get(PageSize.QUERY_PARAM) or request.GET.get(PageSize.QUERY_PARAM) or "1"
    try:
        number = int(raw)
    except (TypeError, ValueError):
        return 1
    return number if number >= 1 else 1


def paginate(request, object_list, per_page=None):
    """Return a Django Page for the requested batch."""
    paginator = Paginator(object_list, per_page or PageSize.DEFAULT)
    return paginator.get_page(page_number_from(request))


def group_rows_by_category(rows):
    """Group dict rows that each include an item with a category."""
    groups = {}
    for row in rows:
        category_name = row["item"].category.name
        groups.setdefault(category_name, []).append(row)
    return list(groups.items())
