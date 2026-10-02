"""
Import the client-supplied photo library into Wagtail's image library.
Source files live in docs/photos-source/ and are registered here as
wagtail.images.Image objects with clean, descriptive titles the rest of
the seed content looks up by name.

Safe, and meant, to run on every container boot (see the Dockerfile): it
checks not just that an Image row exists for a given title, but that its
file is actually present in storage, and re-imports it if not. That
self-healing matters on a host with no persistent disk (Render's free
plan): the database (a separate managed Postgres instance) survives a
restart, but anything written to local disk, including uploaded image
files, does not — so after a restart the Image row is there but the file
behind it is gone. Re-running this then repairs it from the copy of
docs/photos-source/ baked into the Docker image, instead of leaving a
broken image icon on the live site.
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

        created, healed, skipped = 0, 0, 0
        for filename, title in IMAGES:
            existing = Image.objects.filter(title=title).first()
            if existing is not None:
                file_present = bool(existing.file) and existing.file.storage.exists(existing.file.name)
                if file_present:
                    skipped += 1
                    continue
                # Row survived (Postgres), but the file behind it didn't
                # (ephemeral disk reset): drop it and recreate cleanly below,
                # which also clears any now-dangling cached renditions.
                existing.delete()
                healed += 1

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
            f"{created} image(s) importee(s) ({healed} reparee(s)), "
            f"{skipped} deja presente(s) et intacte(s)."
        ))
