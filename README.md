# La Ferme Sénégalaise : site institutionnel

Site vitrine professionnel pour **La Ferme Sénégalaise SAS**, bâti sur **Django + Wagtail CMS**,
conçu pour être administré en autonomie par l'équipe de l'entreprise et pour évoluer vers
l'e-commerce sans refonte du socle technique.

## Sommaire

- [Stack technique et choix d'architecture](#stack-technique-et-choix-darchitecture)
- [Démarrage local](#démarrage-local)
- [Structure du projet](#structure-du-projet)
- [Système de design](#système-de-design)
- [Médiathèque (photos et vidéo)](#médiathèque-photos-et-vidéo)
- [Administrer le contenu (guide éditeur)](#administrer-le-contenu-guide-éditeur)
- [Déploiement](#déploiement)
- [État d'avancement et prochaines étapes](#état-davancement-et-prochaines-étapes)

## Stack technique et choix d'architecture

| Choix | Pourquoi |
|---|---|
| **Django 6 + Wagtail 8** | CMS Python de référence pour des sites corporate (Google, Mozilla, NASA...) : admin moderne, édition par blocs, SEO natif, sécurité Django éprouvée. |
| **Templates Django server-rendered** (pas de SPA React/Vue) | Meilleur temps de chargement et SEO pour un site vitrine ; pas de build JS à maintenir. |
| **CSS sur-mesure (tokens + composants)**, pas de framework | Fidélité totale à la charte graphique (couleurs, typographies) sans surcharge d'un framework générique. |
| **PostgreSQL (prod) / SQLite (dev)** | Standard, portable, pas de verrou fournisseur. |
| **Docker** | Déploiement portable quel que soit l'hébergeur choisi (VPS, PaaS). |
| **StreamField ("blocs" Wagtail)** | Les pages Accueil, Qui sommes-nous, Partenaires... sont composées de blocs réutilisables (Hero, Chiffres clés, Valeurs, Image+texte, CTA...) que l'équipe peut réordonner/ajouter sans développeur. |
| **Français uniquement au lancement** | `WAGTAIL_I18N_ENABLED = False` dans `fermesenegalaise/settings/base.py`. L'architecture est prête pour l'anglais : il suffira de passer ce réglage à `True` et de traduire les pages, sans restructurer les modèles. |

## Démarrage local

Prérequis : Python 3.12+, un environnement virtuel.

```bash
python -m venv venv
venv\Scripts\activate          # PowerShell : venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Base de données locale (SQLite, aucune config requise)
python manage.py migrate

# Compte administrateur pour l'admin Wagtail (/admin/)
python manage.py createsuperuser

# (Optionnel, recommandé la 1ère fois) photos, puis contenu de démonstration :
# voir la section "Médiathèque" ci-dessous pour import_media
python manage.py import_media
python manage.py seed_demo_content

python manage.py runserver
```

Le site est servi sur `http://127.0.0.1:8000/`, l'admin sur `http://127.0.0.1:8000/admin/`.

Par défaut, `manage.py` utilise `fermesenegalaise.settings.dev` (voir `manage.py`).
Pour tester la configuration de production en local, exportez
`DJANGO_SETTINGS_MODULE=fermesenegalaise.settings.production` et fournissez un fichier
`.env` (copier `.env.example`).

## Structure du projet

```
fermesenegalaise/        Réglages Django (settings/base|dev|production.py), urls, templates de base
core/                     Design system partagé : blocs StreamField, icônes SVG, SiteSettings, tags de template
home/                     Page d'accueil (StreamField libre)
pages/                    StandardPage : page flexible générique (Qui sommes-nous, Partenaires, mentions légales...)
activities/               "Nos activités" : page liste + fiches par filière
products/                 "Nos produits" : catégories + fiches produit (prêt pour l'e-commerce plus tard)
news/                     "Actualités" / blog
gallery/                  "Galerie" photos & vidéos, filtrable par catégorie
locations/                "Points de vente" : carte (Leaflet/CARTO) + liste
contact/                  Formulaire de contact (Wagtail forms + anti-spam invisible) + newsletter
```

Chaque app suit le même schéma : `models.py` (modèles Wagtail), `templates/<app>/*.html`.
Les blocs de contenu réutilisables (Hero, Stats, Valeurs, Image+texte, CTA, Timeline,
Témoignages, Logos, Documents, Vidéo) vivent dans `core/blocks.py` avec leurs templates
dans `core/templates/core/blocks/`.

## Système de design

Les tokens (`fermesenegalaise/static/css/tokens.css`) reprennent exactement les couleurs de
la charte graphique (3S Design) :

- `#3AAA35` vert principal · `#95C11F` vert clair · `#634E42` brun terre
- `#F39242` orange · `#E7AD13` or · `#009FE3` bleu (pisciculture)

Pour les boutons et liens sur fond blanc, une teinte de vert légèrement plus foncée
(`--color-primary-strong: #1F7A1D`) est utilisée à la place du vert pur de la charte : le
vert exact n'atteint qu'un contraste d'environ 3:1 avec du texte blanc (sous le seuil
d'accessibilité AA de 4.5:1 pour du texte). Le vert de marque reste utilisé tel quel pour
les grands aplats, icônes et bordures où ce n'est pas un problème.

**Typographies.** Century Gothic (indiquée dans la charte) est une police propriétaire
Monotype non clarifiée pour l'intégration web. Le site utilise **Jost** (Google Fonts,
licence libre OFL), une géométrique très proche dans l'esprit, pour les titres, et
**Work Sans** pour le texte courant (meilleure lisibilité en petite taille). **Alex Brush**,
nommée explicitement dans la charte et disponible sur Google Fonts, est utilisée pour
l'accent script (`Nourrir l'Humanité en toute humanité`).

**Logo.** `fermesenegalaise/static/images/brand/` contient le logo original ainsi que deux
variantes recadrées : `logo-header.png` (icône + nom, sans la baseline, pour l'en-tête) et
`favicon-*.png` / `favicon.ico` (juste le pictogramme maison, pour l'onglet navigateur).

## Médiathèque (photos et vidéo)

Les photos fournies vivent dans `docs/photos-source/`, suivies par Git (contrairement à la
plupart des dossiers de médias, volontairement : voir "Mise en ligne rapide" plus bas pour
pourquoi). La commande suivante les importe dans Wagtail avec des titres propres et les
rattache automatiquement au bon endroit (hero de l'accueil, page Qui sommes-nous, fiches
activités, fiches produits) :

```bash
python manage.py import_media
```

Elle est idempotente : relancez-la sans risque si vous ajoutez de nouvelles photos dans
`docs/photos-source/` (mettez alors aussi à jour la liste `IMAGES` en haut du fichier
`core/management/commands/import_media.py`). Deux filières (Riz & céréales, Prestations de
services) n'ont volontairement pas reçu de photo faute d'un visuel pertinent dans le lot
fourni : elles affichent un repli visuel (icône sur fond dégradé) plutôt qu'une image hors
sujet, jusqu'à ce qu'une vraie photo soit disponible.

La vidéo source (`docs/video-source/`, un plan brut de 78 Mo en 4K) a été recompressée pour
le web : `fermesenegalaise/static/video/aviculture.mp4` (720p, sans son, ~3 Mo, démarrage
rapide) avec son image d'aperçu `aviculture-poster.jpg`. Elle est intégrée directement dans
le gabarit de la page "Production animale" (`activities/templates/activities/activity_page.html`)
via une balise `<video>` native. Pour la remplacer, déposez le nouveau fichier au même
chemin ou recompressez avec ffmpeg :

```bash
ffmpeg -i source.mp4 -vf "scale=1280:-2" -an -c:v libx264 -crf 26 -preset slow -movflags +faststart aviculture.mp4
```

### Carte "Points de vente" : clé API

Aucun fournisseur de fond de carte gratuit et sans clé n'est réellement fiable en
production : OpenStreetMap interdit explicitement l'usage direct de son propre serveur par
des sites tiers, et CARTO (utilisé un temps sur ce projet) affiche désormais un tuile
"API key required" à la place de la carte pour qui n'a pas de clé.

Le projet est câblé pour **MapTiler**, dont l'offre gratuite (100 000 chargements de carte
par mois, sans carte bancaire) suffit largement à ce site :

1. Créer un compte sur <https://cloud.maptiler.com/>.
2. Dans le menu de gauche, ouvrir **API keys** : une clé par défaut est déjà générée (ou en
   créer une nouvelle).
3. Copier cette clé dans le fichier `.env` à la racine du projet (voir `.env.example`) :
   `MAPTILER_API_KEY=votre_cle`.

Tant qu'aucune clé n'est renseignée, la carte utilise automatiquement le serveur
d'OpenStreetMap en secours (visible dans la console du navigateur via un avertissement) :
cela suffit pour développer en local, mais n'est pas garanti de rester fonctionnel une fois
le site public.

## Administrer le contenu (guide éditeur)

1. Se connecter sur `/admin/`.
2. Le menu de gauche **Pages** montre l'arborescence du site. Ouvrir une page puis
   **Modifier** pour éditer son contenu.
3. Les pages "flexibles" (Accueil, Qui sommes-nous, Partenaires, Activités, Produits...)
   utilisent un champ **Contenu** en blocs : cliquer sur **+** pour ajouter un bloc
   (Bannière, Chiffres clés, Valeurs, Image + texte, Témoignages...), glisser-déposer pour
   réordonner.
4. **Réglages du site** (menu Paramètres) centralise téléphone, e-mail, adresse, réseaux
   sociaux et pages légales, modifiables sans toucher au code, répercutés automatiquement
   dans l'en-tête et le pied de page.
5. Une page n'apparaît dans le menu principal que si la case **Afficher dans les menus**
   (onglet **Promotion**) est cochée.
6. **Formulaire de contact** : les champs sont modifiables depuis la page Contact
   (section "Champs du formulaire") sans toucher au code ; les soumissions sont visibles
   sous **Formulaires → Contact** dans l'admin.
7. **Points de vente** : la page contient actuellement des sites fictifs autour de Dakar,
   ajoutés uniquement pour valider l'affichage de la carte. Ouvrez la page dans l'admin,
   section "Sites", pour les remplacer par les adresses réelles (chaque site a besoin
   d'une latitude/longitude, faciles à récupérer via un clic droit sur Google Maps ou
   OpenStreetMap : "Plus d'infos sur cet endroit").

## Déploiement

### Mise en ligne rapide (relecture client)

Pour donner au client un lien public pendant qu'il n'y a pas encore d'hébergement définitif,
le plus rapide est **Render.com** (offre gratuite, ~20 minutes de mise en place, aucune
carte bancaire requise). Le fichier `render.yaml` à la racine du projet décrit déjà le
service et la base de données à créer.

1. **Créer un dépôt GitHub** (si ce n'est pas déjà fait) et y pousser ce projet :
   ```bash
   git remote add origin https://github.com/<votre-compte>/ferme-senegalaise.git
   git push -u origin main
   ```
2. Créer un compte sur <https://dashboard.render.com/> (le plus simple : "Se connecter avec
   GitHub").
3. **New +** → **Blueprint**, choisir le dépôt `ferme-senegalaise`. Render lit `render.yaml`
   et propose de créer le service web et la base PostgreSQL d'un coup : valider.
4. Une fois le premier déploiement terminé, aller dans le service → **Environment** et
   renseigner les variables laissées vides volontairement (pas de secret dans le fichier
   versionné) :
   - `MAPTILER_API_KEY` : la clé obtenue plus haut.
   - `CONTACT_FORM_RECIPIENT_EMAIL` : l'adresse e-mail qui doit recevoir les messages du
     formulaire de contact.
   - `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD` :
     vos identifiants admin (voir note ci-dessous).
   Chaque sauvegarde relance automatiquement le service avec les nouvelles valeurs.
5. Le site est accessible sur `https://ferme-senegalaise.onrender.com` (ou le nom choisi à
   l'étape 3, à répercuter alors dans `ALLOWED_HOSTS`/`BASE_URL`/`CSRF_TRUSTED_ORIGINS` sur
   Render si différent de `render.yaml`). L'admin est sur `/admin/`, avec les identifiants
   donnés à l'étape 4.

**Pas de compte admin ni de contenu à créer à la main** : l'offre gratuite de Render n'a pas
d'onglet Shell ni de "one-off jobs" pour lancer des commandes ponctuelles, donc le
`Dockerfile` les exécute lui-même à chaque démarrage du conteneur (`ensure_superuser`,
`import_media`, `seed_demo_content --if-empty`). Chacune est conçue pour ne rien faire si
elle a déjà fait son travail : le compte admin n'est créé qu'une fois (tant que
`DJANGO_SUPERUSER_*` reste renseigné, inoffensif de le laisser en place), et
`seed_demo_content --if-empty` s'arrête immédiatement dès que la page "Qui sommes-nous"
existe déjà, pour ne jamais écraser un contenu que le client aurait modifié entre-temps
dans l'admin.

Cette protection a une contrepartie : si vous mettez à jour le contenu ou les photos dans
`core/management/commands/seed_demo_content.py` / `import_media.py` **après** le tout
premier déploiement, `--if-empty` les ignore, puisque le site n'est plus "vide" à ses yeux.
Pour forcer malgré tout une mise à jour complète sur le déploiement suivant : variable
d'environnement `FORCE_RESEED=true` dans l'onglet **Environment** du service (voir
`.env.example`), sauvegarder (ce qui relance le déploiement automatiquement), vérifier que
le site est à jour, puis retirer cette variable pour revenir à la protection normale. Aucun
push ni modification de code requis pour ce va-et-vient.

Trois limites propres à l'offre gratuite de Render, à garder en tête pendant cette phase de
relecture :
- Le service "s'endort" après 15 minutes sans visite ; la première page vue ensuite met
  quelques secondes à charger, le temps qu'il se réveille. Sans incidence pour une
  consultation ponctuelle.
- Le disque n'est pas persistant : toute photo ajoutée **directement via l'admin en ligne**
  (plutôt que via `docs/photos-source/` + `import_media`) serait perdue au prochain
  redémarrage. Pour cette phase, le plus sûr reste de continuer à récupérer les
  photos/informations du client par un autre canal (WhatsApp, e-mail...) et de les intégrer
  en local avec `import_media` avant de pousser sur GitHub, comme pour celles déjà en ligne.
  Si le client doit à terme téléverser ses médias lui-même en autonomie, il faudra brancher
  un stockage externe (Cloudflare R2, S3...) avant d'ouvrir cet accès ; je peux m'en charger
  le moment venu.

Les photos du dossier `docs/photos-source/` sont quant à elles suivies par Git (le disque
non persistant ne les affecte donc pas : `import_media` les réimporte automatiquement à
chaque démarrage à partir de la copie embarquée dans l'image Docker, et répare même
silencieusement tout fichier qui aurait disparu d'un redémarrage à l'autre). Seule
exception volontaire : une photo du lot original montre la marque visible d'un tiers
("Supreme Berry Farms") et a été exclue, voir `core/management/commands/import_media.py`.

### Hébergement définitif (VPS)

```bash
cp .env.example .env   # puis renseigner les vraies valeurs
docker compose up --build -d
```

Le `Dockerfile` construit une image de production (Gunicorn + WhiteNoise pour les fichiers
statiques) ; `docker-compose.yml` ajoute une base PostgreSQL. C'est une base portable vers
n'importe quel hébergeur (VPS avec Docker, ou un PaaS qui sait lire un `Dockerfile`/`docker-compose.yml`).
Aucun choix d'hébergeur n'est figé dans le code.

Avant la mise en ligne réelle, `fermesenegalaise/settings/production.py` impose :
`SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS` (voir `.env.example` pour la liste complète).

## État d'avancement et prochaines étapes

**Fait.** Socle technique complet et fonctionnel : Django/Wagtail configuré, système de
design fidèle à la charte, 9 gabarits de page (Accueil, Qui sommes-nous, Nos activités +
fiches, Nos produits + fiches, Galerie, Points de vente avec carte, Actualités, Contact,
Partenaires & investisseurs), SEO (sitemap.xml, robots.txt, meta Open Graph, image de
partage), formulaire de contact avec piège anti-spam invisible, newsletter, Docker prêt
pour le déploiement. Arborescence de pages créée avec le texte réel du cahier des charges,
largement développé sur "Qui sommes-nous" et chaque fiche activité (`python manage.py
seed_demo_content`). Médiathèque de photos et vidéo importée et intégrée aux pages
concernées (`python manage.py import_media`).

**Reste à faire avant la mise en ligne.** Ces points nécessitent des informations ou des
décisions propres à l'entreprise, volontairement non inventées :

- [ ] Compléter la médiathèque : les filières Riz & céréales et Prestations de services
      n'ont pas encore de photo pertinente (repli visuel en icône en attendant).
- [ ] Coordonnées réelles (téléphone, e-mail, adresse) dans **Réglages du site**.
- [ ] Points de vente réels (adresses + coordonnées GPS) dans la page **Points de vente** :
      les six sites actuels sont des exemples fictifs autour de Dakar, à remplacer.
- [ ] Numéro RCCM, NINEA et adresse du siège dans la page **Mentions légales**
      (actuellement marqués `[à compléter]`).
- [ ] Catalogue produit réel (les 6 produits actuels sont des exemples génériques dérivés
      de l'objet social, avec prix "sur demande", à remplacer par le vrai catalogue).
- [ ] Premiers articles d'**Actualités** (page créée vide intentionnellement).
- [ ] Configuration e-mail (`EMAIL_HOST`...) pour que le formulaire de contact envoie
      réellement des notifications.
- [ ] Nom de domaine + hébergement définitif.

**Évolutions prévues par le cahier des charges.** La structure est prête à les recevoir :

- **E-commerce** : `ProductPage` porte déjà `availability`/`unit`/`price_indication` ;
  passer à un vrai panier/paiement s'ajoute par une app `orders` sans redesign des pages
  produit existantes.
- **Bilingue FR/EN** : passer `WAGTAIL_I18N_ENABLED = True` puis traduire les pages via
  l'admin Wagtail (workflow de traduction intégré).
