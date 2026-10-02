
# This stage installs build dependencies and compiles Python packages.
# It will be discarded in the final image, keeping only the compiled packages.
FROM python:3.14-slim-bookworm AS builder

# Install system packages required to build Python packages.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadb-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
 && rm -rf /var/lib/apt/lists/* \
 && python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

# Install the project requirements.
COPY requirements.txt /
RUN pip install -r /requirements.txt

# Install the application server.
RUN pip install "gunicorn==25.1.0"


# RUNTIME STAGE
# Use an official Python runtime based on Debian 12 "bookworm" as a parent image.
FROM python:3.14-slim-bookworm AS runtime

# Install runtime system packages required by Wagtail and Django.
# These are the runtime libraries needed by the compiled Python packages.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    libpq5 \
    libmariadb3 \
    libjpeg62-turbo \
    libwebp7 \
 && rm -rf /var/lib/apt/lists/*

# Add user that will be used in the container.
RUN useradd wagtail

# Port used by this container to serve HTTP.
EXPOSE 8000

# Set environment variables.
# 1. Force Python stdout and stderr streams to be unbuffered.
# 2. Set PORT variable that is used by Gunicorn. This should match "EXPOSE"
#    command.
# 3. Add the virtual environment to PATH.
ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE="fermesenegalaise.settings.production"



# Copy the virtual environment from the builder stage.
COPY --from=builder /opt/venv /opt/venv

# Use /app folder as a directory where the source code is stored.
WORKDIR /app

# Set this directory to be owned by the "wagtail" user. This Wagtail project
# uses SQLite, the folder needs to be owned by the user that
# will be writing to the database file.
RUN chown wagtail:wagtail /app

# Copy the source code of the project into the container.
COPY --chown=wagtail:wagtail . .

# Use user "wagtail" to run the build commands below and the server itself.
USER wagtail

# Collect static files. production.py reads SECRET_KEY/DATABASE_URL eagerly
# at import time, but collectstatic never touches the database: these
# build-only placeholders just satisfy that import; the real values come
# from the platform's env vars at `docker run` / deploy time.
RUN SECRET_KEY="build-time-placeholder" \
    DATABASE_URL="sqlite:///build-time-placeholder.sqlite3" \
    ALLOWED_HOSTS="localhost" \
    BASE_URL="http://localhost" \
    python manage.py collectstatic --noinput --clear

# Runtime command that executes when "docker run" is called, it does the
# following:
#   1. Migrate the database.
#   2. Create the admin account, if DJANGO_SUPERUSER_* env vars are set and
#      it doesn't already exist (see core/management/commands/ensure_superuser.py).
#   3. Import the photo library, if docs/photos-source/ is present in the
#      image (see core/management/commands/import_media.py) — a no-op
#      otherwise, e.g. on a platform where that gitignored folder was never
#      committed.
#   4. Seed the page tree, but only the very first time (--if-empty): once
#      "qui-sommes-nous" exists, this is skipped so a redeploy never
#      overwrites real edits made since in the Wagtail admin.
#   5. Start the application server.
# WARNING:
#   Running this at container boot (rather than as a separate release-phase
#   step) is not best practice, but it's what lets the site come up from a
#   single "docker run" on a platform with no paid shell/one-off-job add-on
#   (e.g. Render's free plan).
CMD set -xe; \
    python manage.py migrate --noinput; \
    (python manage.py ensure_superuser || true); \
    (python manage.py import_media || true); \
    (python manage.py seed_demo_content --if-empty || true); \
    gunicorn fermesenegalaise.wsgi:application --bind 0.0.0.0:${PORT:-8000}
