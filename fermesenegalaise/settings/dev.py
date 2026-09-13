from .base import *  # noqa: F401,F403
from .base import env

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env(
    "SECRET_KEY",
    default="django-insecure-=!$3%wi)#3)%b_p@9rr2l=mxmwm(@5!0x(uho_22ofn0b62ro0",
)

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

INTERNAL_IPS = ["127.0.0.1"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Fast, no-op password hasher for local dev only — never used in production.py.
if env.bool("FAST_TEST_HASHER", default=False):
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
