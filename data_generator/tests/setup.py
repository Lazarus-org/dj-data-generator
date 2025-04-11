from django import setup
from django.conf import settings
from django.core.management.utils import get_random_secret_key


def configure_django_settings() -> None:
    """
    Configures Django settings for testing or standalone usage.

    This function sets up Django's settings if they are not already configured.
    It configures the following settings:

    - DEBUG: Enables Django's debug mode.
    - SECRET_KEY: Provides a generated secret key for Django settings.
    - DATABASES: Configures an in-memory SQLite database for testing.
    - INSTALLED_APPS: Includes essential Django and third-party apps needed for the test environment.
    - MIDDLEWARE: Configures the middleware stack used by Django.
    - ROOT_URLCONF: Specifies the root URL configuration module.
    - TEMPLATES: Configures the template engine settings.
    - LANGUAGE_CODE: Sets the language code for the application.
    - TIME_ZONE: Sets the time zone for the application.
    - USE_I18N: Enables or disables Django's translation system.
    - USE_TZ: Enables or disables timezone support.
    - STATIC_URL: Specifies the URL for serving static files.

    Side Effects:
    --------------
    - Configures Django settings if they are not already set.
    - Calls `django.setup()` to initialize Django with the configured settings.

    Notes:
    ------
    This function is intended for use in testing environments or standalone scripts where
    a minimal Django setup is required. It does not configure production settings.
    """
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY=get_random_secret_key(),  # Add a secret key for testing
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
            INSTALLED_APPS=[
                "django.contrib.admin",
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "django.contrib.sessions",
                "django.contrib.messages",
                "django.contrib.staticfiles",
                "data_generator",
            ],
            MIDDLEWARE=[
                "django.middleware.security.SecurityMiddleware",
                "django.contrib.sessions.middleware.SessionMiddleware",
                "django.middleware.common.CommonMiddleware",
                "django.middleware.csrf.CsrfViewMiddleware",
                "django.contrib.auth.middleware.AuthenticationMiddleware",
                "django.contrib.messages.middleware.MessageMiddleware",
                "django.middleware.clickjacking.XFrameOptionsMiddleware",
            ],
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [],
                    "APP_DIRS": True,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.debug",
                            "django.template.context_processors.request",
                            "django.contrib.auth.context_processors.auth",
                            "django.contrib.messages.context_processors.messages",
                        ],
                    },
                },
            ],
            DATA_GENERATOR_CUSTOM_FIELD_VALUES={"auth.User": {"first_name": "somebody"}},
            LANGUAGE_CODE="en-us",
            TIME_ZONE="UTC",
            USE_I18N=True,
            USE_TZ=True,
            STATIC_URL="static/",
        )
        setup()


configure_django_settings()
