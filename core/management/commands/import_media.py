"""
One-off import of the client-supplied photo library into Wagtail's image
library. Source files live in docs/photos-source/ (kept out of git; see
.gitignore) and are registered here as wagtail.images.Image objects with
clean, descriptive titles the rest of the seed content can look up by name.

Safe to re-run: skipped if an image with the same title already exists.
"""
from pathlib import Path

from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand

from wagtail.images.models import Image

SOURCE_DIR = Path("docs/photos-source")

# (source filename, Wagtail image title). Titles are the lookup keys used
# by seed_demo_content.py: keep them stable once other code depends on them.
IMAGES = [
    ("stijn-te-strake-UdhpcfImQ9Y-unsplash.jpg", "Troupeau au coucher du soleil"),
    ("pexels-gustavo-fring-4975353.jpg", "Agriculteur avec panier de récolte"),
    ("pexels-readymade-3987334.jpg", "Légumes frais de saison"),
    ("pexels-eduschadesoares-5498219.jpg", "Étal de légumes"),
    ("jaron-grobler-aHmgEraWYXs-unsplash.jpg", "Portrait de bovin"),
    ("pexels-yankrukov-5216150.jpg", "Bovins à l'auge"),
    ("pexels-cristian-rojas-10041325.jpg", "Veaux au nourrisseur"),
    ("mikhail-preobrazhenskiy-9kSZdpIf_Fo-unsplash.jpg", "Banc de poissons"),
    ("chicken-farm-scene-with-poultry-people.jpg", "Éleveur avicole"),
    ("pexels-rezkyrahmatullah-37648666.jpg", "Poissons frais au marché"),
    ("pexels-sultan-guner-1095138285-20877229.jpg", "Panier d'œufs fermiers"),
    ("pexels-tanyanovoselova-8922305.jpg", "Huile végétale et légumes racines"),
    ("richard-r-5aZ80momNb4-unsplash.jpg", "Ligne de conditionnement agroalimentaire"),
]


class Command(BaseCommand):
    help = "Import the source photo library into Wagtail's image library."

    def handle(self, *args, **options):
        if not SOURCE_DIR.exists():
            self.stderr.write(
                f"{SOURCE_DIR} introuvable : placez les photos sources a cet "
                "emplacement avant de lancer cette commande."
            )
            return

        created, skipped = 0, 0
        for filename, title in IMAGES:
            if Image.objects.filter(title=title).exists():
                skipped += 1
                continue
            path = SOURCE_DIR / filename
            if not path.exists():
                self.stderr.write(f"Fichier manquant, ignore : {path}")
                continue
            with open(path, "rb") as f:
                image = Image(title=title, file=ImageFile(f, name=filename))
                image.save()
            created += 1
            self.stdout.write(f"Importe : {title}")

        self.stdout.write(self.style.SUCCESS(
            f"{created} image(s) importee(s), {skipped} deja presente(s)."
        ))
