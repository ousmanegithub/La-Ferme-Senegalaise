"""
Populate the page tree with the site's real structure and the narrative
content already present in the cahier des charges (mission, values, legal
object, target audiences). Deliberately does not invent facts the brief
doesn't provide: no fabricated statistics, testimonials, real store
addresses, prices or press articles. Where the client needs to supply
something real (legal registration numbers, real coordinates, photography
credits...) the seeded content says so explicitly rather than making
something up. The points of sale below are an explicit exception: they are
clearly-labelled fictional examples (requested to preview the map feature),
not real addresses.

Safe to re-run: every page is looked up by slug and its content refreshed
in place, so editing this file and re-running updates the site instead of
duplicating pages.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from wagtail.images.models import Image
from wagtail.models import Locale, Site

from activities.models import ActivityGalleryImage, ActivityIndexPage, ActivityPage
from contact.models import ContactFormField, ContactPage
from core.models import SiteSettings
from gallery.models import GalleryPage
from home.models import HomePage
from locations.models import LocationsPage, Location
from news.models import NewsIndexPage
from pages.models import StandardPage
from products.models import ProductCategory, ProductIndexPage, ProductPage


def rich(*paragraphs):
    return "".join(f"<p>{p}</p>" for p in paragraphs)


def img(title):
    """Look up an imported photo by title (see import_media). Returns None,
    silently, if it hasn't been imported yet, so the site still renders
    (with the icon fallback built into the relevant blocks/templates)."""
    return Image.objects.filter(title=title).first()


class Command(BaseCommand):
    help = "Seed the page tree and site settings with the brief's real content."

    @transaction.atomic
    def handle(self, *args, **options):
        home = HomePage.objects.first()
        if home is None:
            self.stderr.write("Aucune page d'accueil trouvee : lancez migrate d'abord.")
            return

        home.title = "Accueil"
        home.draft_title = "Accueil"
        home.seo_title = "La Ferme Sénégalaise : agriculture, élevage et pisciculture intégrés"
        home.search_description = (
            "SAS agricole sénégalaise intégrant production végétale, élevage, "
            "pisciculture et transformation agroalimentaire au service de la "
            "souveraineté alimentaire du Sénégal."
        )
        home.body = self.home_body()
        home.save()
        home.save_revision().publish()

        about = self.get_or_update_child(
            home, StandardPage, "qui-sommes-nous", "Qui sommes-nous",
            intro=(
                "Une entreprise agricole intégrée, fondée en 2026, au service "
                "de la souveraineté alimentaire du Sénégal."
            ),
            body=self.about_body(),
            show_in_menus=True,
        )

        activity_index = self.get_or_update_child(
            home, ActivityIndexPage, "nos-activites", "Nos activités",
            intro=rich(
                "La Ferme Sénégalaise développe des activités intégrées couvrant la "
                "production agricole, la transformation agroalimentaire, la "
                "valorisation des produits locaux ainsi que leur distribution."
            ),
            show_in_menus=True,
        )
        self.seed_activities(activity_index)

        product_index = self.get_or_update_child(
            home, ProductIndexPage, "nos-produits", "Nos produits",
            intro=rich(
                "Un catalogue construit autour de nos cinq filières, mis à jour au "
                "fil de la montée en production de nos exploitations."
            ),
            show_in_menus=True,
        )
        self.seed_products(product_index)

        self.get_or_update_child(
            home, GalleryPage, "galerie", "Galerie",
            intro=rich(
                "Photos et vidéos de nos exploitations, de nos activités et de nos "
                "réalisations. Cette galerie sera enrichie au fil de nos reportages "
                "terrain."
            ),
            show_in_menus=True,
        )

        locations_page = self.get_or_update_child(
            home, LocationsPage, "points-de-vente", "Points de vente",
            intro=rich(
                "Retrouvez nos exploitations et nos points de vente et de "
                "distribution près de chez vous.",
                "<em>Les sites ci-dessous sont des exemples fictifs, positionnés "
                "autour de Dakar pour illustrer la carte : ils seront remplacés "
                "par nos adresses réelles avant la mise en ligne.</em>",
            ),
            show_in_menus=True,
        )
        self.seed_locations(locations_page)

        self.get_or_update_child(
            home, NewsIndexPage, "actualites", "Actualités",
            intro=rich(
                "Nouveautés, événements et campagnes de La Ferme Sénégalaise."
            ),
            show_in_menus=True,
        )

        self.get_or_update_child(
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

        self.get_or_update_child(
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

        legal_notice = self.get_or_update_child(
            home, StandardPage, "mentions-legales", "Mentions légales",
            body=self.legal_notice_body(),
            show_in_menus=False,
        )
        privacy_policy = self.get_or_update_child(
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
            "agroalimentaire et distribution : une agriculture intégrée au "
            "service de la souveraineté alimentaire du Sénégal."
        )
        settings_obj.legal_notice_page = legal_notice
        settings_obj.privacy_policy_page = privacy_policy
        settings_obj.save()

        self.stdout.write(self.style.SUCCESS(
            "Contenu de demonstration cree/mis a jour : pages, catégories, "
            "réglages du site.\n"
            "Rappel : coordonnées reelles, numeros d'immatriculation, "
            "points de vente reels et articles d'actualite restent a "
            "completer dans l'admin Wagtail (/admin/) avant la mise en "
            "ligne, voir README."
        ))
        if contact_page:
            self.stdout.write(f"Page Contact : /{contact_page.slug}/")

    # ------------------------------------------------------------------
    def get_or_update_child(self, parent, model, slug, title, show_in_menus=False, **fields):
        """
        get_or_create by slug, but also refresh the fields on an existing
        page and republish, so iterating on this command's content updates
        the live site instead of being a no-op after the first run.
        """
        existing = model.objects.child_of(parent).filter(slug=slug).first()
        if existing:
            existing.title = title
            for key, value in fields.items():
                setattr(existing, key, value)
            existing.show_in_menus = show_in_menus
            existing.save()
            existing.save_revision().publish()
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
                    "eyebrow": "SAS agricole intégrée. Sénégal. Fondée en 2026",
                    "heading": "Nourrir l'Humanité en toute humanité",
                    "subheading": (
                        "Production agricole, élevage, pisciculture et "
                        "transformation agroalimentaire, au service de la "
                        "souveraineté alimentaire du Sénégal."
                    ),
                    "image": img("Troupeau au coucher du soleil").pk if img("Troupeau au coucher du soleil") else None,
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
                        "locaux ainsi que leur distribution, pour répondre aux besoins "
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
                    "image": img("Bovins à l'auge").pk if img("Bovins à l'auge") else None,
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
                    "image": img("Légumes frais de saison").pk if img("Légumes frais de saison") else None,
                    "fallback_icon": "leaf",
                    "eyebrow": "Nos produits",
                    "heading": "Des produits sains, accessibles et de qualité",
                    "body": rich(
                        "Notre catalogue s'organise autour de nos filières de "
                        "production : maraîchage et céréales, élevage et volaille, "
                        "pisciculture, produits transformés, pour répondre aux "
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
        gustavo = img("Agriculteur avec panier de récolte")
        return [
            {
                "type": "text",
                "value": {
                    "eyebrow": "Depuis 2026",
                    "heading": "Notre histoire",
                    "alignment": "left",
                    "body": rich(
                        "La Ferme Sénégalaise est une entreprise agricole créée avec "
                        "l'ambition de contribuer durablement à la souveraineté "
                        "alimentaire du Sénégal, tout en promouvant un modèle de "
                        "production respectueux des principes du développement "
                        "durable. Elle naît d'un constat simple : le Sénégal dispose "
                        "de terres, d'un savoir-faire agricole et d'une demande "
                        "intérieure croissante, mais une partie de son alimentation "
                        "reste dépendante de filières longues et importées. Fonder une "
                        "ferme intégrée, capable de produire, transformer et "
                        "distribuer sur son propre territoire, est une réponse directe "
                        "à cet enjeu de souveraineté.",
                        "Fondée sur une vision moderne de l'agriculture et de "
                        "l'agroalimentaire, l'entreprise s'attache à offrir aux "
                        "consommateurs des produits sains, accessibles et de qualité, "
                        "en s'appuyant sur des valeurs fortes de proximité, de "
                        "réactivité, d'équité et de responsabilité. Ces quatre valeurs "
                        "ne sont pas de simples mots d'ordre : elles structurent la "
                        "manière dont La Ferme Sénégalaise choisit ses implantations, "
                        "fixe ses prix et organise sa relation avec ses clients comme "
                        "avec ses partenaires.",
                        "La société a pour objet, tant au Sénégal qu'à l'étranger, "
                        "l'exploitation de terres agricoles, l'élevage, la "
                        "transformation agroalimentaire, la commercialisation ainsi "
                        "que la fourniture de prestations de services agricoles. Cette "
                        "intégration verticale, de la parcelle à l'assiette, est au "
                        "cœur du modèle : elle permet de maîtriser la qualité à chaque "
                        "étape, de réduire les intermédiaires inutiles et de mieux "
                        "répercuter la valeur créée vers les producteurs comme vers "
                        "les consommateurs.",
                        "Au-delà de sa vocation productive, La Ferme Sénégalaise place "
                        "le consommateur au cœur de son projet. À travers un réseau de "
                        "points de service accessibles, fiables et adaptés aux "
                        "réalités urbaines, elle entend rapprocher durablement le "
                        "producteur du consommateur et favoriser une alimentation de "
                        "qualité à des prix justes, aussi bien pour les ménages que "
                        "pour les restaurateurs, hôtels et commerces qui s'approvisionnent "
                        "chez elle.",
                        "Portée par une démarche entrepreneuriale rigoureuse, "
                        "l'entreprise veille au respect des normes d'hygiène, de "
                        "sécurité sanitaire et de qualité à chaque étape de sa chaîne "
                        "de valeur. Elle s'engage également à promouvoir des pratiques "
                        "agricoles responsables, génératrices d'emplois et de revenus, "
                        "contribuant ainsi au développement économique local et à la "
                        "résilience des systèmes alimentaires nationaux. La Ferme "
                        "Sénégalaise se veut ainsi un acteur de référence dans la "
                        "construction d'une agriculture moderne, performante et "
                        "durable, au service des populations et du développement du "
                        "Sénégal.",
                    ),
                },
            },
            {
                "type": "image_text",
                "value": {
                    "image": gustavo.pk if gustavo else None,
                    "fallback_icon": "handshake",
                    "eyebrow": "Notre vision",
                    "heading": "Rapprocher durablement le producteur du consommateur",
                    "body": rich(
                        "Nous croyons qu'une agriculture forte se construit en "
                        "circuit court, en associant production rigoureuse et "
                        "proximité avec ceux qui consomment. Chaque exploitation, "
                        "chaque point de vente et chaque prestation de service "
                        "s'inscrit dans cette même logique : produire local, "
                        "transformer localement ce qui peut l'être, et distribuer au "
                        "plus près des ménages, des restaurateurs et des commerces "
                        "qui en dépendent au quotidien."
                    ),
                    "button": {"text": "Voir nos activités", "page": None, "url": "/nos-activites/", "style": "primary"},
                    "image_position": "right",
                },
            },
            {
                "type": "timeline",
                "value": {
                    "heading": "Notre feuille de route",
                    "items": [
                        {"year": "2026", "text": "Création de La Ferme Sénégalaise SAS, avec l'ambition de contribuer durablement à la souveraineté alimentaire du Sénégal."},
                        {"year": "Aujourd'hui", "text": "Mise en place des cinq filières intégrées (production végétale, production animale, transformation, commercialisation, prestations de services) et structuration du réseau de distribution."},
                        {"year": "Demain", "text": "Montée en puissance progressive des exploitations, élargissement du catalogue de produits et ouverture, à terme, d'un module de commande en ligne."},
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
                        "<strong>Production végétale.</strong> Elle couvre "
                        "l'exploitation de terres agricoles, la culture de céréales, "
                        "de plantes oléagineuses, de fruits, de légumes (maraîchage), "
                        "et de toutes plantes horticoles ou industrielles. C'est le "
                        "socle de notre activité : des céréales qui contribuent à la "
                        "sécurité alimentaire des ménages jusqu'aux légumes de "
                        "maraîchage qui garnissent les étals au quotidien, en passant "
                        "par les plantes oléagineuses qui alimentent notre propre "
                        "activité de transformation. Cette filière est pensée pour "
                        "limiter la dépendance aux importations et valoriser le "
                        "potentiel agronomique du territoire sénégalais.",
                        "<strong>Production animale.</strong> Elle regroupe l'élevage "
                        "de bétail (bovins, ovins, caprins, porcins), l'aviculture "
                        "(poulets de chair et pondeuses), la production de lait et "
                        "d'œufs, la pisciculture, la cuniculture et la "
                        "coturniculture. En intégrant l'élevage terrestre et la "
                        "pisciculture au sein d'une même filière, nous diversifions "
                        "les sources de protéines animales proposées à nos clients "
                        "tout en répartissant les risques liés à chaque type "
                        "d'élevage. Le bien-être animal et le respect des normes "
                        "sanitaires y sont une exigence constante.",
                        "<strong>Transformation agroalimentaire.</strong> Elle "
                        "comprend le conditionnement, la conservation, la "
                        "transformation et la valorisation des produits issus de "
                        "l'exploitation, par exemple le pressage d'huile ou le "
                        "séchage de fruits. Cette étape est ce qui distingue une "
                        "ferme d'une véritable entreprise agroalimentaire : elle "
                        "permet de prolonger la durée de vie des récoltes, de "
                        "réduire les pertes post-récolte et de proposer des produits "
                        "prêts à consommer ou à cuisiner, avec une traçabilité "
                        "maîtrisée de bout en bout.",
                        "<strong>Commercialisation.</strong> Elle couvre la vente en "
                        "gros, demi-gros ou détail, ainsi que l'import-export de "
                        "produits agricoles, de semences, d'engrais et de matériel "
                        "agricole. À travers un réseau de points de vente et de "
                        "distribution accessibles, cette filière est le lien direct "
                        "entre nos exploitations et les ménages, restaurateurs, "
                        "hôtels et commerces qui nous font confiance au quotidien.",
                        "<strong>Prestations de services.</strong> Elle regroupe la "
                        "fourniture de services agricoles tels que le labour, la "
                        "récolte et les conseils techniques, ainsi que la gestion de "
                        "systèmes d'irrigation. Au-delà de notre propre production, "
                        "nous mettons notre savoir-faire agricole au service "
                        "d'autres exploitants, contribuant ainsi à la modernisation "
                        "et à la performance de l'agriculture sénégalaise dans son "
                        "ensemble.",
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
                        "<strong>Éditeur du site :</strong> La Ferme Sénégalaise SAS, "
                        "société créée en 2026, dont le siège social est situé au "
                        "Sénégal. Numéro RCCM, NINEA et adresse complète du siège : "
                        "[à compléter par l'entreprise avant la mise en ligne].",
                        "<strong>Directeur de la publication :</strong> [à compléter].",
                        "<strong>Hébergement :</strong> [nom et adresse de "
                        "l'hébergeur à compléter au moment du déploiement].",
                        "<strong>Contact :</strong> voir la page Contact du site.",
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
                        "<strong>Données collectées :</strong> les informations "
                        "transmises via le formulaire de contact (nom, e-mail, "
                        "téléphone, message) et, si vous vous inscrivez, votre "
                        "adresse e-mail pour la newsletter.",
                        "<strong>Utilisation :</strong> ces données sont utilisées "
                        "exclusivement pour répondre à vos demandes et vous tenir "
                        "informé(e) de notre actualité si vous y avez consenti. Elles "
                        "ne sont ni vendues ni cédées à des tiers.",
                        "<strong>Vos droits :</strong> vous pouvez demander l'accès, "
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
            (
                "production-vegetale", "Production végétale", "seedling",
                "Exploitation de terres agricoles : céréales, plantes oléagineuses, fruits, légumes et maraîchage.",
                "Légumes frais de saison",
                rich(
                    "Notre filière de production végétale couvre l'exploitation de "
                    "terres agricoles, la culture de céréales, de plantes "
                    "oléagineuses, de fruits, de légumes de maraîchage, et de toutes "
                    "plantes horticoles ou industrielles.",
                    "C'est la première étape de notre chaîne de valeur : elle fournit "
                    "à la fois les produits vendus frais sur nos points de vente et "
                    "les matières premières de notre filière de transformation "
                    "agroalimentaire, par exemple les plantes oléagineuses pressées "
                    "pour produire de l'huile.",
                    "Nous portons une attention particulière à la qualité du sol, à "
                    "la gestion raisonnée de l'eau et à des pratiques culturales "
                    "responsables, dans la continuité de notre engagement pour un "
                    "développement durable et une production locale de qualité.",
                ),
                [],
            ),
            (
                "production-animale", "Production animale", "home",
                "Élevage de bétail, aviculture, production de lait et d'œufs, pisciculture, cuniculture et coturniculture.",
                "Bovins à l'auge",
                rich(
                    "Notre filière de production animale regroupe l'élevage de "
                    "bétail (bovins, ovins, caprins, porcins), l'aviculture (poulets "
                    "de chair et pondeuses), la production de lait et d'œufs, la "
                    "pisciculture, la cuniculture et la coturniculture.",
                    "En réunissant élevage terrestre et pisciculture au sein d'une "
                    "même filière intégrée, nous diversifions les sources de "
                    "protéines animales que nous proposons à nos clients, qu'il "
                    "s'agisse de viande, de lait, d'œufs ou de poisson d'élevage.",
                    "Le respect du bien-être animal, le suivi sanitaire rigoureux et "
                    "une alimentation adaptée à chaque espèce sont au cœur de nos "
                    "pratiques d'élevage, au service de produits sains et d'une "
                    "traçabilité complète, de l'exploitation jusqu'au point de "
                    "vente.",
                ),
                ["Veaux au nourrisseur", "Portrait de bovin", "Banc de poissons"],
            ),
            (
                "transformation-agroalimentaire", "Transformation agroalimentaire", "bolt",
                "Conditionnement, conservation, transformation et valorisation des produits issus de l'exploitation.",
                "Ligne de conditionnement agroalimentaire",
                rich(
                    "Notre filière de transformation agroalimentaire assure le "
                    "conditionnement, la conservation, la transformation et la "
                    "valorisation des produits issus de nos exploitations, "
                    "notamment le pressage d'huile et le séchage de fruits.",
                    "Cette étape prolonge la durée de vie de nos récoltes, réduit "
                    "les pertes après récolte et permet de proposer à nos clients "
                    "des produits transformés prêts à consommer ou à cuisiner, avec "
                    "un niveau de qualité et d'hygiène constant.",
                    "Chaque produit transformé reste traçable jusqu'à l'exploitation "
                    "dont il est issu, dans le respect des normes d'hygiène et de "
                    "sécurité sanitaire qui structurent l'ensemble de notre "
                    "démarche.",
                ),
                ["Huile végétale et légumes racines"],
            ),
            (
                "commercialisation", "Commercialisation", "handshake",
                "Vente en gros, demi-gros ou détail, import-export de produits agricoles, semences, engrais et matériel agricole.",
                "Étal de légumes",
                rich(
                    "Notre filière de commercialisation couvre la vente en gros, "
                    "demi-gros ou détail, ainsi que l'import-export de produits "
                    "agricoles, de semences, d'engrais et de matériel agricole.",
                    "À travers un réseau de points de vente et de distribution "
                    "accessibles, fiables et adaptés aux réalités urbaines, cette "
                    "filière est le lien direct entre nos exploitations et les "
                    "ménages, restaurateurs, hôtels et commerces qui nous font "
                    "confiance au quotidien.",
                    "Notre objectif est de proposer une alimentation de qualité à "
                    "des prix justes, tout en construisant une relation de "
                    "proximité et de confiance durable avec l'ensemble de nos "
                    "clients et partenaires commerciaux.",
                ),
                [],
            ),
            (
                "prestations-de-services", "Prestations de services", "shield",
                "Services agricoles (labour, récolte, conseils techniques) et gestion de systèmes d'irrigation.",
                None,
                rich(
                    "Notre filière de prestations de services regroupe la "
                    "fourniture de services agricoles tels que le labour, la "
                    "récolte et les conseils techniques, ainsi que la gestion de "
                    "systèmes d'irrigation.",
                    "Au-delà de notre propre production, nous mettons notre "
                    "savoir-faire agricole au service d'autres exploitants et "
                    "partenaires techniques, contribuant ainsi à la modernisation "
                    "et à la performance de l'agriculture sénégalaise dans son "
                    "ensemble.",
                    "Cette filière illustre notre ambition de devenir un acteur de "
                    "référence de l'agriculture moderne au Sénégal, au service des "
                    "producteurs autant que des consommateurs.",
                ),
                [],
            ),
        ]
        for slug, title, icon, summary, cover_title, body_text, gallery_titles in activities:
            cover = img(cover_title) if cover_title else None
            body = [{"type": "text", "value": {"eyebrow": "", "heading": "", "alignment": "left", "body": body_text}}]
            page = self.get_or_update_child(
                index_page, ActivityPage, slug, title,
                icon=icon, summary=summary,
                cover_image=cover,
                body=body,
                show_in_menus=True,
            )
            existing_images = set(page.gallery_images.values_list("image__title", flat=True))
            for order, gallery_title in enumerate(gallery_titles):
                if gallery_title in existing_images:
                    continue
                image = img(gallery_title)
                if image:
                    ActivityGalleryImage.objects.create(page=page, image=image, sort_order=order)

    # ------------------------------------------------------------------
    def seed_products(self, index_page):
        categories = [
            ("maraichage-cereales", "Maraîchage & céréales", "seedling"),
            ("elevage-volaille", "Élevage & volaille", "home"),
            ("pisciculture", "Pisciculture", "water"),
            ("produits-transformes", "Produits transformés", "bolt"),
        ]
        cat_objs = {}
        for slug, name, icon in categories:
            cat, _ = ProductCategory.objects.get_or_create(slug=slug, defaults={"name": name, "icon": icon})
            cat_objs[slug] = cat

        products = [
            ("riz-cereales", "Riz & céréales", "maraichage-cereales", "Céréales issues de notre production végétale.", "kg", None),
            ("legumes-frais", "Légumes frais", "maraichage-cereales", "Légumes de maraîchage cultivés selon des pratiques responsables.", "kg", "Légumes frais de saison"),
            ("poulet-de-chair", "Poulet de chair", "elevage-volaille", "Volaille issue de notre filière avicole.", "kg", "Éleveur avicole"),
            ("oeufs-frais", "Œufs frais", "elevage-volaille", "Œufs de poules pondeuses de nos exploitations.", "plateau de 30", "Panier d'œufs fermiers"),
            ("poisson-tilapia", "Poisson (tilapia)", "pisciculture", "Poisson d'élevage issu de notre activité de pisciculture intégrée.", "kg", "Poissons frais au marché"),
            ("huile-vegetale", "Huile végétale", "produits-transformes", "Huile pressée à partir de nos plantes oléagineuses.", "litre", "Huile végétale et légumes racines"),
        ]
        for slug, title, cat_slug, desc, unit, cover_title in products:
            self.get_or_update_child(
                index_page, ProductPage, slug, title,
                category=cat_objs[cat_slug],
                cover_image=img(cover_title) if cover_title else None,
                short_description=desc,
                availability="coming_soon",
                unit=unit,
                price_indication="Prix sur demande",
                body=[],
                show_in_menus=False,
            )

    # ------------------------------------------------------------------
    def seed_locations(self, locations_page):
        """
        Fictional points of sale around Dakar, requested explicitly to
        preview the map feature. Clearly labelled as examples in the page
        intro above; replace with real addresses before launch.
        """
        if locations_page.locations.exists():
            return

        fictional_sites = [
            ("Point de vente Plateau (exemple)", "point_de_vente", "12 Avenue Léopold Sédar Senghor", "Dakar", "+221 77 000 00 01", "Lun-Sam : 8h-19h", 14.6710, -17.4380),
            ("Point de vente Almadies (exemple)", "point_de_vente", "Route des Almadies", "Dakar", "+221 77 000 00 02", "Lun-Dim : 8h-20h", 14.7420, -17.5130),
            ("Point de vente Parcelles Assainies (exemple)", "point_de_vente", "Unité 12, Parcelles Assainies", "Dakar", "+221 77 000 00 03", "Lun-Sam : 8h-19h", 14.7583, -17.4167),
            ("Centre de distribution Pikine (exemple)", "distribution", "Zone industrielle, Pikine", "Pikine", "+221 77 000 00 04", "Lun-Ven : 7h-17h", 14.7547, -17.3900),
            ("Point de vente Rufisque (exemple)", "point_de_vente", "Marché central de Rufisque", "Rufisque", "+221 77 000 00 05", "Lun-Sam : 8h-18h", 14.7167, -17.2667),
            ("Exploitation pilote (exemple)", "exploitation", "Route de Sébikotane", "Sébikotane", "", "", 14.7500, -17.1333),
        ]
        for order, (name, ltype, address, city, phone, hours, lat, lng) in enumerate(fictional_sites):
            Location.objects.create(
                page=locations_page, sort_order=order,
                name=name, location_type=ltype, address=address, city=city,
                phone=phone, opening_hours=hours, latitude=lat, longitude=lng,
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
            subject="Nouveau message du site La Ferme Sénégalaise",
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
