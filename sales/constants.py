"""Shared UI and domain constants for Sweet Mother's Kitchen."""


class NavItem:
    OVERVIEW = "overview"
    NEW_SALE = "new_sale"
    SALES_LIST = "sales_list"
    KITCHEN_LOG = "kitchen_log"
    SHOP_CLOSING = "shop_closing"
    DAILY_REPORT = "daily_report"
    REPORT_ARCHIVE = "report_archive"
    ACCOUNT = "account"


URL_TO_NAV = {
    "home": NavItem.OVERVIEW,
    "sales_entry": NavItem.NEW_SALE,
    "sales_list": NavItem.SALES_LIST,
    "void_sale": NavItem.SALES_LIST,
    "kitchen_log": NavItem.KITCHEN_LOG,
    "shop_closing": NavItem.SHOP_CLOSING,
    "daily_report": NavItem.DAILY_REPORT,
    "report_archive": NavItem.REPORT_ARCHIVE,
    "export_archive_csv": NavItem.REPORT_ARCHIVE,
}


class Brand:
    NAME = "Sweet Mother's Kitchen"
    LOCATION = "Ayikuma, Accra"


class SidebarState:
    STORAGE_KEY = "smk_sidebar_collapsed"
    COLLAPSED = "1"
    EXPANDED = "0"


class CategoryFilter:
    ALL = "all"


class PaymentUi:
    CASH = "CASH"
    MOMO = "MOMO"
    CARD = "CARD"
