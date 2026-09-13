from django.db import models

from wagtail.admin.panels import FieldPanel, MultiFieldPanel, PageChooserPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField


@register_setting(icon="cog")
class SiteSettings(BaseSiteSetting):
    """
    Site-wide values an editor can change without a developer: contact
    details, social links and the handful of legal pages the footer always
    needs. Everything here is exposed to every template via
    core.context_processors.site_settings.
    """

    # --- Identité / contact -------------------------------------------------
    phone = models.CharField(
        max_length=30, blank=True,
        help_text="Numéro affiché dans l'en-tête et le pied de page, ex. +221 33 000 00 00",
    )
    whatsapp_number = models.CharField(
        max_length=30, blank=True,
        help_text="Numéro international sans espaces ni +, ex. 221770000000 (pour le lien WhatsApp).",
    )
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True, default="Dakar, Sénégal")
    opening_hours = models.CharField(
        max_length=255, blank=True,
        help_text="Ex. Lun–Ven : 8h–18h · Sam : 9h–13h",
    )

    # --- Réseaux sociaux -----------------------------------------------------
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)

    # --- Pied de page ----------------------------------------------------
    footer_about_text = RichTextField(
        blank=True,
        features=["bold", "italic", "link"],
        help_text="Court paragraphe de présentation affiché en pied de page.",
    )
    newsletter_intro = models.CharField(
        max_length=255, blank=True,
        default="Recevez nos actualités et nos offres directement par e-mail.",
    )
    copyright_holder = models.CharField(
        max_length=255, blank=True, default="La Ferme Sénégalaise SAS",
    )

    # --- Pages légales (liées, pas codées en dur) ---------------------------
    legal_notice_page = models.ForeignKey(
        "wagtailcore.Page", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        verbose_name="Mentions légales",
    )
    privacy_policy_page = models.ForeignKey(
        "wagtailcore.Page", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        verbose_name="Politique de confidentialité",
    )

    # --- Suivi (facultatif, laissé vide tant que le client ne fournit rien) --
    google_maps_embed_url = models.URLField(
        blank=True,
        help_text="URL d'intégration Google Maps (facultatif, sinon la carte utilise OpenStreetMap).",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("phone"),
                FieldPanel("whatsapp_number"),
                FieldPanel("email"),
                FieldPanel("address"),
                FieldPanel("city"),
                FieldPanel("opening_hours"),
            ],
            heading="Coordonnées",
        ),
        MultiFieldPanel(
            [
                FieldPanel("facebook_url"),
                FieldPanel("instagram_url"),
                FieldPanel("linkedin_url"),
                FieldPanel("youtube_url"),
                FieldPanel("tiktok_url"),
            ],
            heading="Réseaux sociaux",
        ),
        MultiFieldPanel(
            [
                FieldPanel("footer_about_text"),
                FieldPanel("newsletter_intro"),
                FieldPanel("copyright_holder"),
            ],
            heading="Pied de page",
        ),
        MultiFieldPanel(
            [
                PageChooserPanel("legal_notice_page"),
                PageChooserPanel("privacy_policy_page"),
            ],
            heading="Pages légales",
        ),
        FieldPanel("google_maps_embed_url"),
    ]

    class Meta:
        verbose_name = "Réglages du site"
