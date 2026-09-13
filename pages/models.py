from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from core.blocks import BodyStreamBlock


class StandardPage(Page):
    """
    A general-purpose flexible page built from the shared StreamField
    palette. Used for "Qui sommes-nous", "Partenaires & investisseurs",
    legal notices and any one-off page that doesn't need its own model.
    """

    intro = models.CharField(
        max_length=255, blank=True,
        help_text="Court chapeau affiché sous le titre (facultatif).",
    )
    body = StreamField(BodyStreamBlock(), blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    subpage_types = ["pages.StandardPage"]

    class Meta:
        verbose_name = "Page standard"
