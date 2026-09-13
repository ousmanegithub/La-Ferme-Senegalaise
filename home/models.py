from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from core.blocks import BodyStreamBlock


class HomePage(Page):
    """
    The site root. Everything below the hero is built from the shared
    StreamField palette so an editor can reorder the homepage narrative
    (chiffres clés, activités, actualités, CTA...) without a developer.
    """

    max_count = 1
    parent_page_types = ["wagtailcore.Page"]

    body = StreamField(BodyStreamBlock(), blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    class Meta:
        verbose_name = "Page d'accueil"
