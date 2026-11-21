from .constants import Brand, NavItem, RoleName, URL_TO_NAV
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
    manager = su or RoleName.MANAGER in names

    active_nav = ""
    if getattr(request, "resolver_match", None):
        active_nav = URL_TO_NAV.get(request.resolver_match.url_name, "")

    return {
        "nav_closing": su or RoleName.CASHIER in names or RoleName.MANAGER in names,
        "nav_kitchen": su or RoleName.KITCHEN in names or RoleName.MANAGER in names,
        "nav_manager": manager,
        "nav_reports": manager or RoleName.OWNER in names,
        "nav_catalog": manager or RoleName.OWNER in names,
        "nav_item": NavItem,
        "active_nav": active_nav,
        "brand_name": Brand.NAME,
        "brand_location": Brand.LOCATION,
        "display_name": user.get_full_name() or user.username,
        "sale_status": Sale.Status,
        "payment_method": Sale.PaymentMethod,
    }
