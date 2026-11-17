from .constants import Brand, NavItem, URL_TO_NAV
from .models import Sale


def roles(request):
    user = request.user
    if not user.is_authenticated:
        return {
            "brand_name": Brand.NAME,
            "brand_location": Brand.LOCATION,
        }

    names = set(user.groups.values_list("name", flat=True))
    su = user.is_superuser
    manager = su or "Manager" in names

    active_nav = ""
    if getattr(request, "resolver_match", None):
        active_nav = URL_TO_NAV.get(request.resolver_match.url_name, "")

    return {
        "nav_closing": su or "Cashier" in names or "Manager" in names,
        "nav_kitchen": su or "Kitchen" in names or "Manager" in names,
        "nav_manager": manager,
        "nav_reports": manager or "Owner" in names,
        "nav_item": NavItem,
        "active_nav": active_nav,
        "brand_name": Brand.NAME,
        "brand_location": Brand.LOCATION,
        "display_name": user.get_full_name() or user.username,
        "sale_status": Sale.Status,
        "payment_method": Sale.PaymentMethod,
    }
