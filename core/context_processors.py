from django.conf import settings

from core.models import SiteSettings


def site_settings(request):
    """
    Makes SiteSettings (editor-managed) and a couple of read-only env-driven
    settings available in every template, without every view fetching them.
    """
    return {
        "site_settings": SiteSettings.for_request(request),
        "GA4_MEASUREMENT_ID": getattr(settings, "GA4_MEASUREMENT_ID", ""),
        "GOOGLE_SITE_VERIFICATION": getattr(settings, "GOOGLE_SITE_VERIFICATION", ""),
    }
