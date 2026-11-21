"""Template helpers compatible with Django 5.0."""

from django import template

from sales.constants import PageSize

register = template.Library()


@register.simple_tag(takes_context=True)
def page_query(context, page_number):
    """Build a query string that keeps current GET params and sets page=N."""
    request = context.get("request")
    if request is None:
        return f"{PageSize.QUERY_PARAM}={page_number}"
    params = request.GET.copy()
    params[PageSize.QUERY_PARAM] = str(page_number)
    return params.urlencode()
