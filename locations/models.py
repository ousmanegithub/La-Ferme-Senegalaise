from django.db import models

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page

LOCATION_TYPE_CHOICES = [
    ("exploitation", "Exploitation / ferme"),
    ("point_de_vente", "Point de vente"),
    ("distribution", "Centre de distribution"),
    ("siege", "Siège social"),
]


class LocationsPage(Page):
    """Map + list of farms, points of sale and distribution centres."""

    intro = RichTextField(blank=True, features=["bold", "italic", "link"])

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        InlinePanel("locations", label="Sites"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = []
    max_count = 1

    class Meta:
        verbose_name = "Page « Points de vente »"


class Location(Orderable):
    page = ParentalKey(LocationsPage, on_delete=models.CASCADE, related_name="locations")
    name = models.CharField(max_length=150)
    location_type = models.CharField(
        max_length=20, choices=LOCATION_TYPE_CHOICES, default="point_de_vente",
    )
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100, default="Dakar")
    phone = models.CharField(max_length=30, blank=True)
    opening_hours = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    panels = [
        FieldPanel("name"),
        FieldPanel("location_type"),
        FieldPanel("address"),
        FieldPanel("city"),
        FieldPanel("phone"),
        FieldPanel("opening_hours"),
        FieldPanel("latitude"),
        FieldPanel("longitude"),
    ]

    class Meta:
        verbose_name = "Site"
