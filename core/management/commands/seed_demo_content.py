"""
Populate the page tree with the site's real structure and the narrative
content already present in the cahier des charges (mission, values, legal
object, target audiences). Deliberately does NOT invent facts the brief
doesn't provide — no fabricated statistics, testimonials, store addresses,
prices or press articles. Where the client needs to supply something real
(legal registration numbers, coordinates, photography...) the seeded
content says so explicitly rather than making something up.

Safe to re-run: every page/setting is get_or_create'd by slug.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from wagtail.models import Locale, Page, Site

from activities.models import ActivityIndexPage, ActivityPage
from contact.models import ContactFormField, ContactPage
from core.models import SiteSettings
from gallery.models import GalleryPage
from home.models import HomePage
from locations.models import LocationsPage
from news.models import NewsIndexPage
from pages.models import StandardPage
from products.models import ProductCategory, ProductIndexPage, ProductPage


def rich(*paragraphs):
    return "".join(f"<p>{p}</p>" for p in paragraphs)


class Command(BaseCommand):
    help = "Seed the page tree and site settings with the brief's real content."

    @transaction.atomic
    def handle(self, *args, **options):
        home = HomePage.objects.first()
        if home is None:
            self.stderr.write("No HomePage found — run migrate first.")
            return

        home.title = "Accueil"
        home.draft_title = "Accueil"
        home.seo_title = "La Ferme Sénégalaise — Agriculture, élevage et pisciculture intégrés"
        home.search_description = (
            "SAS agricole sénégalaise intégrant production végétale, élevage, "
            "pisciculture et transformation agroalimentaire au service de la "
            "souveraineté alimentaire du Sénégal."
        )
        home.body = self.home_body()
        home.save()

        about = self.get_or_create_child(
            home, StandardPage, "qui-sommes-nous", "Qui sommes-nous",
            intro=(
                "Une entreprise agricole intégrée, fondée en 2026, au service "
                "de la souveraineté alimentaire du Sénégal."
            ),
            body=self.about_body(),
            show_in_menus=True,
        )

        activity_index = self.get_or_create_child(
            home, ActivityIndexPage, "nos-activites", "Nos activités",
            intro=rich(
                "La Ferme Sénégalaise développe des activités intégrées couvrant la "
                "production agricole, la transformation agroalimentaire, la "
                "valorisation des produits locaux ainsi que leur distribution."
            ),
            show_in_menus=True,
        )
        self.seed_activities(activity_index)

        product_index = self.get_or_create_child(
            home, ProductIndexPage, "nos-produits", "Nos produits",
            intro=rich(
                "Un catalogue construit autour de nos cinq filières — mis à jour au "
                "fil de la montée en production de nos exploitations."
            ),
            show_in_menus=True,
        )
        self.seed_products(product_index)

        self.get_or_create_child(
            home, GalleryPage, "galerie", "Galerie",
            intro=rich(
                "Photos et vidéos de nos exploitations, de nos activités et de nos "
                "réalisations — cette galerie sera enrichie au fil de nos reportages "
                "terrain."
            ),
            show_in_menus=True,
        )

        self.get_or_create_child(
            home, LocationsPage, "points-de-vente", "Points de vente",
            intro=rich(
                "Retrouvez nos exploitations et nos points de vente et de "
                "distribution près de chez vous."
            ),
            show_in_menus=True,
        )

        self.get_or_create_child(
            home, NewsIndexPage, "actualites", "Actualités",
            intro=rich(
                "Nouveautés, événements et campagnes de La Ferme Sénégalaise."
            ),
            show_in_menus=True,
        )

        self.get_or_create_child(
            home, StandardPage, "partenaires-et-investisseurs",
            "Partenaires & investisseurs",
            intro=(
                "Une vitrine de nos réalisations, de nos capacités de production et "
                "de nos engagements qualité, pour nos partenaires institutionnels, "
                "financiers et commerciaux."
            ),
            body=self.partners_body(),
            show_in_menus=False,
        )

        self.get_or_create_child(
            home, StandardPage, "ressources", "Ressources",
            intro=(
                "Brochures, catalogues et documents de présentation de "
                "La Ferme Sénégalaise."
            ),
            body=[
                {"type": "documents", "value": {"heading": "Documents à télécharger", "documents": []}},
            ],
            show_in_menus=False,
        )

        legal_notice = self.get_or_create_child(
            home, StandardPage, "mentions-legales", "Mentions légales",
            body=self.legal_notice_body(),
            show_in_menus=False,
        )
        privacy_policy = self.get_or_create_child(
            home, StandardPage, "politique-de-confidentialite",
            "Politique de confidentialité",
            body=self.privacy_policy_body(),
            show_in_menus=False,
        )

        contact_page = self.seed_contact_page(home)

        # --- Site settings -------------------------------------------------
        site = Site.objects.filter(is_default_site=True).first()
        if site:
            site.site_name = "La Ferme Sénégalaise"
            site.save()

        settings_obj, _ = SiteSettings.objects.get_or_create(site=site)
        settings_obj.city = settings_obj.city or "Dakar, Sénégal"
        settings_obj.footer_about_text = settings_obj.footer_about_text or rich(
            "Production végétale, élevage, pisciculture, transformation "
            "agroalimentaire et distribution — une agriculture intégrée au "
            "service de la souveraineté alimentaire du Sénégal."
        )
        settings_obj.legal_notice_page = legal_notice
        settings_obj.privacy_policy_page = privacy_policy
        settings_obj.save()

        self.stdout.write(self.style.SUCCESS(
            "Contenu de démonstration créé : pages, catégories, réglages du site.\n"
            "Rappel : coordonnées, photos, points de vente, numéros d'immatriculation "
            "et articles d'actualité restent à compléter dans l'admin Wagtail "
            "(/admin/) avant la mise en ligne — voir README."
        ))
        if contact_page:
            self.stdout.write(f"Page Contact : /{contact_page.slug}/")

    # ------------------------------------------------------------------
    def get_or_create_child(self, parent, model, slug, title, show_in_menus=False, **fields):
        existing = model.objects.child_of(parent).filter(slug=slug).first()
        if existing:
            return existing
        page = model(
            title=title, slug=slug, show_in_menus=show_in_menus,
            locale=Locale.get_default(), **fields,
        )
        parent.add_child(instance=page)
        page.save_revision().publish()
        return page

    # ------------------------------------------------------------------
    def home_body(self):
        return [
            {
                "type": "hero",
                "value": {
                    "eyebrow": "SAS agricole intégrée · Sénégal · Fondée en 2026",
                    "heading": "Nourrir l'Humanité en toute humanité",
                    "subheading": (
                        "Production agricole, élevage, pisciculture et "
                        "transformation agroalimentaire, au service de la "
                        "souveraineté alimentaire du Sénégal."
                    ),
                    "image": None,
                    "overlay": "brand",
                    "buttons": [
                        {"text": "Découvrir nos activités", "page": None, "url": "/nos-activites/", "style": "primary"},
                        {"text": "Nous contacter", "page": None, "url": "/contact/", "style": "secondary"},
                    ],
                },
            },
            {
                "type": "text",
                "value": {
                    "eyebrow": "Notre mission",
                    "heading": "Une agriculture intégrée, moderne et durable",
                    "alignment": "left",
                    "body": rich(
                        "La Ferme Sénégalaise est une entreprise agricole créée avec "
                        "l'ambition de contribuer durablement à la souveraineté "
                        "alimentaire du Sénégal, tout en promouvant un modèle de "
                        "production respectueux des principes du développement durable.",
                        "Nos activités intégrées couvrent la production agricole, la "
                        "transformation agroalimentaire, la valorisation des produits "
                        "locaux ainsi que leur distribution — pour répondre aux besoins "
                        "des ménages tout en soutenant les filières agricoles nationales.",
                    ),
                },
            },
            {
                "type": "values",
                "value": {
                    "eyebrow": "Nos valeurs",
                    "heading": "Ce qui guide chacune de nos décisions",
                    "cards": [
                        {"icon": "handshake", "title": "Proximité", "text": "Un réseau de points de service accessibles, fiables et adaptés aux réalités urbaines, pour rapprocher durablement le producteur du consommateur."},
                        {"icon": "bolt", "title": "Réactivité", "text": "Une organisation entrepreneuriale rigoureuse, capable de répondre efficacement aux besoins croissants des ménages et de nos partenaires."},
                        {"icon": "shield", "title": "Équité", "text": "Une alimentation de qualité à des prix justes, et des pratiques génératrices d'emplois et de revenus pour l'ensemble de la chaîne de valeur."},
                        {"icon": "globe", "title": "Responsabilité", "text": "Le respect des normes d'hygiène, de sécurité sanitaire et de qualité, au service de la résilience des systèmes alimentaires nationaux."},
                    ],
                },
            },
            {
                "type": "stats",
                "value": {
                    "heading": "La Ferme Sénégalaise en un coup d'œil",
                    "stats": [
                        {"number": "2026", "label": "Année de création"},
                        {"number": "5", "label": "Filières d'activité intégrées"},
                        {"number": "SAS", "label": "Statut juridique"},
                        {"number": "Sénégal", "label": "Opérations au Sénégal et à l'international"},
                    ],
                },
            },
            {
                "type": "image_text",
                "value": {
                    "image": None,
                    "fallback_icon": "seedling",
                    "eyebrow": "Nos activités",
                    "heading": "De la production à la distribution",
                    "body": rich(
                        "Production végétale, production animale, transformation "
                        "agroalimentaire, commercialisation et prestations de "
                        "services : cinq filières pensées pour créer de la valeur à "
                        "chaque étape, du champ à l'assiette."
                    ),
                    "button": {"text": "Voir toutes nos activités", "page": None, "url": "/nos-activites/", "style": "primary"},
                    "image_position": "left",
                },
            },
            {
                "type": "image_text",
                "value": {
                    "image": None,
                    "fallback_icon": "leaf",
                    "eyebrow": "Nos produits",
                    "heading": "Des produits sains, accessibles et de qualité",
                    "body": rich(
                        "Notre catalogue s'organise autour de nos filières de "
                        "production — maraîchage et céréales, élevage et volaille, "
                        "pisciculture, produits transformés — pour répondre aux "
                        "besoins des ménages comme des professionnels."
                    ),
                    "button": {"text": "Découvrir le catalogue", "page": None, "url": "/nos-produits/", "style": "primary"},
                    "image_position": "right",
                },
            },
            {
                "type": "cta",
                "value": {
                    "heading": "Devenez partenaire de La Ferme Sénégalaise",
                    "text": "Distributeurs, professionnels de l'alimentation, investisseurs ou institutions : parlons de votre projet.",
                    "style": "brand",
                    "buttons": [
                        {"text": "Nous contacter", "page": None, "url": "/contact/", "style": "primary"},
                        {"text": "Partenaires & investisseurs", "page": None, "url": "/partenaires-et-investisseurs/", "style": "secondary"},
                    ],
                },
            },
        ]

    def about_body(self):
        return [
            {
                "type": "text",
                "value": {
                    "eyebrow": "",
                    "heading": "Notre histoire",
                    "alignment": "left",
                    "body": rich(
                        "Fondée sur une vision moderne de l'agriculture et de "
                        "l'agroalimentaire, La Ferme Sénégalaise s'attache à offrir "
                        "aux consommateurs des produits sains, accessibles et de "
                        "qualité, en s'appuyant sur des valeurs fortes de proximité, "
                        "de réactivité, d'équité et de responsabilité.",
                        "Au-delà de sa vocation productive, La Ferme Sénégalaise place "
                        "le consommateur au cœur de son projet. À travers un réseau de "
                        "points de service accessibles, fiables et adaptés aux "
                        "réalités urbaines, elle entend rapprocher durablement le "
                        "producteur du consommateur et favoriser une alimentation de "
                        "qualité à des prix justes.",
                        "Portée par une démarche entrepreneuriale rigoureuse, "
                        "l'entreprise veille au respect des normes d'hygiène, de "
                        "sécurité sanitaire et de qualité, et s'engage à promouvoir "
                        "des pratiques agricoles responsables, génératrices d'emplois "
                        "et de revenus.",
                    ),
                },
            },
            {
                "type": "timeline",
                "value": {
                    "heading": "Notre feuille de route",
                    "items": [
                        {"year": "2026", "text": "Création de La Ferme Sénégalaise SAS, avec l'ambition de contribuer durablement à la souveraineté alimentaire du Sénégal."},
                    ],
                },
            },
            {
                "type": "text",
                "value": {
                    "eyebrow": "Notre objet social",
                    "heading": "Cinq filières intégrées",
                    "alignment": "left",
                    "body": rich(
                        "<strong>Production végétale</strong> — exploitation de terres "
                        "agricoles, culture de céréales, plantes oléagineuses, fruits, "
                        "légumes (maraîchage) et plantes horticoles ou industrielles.",
                        "<strong>Production animale</strong> — élevage de bétail "
                        "(bovins, ovins, caprins, porcins), aviculture, production de "
                        "lait et d'œufs, pisciculture, cuniculture et coturniculture.",
                        "<strong>Transformation agroalimentaire</strong> — "
                        "conditionnement, conservation, transformation et valorisation "
                        "des produits issus de l'exploitation.",
                        "<strong>Commercialisation</strong> — vente en gros, demi-gros "
                        "ou détail, import-export de produits agricoles, de semences, "
                        "d'engrais et de matériel agricole.",
                        "<strong>Prestations de services</strong> — services agricoles "
                        "(labour, récolte, conseils techniques) et gestion de systèmes "
                        "d'irrigation.",
                    ),
                },
            },
        ]

    def partners_body(self):
        return [
            {
                "type": "text",
                "value": {
                    "eyebrow": "",
                    "heading": "Une vitrine professionnelle pour nos partenaires",
                    "alignment": "left",
                    "body": rich(
                        "La Ferme Sénégalaise s'adresse aux distributeurs et "
                        "partenaires commerciaux, aux investisseurs et institutions "
                        "financières, aux partenaires techniques et au développement, "
                        "ainsi qu'aux administrations publiques et collectivités "
                        "territoriales.",
                        "Nous valorisons nos réalisations, nos capacités de "
                        "production et nos engagements en matière de qualité, dans "
                        "une démarche entrepreneuriale rigoureuse et transparente.",
                    ),
                },
            },
            {
                "type": "cta",
                "value": {
                    "heading": "Discutons de votre projet",
                    "text": "Notre équipe se tient à votre disposition pour toute demande de partenariat, d'investissement ou de collaboration technique.",
                    "style": "dark",
                    "buttons": [
                        {"text": "Nous contacter", "page": None, "url": "/contact/", "style": "primary"},
                    ],
                },
            },
        ]

    def legal_notice_body(self):
        return [
            {
                "type": "text",
                "value": {
                    "eyebrow": "",
                    "heading": "",
                    "alignment": "left",
                    "body": rich(
                        "<strong>Éditeur du site</strong> — La Ferme Sénégalaise SAS, "
                        "société créée en 2026, dont le siège social est situé au "
                        "Sénégal. Numéro RCCM, NINEA et adresse complète du siège : "
                        "[à compléter par l'entreprise avant la mise en ligne].",
                        "<strong>Directeur de la publication</strong> — [à compléter].",
                        "<strong>Hébergement</strong> — [nom et adresse de "
                        "l'hébergeur à compléter au moment du déploiement].",
                        "<strong>Contact</strong> — voir la page Contact du site.",
                    ),
                },
            },
        ]

    def privacy_policy_body(self):
        return [
            {
                "type": "text",
                "value": {
                    "eyebrow": "",
                    "heading": "",
                    "alignment": "left",
                    "body": rich(
                        "La Ferme Sénégalaise attache une grande importance à la "
                        "protection des données personnelles des visiteurs et clients "
                        "de ce site.",
                        "<strong>Données collectées</strong> — les informations "
                        "transmises via le formulaire de contact (nom, e-mail, "
                        "téléphone, message) et, si vous vous inscrivez, votre "
                        "adresse e-mail pour la newsletter.",
                        "<strong>Utilisation</strong> — ces données sont utilisées "
                        "exclusivement pour répondre à vos demandes et vous tenir "
                        "informé(e) de notre actualité si vous y avez consenti. Elles "
                        "ne sont ni vendues ni cédées à des tiers.",
                        "<strong>Vos droits</strong> — vous pouvez demander l'accès, "
                        "la rectification ou la suppression de vos données en nous "
                        "contactant via la page Contact.",
                        "Cette politique sera complétée avec les mentions requises "
                        "par la réglementation applicable (loi sénégalaise sur la "
                        "protection des données à caractère personnel) avant la mise "
                        "en ligne définitive.",
                    ),
                },
            },
        ]

    # ------------------------------------------------------------------
    def seed_activities(self, index_page):
        activities = [
            ("production-vegetale", "Production végétale", "seedling",
             "Exploitation de terres agricoles : céréales, plantes oléagineuses, fruits, légumes et maraîchage.",
             rich("L'exploitation de terres agricoles, la culture de céréales, de plantes oléagineuses, de fruits, de légumes (maraîchage), et de toutes plantes horticoles ou industrielles.")),
            ("production-animale", "Production animale", "home",
             "Élevage de bétail, aviculture, production de lait et d'œufs, pisciculture, cuniculture et coturniculture.",
             rich("L'élevage de bétail (bovins, ovins, caprins, porcins), l'aviculture (poulets de chair et pondeuses), ainsi que la production de lait et d'œufs, la pisciculture, la cuniculture et la coturniculture.")),
            ("transformation-agroalimentaire", "Transformation agroalimentaire", "bolt",
             "Conditionnement, conservation, transformation et valorisation des produits issus de l'exploitation.",
             rich("Le conditionnement, la conservation, la transformation et la valorisation des produits issus de l'exploitation (pressage d'huile, séchage de fruits, etc.).")),
            ("commercialisation", "Commercialisation", "handshake",
             "Vente en gros, demi-gros ou détail, import-export de produits agricoles, semences, engrais et matériel agricole.",
             rich("La vente en gros, demi-gros ou détail, l'import-export de produits agricoles, de semences, d'engrais et de matériel agricole.")),
            ("prestations-de-services", "Prestations de services", "shield",
             "Services agricoles (labour, récolte, conseils techniques) et gestion de systèmes d'irrigation.",
             rich("La fourniture de services agricoles (labour, récolte, conseils techniques) et la gestion de systèmes d'irrigation.")),
        ]
        for slug, title, icon, summary, body_text in activities:
            self.get_or_create_child(
                index_page, ActivityPage, slug, title,
                icon=icon, summary=summary,
                body=[{"type": "text", "value": {"eyebrow": "", "heading": "", "alignment": "left", "body": body_text}}],
                show_in_menus=True,
            )

    # ------------------------------------------------------------------
    def seed_products(self, index_page):
        categories = [
            ("mareaichage-cereales", "Maraîchage & céréales", "seedling"),
            ("elevage-volaille", "Élevage & volaille", "home"),
            ("pisciculture", "Pisciculture", "water"),
            ("produits-transformes", "Produits transformés", "bolt"),
        ]
        cat_objs = {}
        for slug, name, icon in categories:
            cat, _ = ProductCategory.objects.get_or_create(slug=slug, defaults={"name": name, "icon": icon})
            cat_objs[slug] = cat

        products = [
            ("riz-cereales", "Riz & céréales", "mareaichage-cereales", "Céréales issues de notre production végétale.", "kg"),
            ("legumes-frais", "Légumes frais", "mareaichage-cereales", "Légumes de maraîchage cultivés selon des pratiques responsables.", "kg"),
            ("poulet-de-chair", "Poulet de chair", "elevage-volaille", "Volaille issue de notre filière avicole.", "kg"),
            ("oeufs-frais", "Œufs frais", "elevage-volaille", "Œufs de poules pondeuses de nos exploitations.", "plateau de 30"),
            ("poisson-tilapia", "Poisson (tilapia)", "pisciculture", "Poisson d'élevage issu de notre activité de pisciculture intégrée.", "kg"),
            ("huile-vegetale", "Huile végétale", "produits-transformes", "Huile pressée à partir de nos plantes oléagineuses.", "litre"),
        ]
        for slug, title, cat_slug, desc, unit in products:
            self.get_or_create_child(
                index_page, ProductPage, slug, title,
                category=cat_objs[cat_slug],
                short_description=desc,
                availability="coming_soon",
                unit=unit,
                price_indication="Prix sur demande",
                body=[],
                show_in_menus=False,
            )

    # ------------------------------------------------------------------
    def seed_contact_page(self, home):
        existing = ContactPage.objects.child_of(home).filter(slug="contact").first()
        if existing:
            return existing

        page = ContactPage(
            title="Contact",
            slug="contact",
            show_in_menus=True,
            intro=rich(
                "Une question sur nos produits, un projet de partenariat ou une "
                "demande d'information ? Écrivez-nous."
            ),
            thank_you_text=rich(
                "Merci, votre message a bien été envoyé. Notre équipe vous "
                "répondra dans les meilleurs délais."
            ),
            from_address="",
            to_address="",
            subject="Nouveau message — site La Ferme Sénégalaise",
        )
        home.add_child(instance=page)

        field_defs = [
            ("Nom complet", "singleline", True),
            ("E-mail", "email", True),
            ("Téléphone", "singleline", False),
            ("Sujet", "singleline", False),
            ("Message", "multiline", True),
        ]
        for i, (label, field_type, required) in enumerate(field_defs):
            ContactFormField.objects.create(
                page=page, sort_order=i, label=label,
                field_type=field_type, required=required,
            )

        page.save_revision().publish()
        return page
