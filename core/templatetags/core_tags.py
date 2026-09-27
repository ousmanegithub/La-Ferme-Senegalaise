from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def resolve_button_url(button):
    """Given a ButtonBlock value, return the internal page URL or the external URL."""
    if not button:
        return ""
    page = button.get("page")
    if page:
        return page.url
    return button.get("url") or "#"


@register.filter
def is_active_nav_item(nav_page, request):
    """True when the current request path is on/under this nav item's page."""
    if not nav_page or not request:
        return False
    current_path = request.path
    return current_path == nav_page.url or (
        nav_page.url != "/" and current_path.startswith(nav_page.url)
    )


@register.simple_tag(takes_context=True)
def main_menu(context):
    """
    The primary navigation: live, "show in menu" pages directly under the
    site root, each with its own live/in-menu children for a dropdown.
    Editors control this entirely from the page tree, no separate
    "navigation" admin screen to keep in sync.
    """
    from wagtail.models import Site

    request = context.get("request")
    site = getattr(request, "site", None) if request else None
    if site is None:
        # request.site is only set inside Wagtail's page-serving view; on
        # other views (404s, non-Wagtail routes rendering base.html) fall
        # back to resolving it directly so the header never goes empty.
        site = Site.find_for_request(request) if request else Site.objects.filter(is_default_site=True).first()
    if site is None:
        return []
    root = site.root_page
    items = []
    for page in root.get_children().live().in_menu().specific():
        children = list(page.get_children().live().in_menu().specific())
        items.append({"page": page, "children": children})
    return items


@register.simple_tag
def breadcrumb_ancestors(page):
    """Ancestors below the site root/home (depth > 2), for breadcrumb trails."""
    if not page:
        return []
    return page.get_ancestors().filter(depth__gt=2).specific()


@register.simple_tag
def icon_svg(name, css_class=""):
    """
    Inline a brand icon by name (see core/static/core/icons.py for the set).
    Keeping icons inline (rather than an <img>) lets them inherit
    `currentColor`, so hover/theme colour changes need no extra image asset.
    """
    from core.icons import ICONS

    path = ICONS.get(name, ICONS["leaf"])
    return mark_safe(format_html(
        '<svg class="icon {}" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="1.75" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true">{}</svg>',
        css_class, mark_safe(path),
    ))
