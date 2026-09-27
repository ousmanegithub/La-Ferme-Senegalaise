"""
Reusable StreamField blocks shared by every flexible page (Home, the
generic StandardPage, Activities, Partners...). Keeping them in one place
means an editor gets the same "Hero", "Chiffres clés", "Nos valeurs" etc.
building blocks everywhere instead of every app reinventing its own.
"""
from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    ListBlock,
    PageChooserBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
    URLBlock,
)
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock


class ButtonBlock(StructBlock):
    """
    An optional internal page OR an external URL, with a label. Resolve the
    final href in templates with the `resolve_button_url` template filter
    (core/templatetags/core_tags.py): `{{ button|resolve_button_url }}`.
    """

    text = CharBlock(max_length=60, label="Texte du bouton")
    page = PageChooserBlock(required=False, label="Page interne (prioritaire)")
    url = URLBlock(required=False, label="ou lien externe")
    style = ChoiceBlock(
        choices=[("primary", "Plein (primaire)"), ("secondary", "Contour (secondaire)")],
        default="primary",
        required=False,
    )

    class Meta:
        icon = "link"
        label = "Bouton"


class HeroBlock(StructBlock):
    eyebrow = CharBlock(
        required=False, max_length=80,
        label="Sur-titre",
        help_text="Petit texte au-dessus du titre, ex. « SAS créée en 2026 »",
    )
    heading = CharBlock(max_length=140, label="Titre")
    subheading = TextBlock(required=False, label="Sous-titre")
    image = ImageChooserBlock(required=False, label="Image de fond")
    buttons = ListBlock(ButtonBlock(), label="Boutons d'appel à l'action", required=False)
    overlay = ChoiceBlock(
        choices=[
            ("dark", "Sombre (texte blanc)"),
            ("brand", "Dégradé vert de marque"),
            ("light", "Clair (texte foncé)"),
        ],
        default="brand",
        required=False,
        label="Habillage",
    )

    class Meta:
        icon = "image"
        label = "Bannière (Hero)"
        template = "core/blocks/hero_block.html"


class TextSectionBlock(StructBlock):
    eyebrow = CharBlock(required=False, max_length=80, label="Sur-titre")
    heading = CharBlock(required=False, max_length=140, label="Titre")
    body = RichTextBlock(label="Texte")
    alignment = ChoiceBlock(
        choices=[("left", "Aligné à gauche"), ("center", "Centré")],
        default="left",
        required=False,
    )

    class Meta:
        icon = "doc-full"
        label = "Section de texte"
        template = "core/blocks/text_section_block.html"


class StatItemBlock(StructBlock):
    number = CharBlock(max_length=20, label="Chiffre", help_text="Ex. 12, 4500, 100%")
    label = CharBlock(max_length=100, label="Libellé")

    class Meta:
        icon = "site"


class StatsBlock(StructBlock):
    heading = CharBlock(required=False, max_length=140, label="Titre")
    stats = ListBlock(StatItemBlock(), label="Chiffres clés")

    class Meta:
        icon = "table"
        label = "Chiffres clés"
        template = "core/blocks/stats_block.html"


# Shared between ValueCardBlock and ImageTextBlock's fallback icon so both
# editor pickers stay in sync with the icon set actually defined in
# core/icons.py.
ICON_CHOICES = [
    ("leaf", "Feuille (durabilité)"),
    ("sun", "Soleil (énergie/vitalité)"),
    ("water", "Eau (pisciculture)"),
    ("shield", "Bouclier (qualité/sécurité)"),
    ("handshake", "Poignée de main (proximité/équité)"),
    ("bolt", "Éclair (réactivité)"),
    ("home", "Maison (ferme/famille)"),
    ("globe", "Globe (souveraineté alimentaire)"),
    ("seedling", "Pousse (production végétale)"),
]


class ValueCardBlock(StructBlock):
    icon = ChoiceBlock(choices=ICON_CHOICES, label="Icône")
    title = CharBlock(max_length=100, label="Titre")
    text = TextBlock(label="Description")

    class Meta:
        icon = "pick"


class ValuesBlock(StructBlock):
    eyebrow = CharBlock(required=False, max_length=80, label="Sur-titre")
    heading = CharBlock(required=False, max_length=140, label="Titre")
    cards = ListBlock(ValueCardBlock(), label="Cartes")

    class Meta:
        icon = "pick"
        label = "Nos valeurs / atouts"
        template = "core/blocks/values_block.html"


class ImageTextBlock(StructBlock):
    image = ImageChooserBlock(required=False, label="Image")
    fallback_icon = ChoiceBlock(
        choices=ICON_CHOICES,
        default="leaf",
        required=False,
        label="Icône (si aucune image n'est choisie)",
    )
    eyebrow = CharBlock(required=False, max_length=80, label="Sur-titre")
    heading = CharBlock(required=False, max_length=140, label="Titre")
    body = RichTextBlock(label="Texte")
    button = ButtonBlock(required=False)
    image_position = ChoiceBlock(
        choices=[("left", "Image à gauche"), ("right", "Image à droite")],
        default="left",
        required=False,
    )

    class Meta:
        icon = "image"
        label = "Image + texte"
        template = "core/blocks/image_text_block.html"


class CTABlock(StructBlock):
    heading = CharBlock(max_length=140, label="Titre")
    text = TextBlock(required=False, label="Texte")
    buttons = ListBlock(ButtonBlock(), label="Boutons")
    style = ChoiceBlock(
        choices=[("brand", "Fond vert de marque"), ("dark", "Fond sombre (terre)")],
        default="brand",
        required=False,
    )

    class Meta:
        icon = "plus"
        label = "Appel à l'action"
        template = "core/blocks/cta_block.html"


class TimelineItemBlock(StructBlock):
    year = CharBlock(max_length=20, label="Année / date")
    text = TextBlock(label="Description")

    class Meta:
        icon = "date"


class TimelineBlock(StructBlock):
    heading = CharBlock(required=False, max_length=140, label="Titre")
    items = ListBlock(TimelineItemBlock(), label="Étapes")

    class Meta:
        icon = "history"
        label = "Frise chronologique"
        template = "core/blocks/timeline_block.html"


class TestimonialItemBlock(StructBlock):
    quote = TextBlock(label="Citation")
    author = CharBlock(max_length=100, label="Nom")
    role = CharBlock(required=False, max_length=140, label="Fonction / structure")
    photo = ImageChooserBlock(required=False, label="Photo")

    class Meta:
        icon = "openquote"


class TestimonialsBlock(StructBlock):
    heading = CharBlock(required=False, max_length=140, label="Titre")
    items = ListBlock(TestimonialItemBlock(), label="Témoignages")

    class Meta:
        icon = "openquote"
        label = "Témoignages"
        template = "core/blocks/testimonials_block.html"


class LogoCloudBlock(StructBlock):
    heading = CharBlock(required=False, max_length=140, label="Titre")
    logos = ListBlock(ImageChooserBlock(), label="Logos")

    class Meta:
        icon = "grip"
        label = "Logos partenaires / certifications"
        template = "core/blocks/logo_cloud_block.html"


class GalleryPreviewBlock(StructBlock):
    heading = CharBlock(required=False, max_length=140, label="Titre")
    images = ListBlock(ImageChooserBlock(), label="Images")
    link_page = PageChooserBlock(required=False, label="Voir toute la galerie (page)")

    class Meta:
        icon = "image"
        label = "Aperçu galerie"
        template = "core/blocks/gallery_preview_block.html"


class DocumentListBlock(StructBlock):
    heading = CharBlock(required=False, max_length=140, label="Titre")
    documents = ListBlock(DocumentChooserBlock(), label="Documents")

    class Meta:
        icon = "download"
        label = "Documents à télécharger"
        template = "core/blocks/document_list_block.html"


class VideoEmbedBlock(StructBlock):
    heading = CharBlock(required=False, max_length=140, label="Titre")
    embed = EmbedBlock(label="Lien vidéo (YouTube, Vimeo...)")

    class Meta:
        icon = "media"
        label = "Vidéo"
        template = "core/blocks/video_embed_block.html"


class BodyStreamBlock(StreamBlock):
    """The full palette of content blocks available on flexible pages."""

    hero = HeroBlock()
    text = TextSectionBlock()
    image_text = ImageTextBlock()
    stats = StatsBlock()
    values = ValuesBlock()
    timeline = TimelineBlock()
    testimonials = TestimonialsBlock()
    logo_cloud = LogoCloudBlock()
    gallery_preview = GalleryPreviewBlock()
    documents = DocumentListBlock()
    video = VideoEmbedBlock()
    cta = CTABlock()
