from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from core.blocks import BodyStreamBlock


@register_snippet
class ProductCategory(models.Model):
    """
    Editable product categories (e.g. Maraîchage, Volaille, Produits
    laitiers, Pisciculture...) so the catalogue structure isn't hard-coded.
    """

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(
        max_length=30,
        choices=[
            ("seedling", "Production végétale"),
            ("home", "Élevage"),
            ("water", "Pisciculture"),
            ("bolt", "Transformation"),
        ],
        default="seedling",
    )

    panels = [FieldPanel("name"), FieldPanel("slug"), FieldPanel("icon")]

    class Meta:
        verbose_name = "Catégorie de produit"
        verbose_name_plural = "Catégories de produits"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProductIndexPage(Page):
    intro = RichTextField(blank=True, features=["bold", "italic", "link"])

    content_panels = Page.content_panels + [FieldPanel("intro")]
    subpage_types = ["products.ProductPage"]
    parent_page_types = ["home.HomePage"]
    max_count = 1

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        products = self.get_children().live().specific()
        category_slug = request.GET.get("categorie")
        if category_slug:
            products = [p for p in products if p.category and p.category.slug == category_slug]
        context["products"] = products
        context["categories"] = ProductCategory.objects.all()
        context["active_category"] = category_slug
        return context

    class Meta:
        verbose_name = "Page « Nos produits »"


class ProductPage(Page):
    """
    A single product or product line. `availability` and
    `price_indication` are deliberately simple text fields, not a real
    price/stock engine: the brief asks for a showcase today with an
    e-commerce module "later"; this shape upgrades cleanly (add a real
    Product/Order app that reuses these pages) without a redesign.
    """

    AVAILABILITY_CHOICES = [
        ("available", "Disponible"),
        ("seasonal", "Saisonnier"),
        ("coming_soon", "Bientôt disponible"),
    ]

    category = models.ForeignKey(
        ProductCategory, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="products",
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    short_description = models.CharField(max_length=280)
    availability = models.CharField(
        max_length=20, choices=AVAILABILITY_CHOICES, default="available",
    )
    unit = models.CharField(
        max_length=60, blank=True,
        help_text="Ex. « kg », « sac de 50kg », « plateau de 30 œufs »",
    )
    price_indication = models.CharField(
        max_length=100, blank=True,
        help_text="Ex. « Prix sur demande », « À partir de 2 500 FCFA/kg ». "
                   "Laissez vide pour ne rien afficher.",
    )
    body = StreamField(BodyStreamBlock(), blank=True, use_json_field=True)

    search_fields = Page.search_fields + [
        index.SearchField("short_description"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("category"),
        FieldPanel("cover_image"),
        FieldPanel("short_description"),
        FieldPanel("availability"),
        FieldPanel("unit"),
        FieldPanel("price_indication"),
        FieldPanel("body"),
    ]

    parent_page_types = ["products.ProductIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
