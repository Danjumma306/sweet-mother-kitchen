def roles(request):
    user = request.user
    if not user.is_authenticated:
        return {}

    names = set(user.groups.values_list("name", flat=True))
    su = user.is_superuser
    manager = su or "Manager" in names

    return {
        "nav_closing": su or "Cashier" in names or "Manager" in names,
        "nav_kitchen": su or "Kitchen" in names or "Manager" in names,
        "nav_manager": manager,
        "nav_reports": manager or "Owner" in names,
    }