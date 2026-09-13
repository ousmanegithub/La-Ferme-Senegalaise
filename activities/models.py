from django.db import models

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index

from core.blocks import BodyStreamBlock

ACTIVITY_ICON_CHOICES = [
    ("seedling", "Production végétale"),
    ("home", "Production animale / élevage"),
    ("water", "Pisciculture"),
    ("bolt", "Transformation agroalimentaire"),
    ("handshake", "Commercialisation"),
    ("shield", "Prestations de services"),
]


class ActivityIndexPage(Page):
    """Landing page listing every activity ("Nos activités")."""

    intro = RichTextField(blank=True, features=["bold", "italic", "link"])

    content_panels = Page.content_panels + [FieldPanel("intro")]
    subpage_types = ["activities.ActivityPage"]
    parent_page_types = ["home.HomePage"]
    max_count = 1

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["activities"] = self.get_children().live().specific()
        return context

    class Meta:
        verbose_name = "Page « Nos activités »"


class ActivityPage(Page):
    """
    One activity/métier: production végétale, élevage, pisciculture,
    transformation, commercialisation, prestations de services...
    """

    icon = models.CharField(max_length=30, choices=ACTIVITY_ICON_CHOICES, default="seedling")
    summary = models.CharField(
        max_length=280,
        help_text="Résumé affiché sur la vignette de la page « Nos activités ».",
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    body = StreamField(BodyStreamBlock(), blank=True, use_json_field=True)

    search_fields = Page.search_fields + [
        index.SearchField("summary"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("icon"),
        FieldPanel("summary"),
        FieldPanel("cover_image"),
        FieldPanel("body"),
        InlinePanel("gallery_images", label="Images de la galerie"),
    ]

    parent_page_types = ["activities.ActivityIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Activité"
        verbose_name_plural = "Activités"


class ActivityGalleryImage(Orderable):
    page = ParentalKey(ActivityPage, on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+",
    )
    caption = models.CharField(max_length=255, blank=True)

    panels = [FieldPanel("image"), FieldPanel("caption")]
