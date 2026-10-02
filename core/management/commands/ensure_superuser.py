"""
Non-interactive, idempotent superuser bootstrap for platforms without shell
access on their free tier (Render's free plan, notably). Reads credentials
from environment variables and is safe to run on every container boot:
skips quietly if the account already exists, and never raises if the env
vars are missing (so a deploy without them configured yet still starts).
"""
import environ
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the initial Wagtail admin account from DJANGO_SUPERUSER_* env vars."

    def handle(self, *args, **options):
        env = environ.Env()

        username = env("DJANGO_SUPERUSER_USERNAME", default="")
        email = env("DJANGO_SUPERUSER_EMAIL", default="")
        password = env("DJANGO_SUPERUSER_PASSWORD", default="")

        if not username or not password:
            self.stdout.write(
                "DJANGO_SUPERUSER_USERNAME/PASSWORD non definis : aucun compte "
                "administrateur cree automatiquement (voir .env.example)."
            )
            return

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Le compte '{username}' existe deja, rien a faire.")
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Compte administrateur '{username}' cree."))
