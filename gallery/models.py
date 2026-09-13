from django.db import models

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page

GALLERY_CATEGORY_CHOICES = [
    ("exploitations", "Nos exploitations"),
    ("activites", "Nos activités"),
    ("realisations", "Nos réalisations"),
    ("evenements", "Événements"),
]


class GalleryPage(Page):
    """
    Single "Galerie" page: photos and videos of the farms, activities and
    achievements, filterable by category (cahier des charges §32).
    """

    intro = RichTextField(blank=True, features=["bold", "italic", "link"])

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        InlinePanel("images", label="Photos"),
        InlinePanel("videos", label="Vidéos"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = []
    max_count = 1

    class Meta:
        verbose_name = "Page « Galerie »"


class GalleryImage(Orderable):
    page = ParentalKey(GalleryPage, on_delete=models.CASCADE, related_name="images")
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+",
    )
    caption = models.CharField(max_length=255, blank=True)
    category = models.CharField(
        max_length=20, choices=GALLERY_CATEGORY_CHOICES, default="exploitations",
    )

    panels = [FieldPanel("image"), FieldPanel("caption"), FieldPanel("category")]


class GalleryVideo(Orderable):
    page = ParentalKey(GalleryPage, on_delete=models.CASCADE, related_name="videos")
    thumbnail = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+",
    )
    title = models.CharField(max_length=150, blank=True)
    embed_url = models.URLField(help_text="Lien YouTube / Vimeo de la vidéo.")
    category = models.CharField(
        max_length=20, choices=GALLERY_CATEGORY_CHOICES, default="activites",
    )

    panels = [
        FieldPanel("thumbnail"),
        FieldPanel("title"),
        FieldPanel("embed_url"),
        FieldPanel("category"),
    ]
