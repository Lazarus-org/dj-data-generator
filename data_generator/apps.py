from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DataGeneratorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "data_generator"
    verbose_name = _("Data Generator")
