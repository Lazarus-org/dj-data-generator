from typing import Any, Dict, List

from django.conf import settings

from data_generator.constants.default_settings import DefaultCommandSettings
from data_generator.constants.types import CustomFieldValues


class DataGeneratorConfig:
    """A configuration handler for the Django Data Generator, allowing settings
    to be dynamically loaded from Django settings with defaults provided
    through `DefaultCommandSettings`.

    Attributes:
        exclude_apps (List[str]): A list of apps excluded from data generation.
        exclude_models (List[str]): A list of models excluded from data generation.
        exclude_models (Dict[str, Dict[str, Any]]): A dict of models with field-value pairs used for data generation.

    """

    prefix = "DATA_GENERATOR_"

    default_command_settings: DefaultCommandSettings = DefaultCommandSettings()

    def __init__(self) -> None:
        """Initialize the DataGeneratorConfig, loading values from Django
        settings or falling back to the default settings."""

        self.exclude_apps: List[str] = self.get_setting(
            f"{self.prefix}EXCLUDE_APPS",
            self.default_command_settings.exclude_apps,
        )
        self.exclude_models: List[str] = self.get_setting(
            f"{self.prefix}EXCLUDE_MODELS",
            self.default_command_settings.exclude_models,
        )
        self.custom_field_values: CustomFieldValues = self.get_setting(
            f"{self.prefix}CUSTOM_FIELD_VALUES",
            self.default_command_settings.custom_field_values,
        )

    def get_setting(self, setting_name: str, default_value: Any) -> Any:
        """Retrieve a setting from Django settings with a default fallback.

        Args:
            setting_name (str): The name of the setting to retrieve.
            default_value (Any): The default value to return if the setting is not found.

        Returns:
            Any: The value of the setting or the default value if not found.

        """
        return getattr(settings, setting_name, default_value)


config: DataGeneratorConfig = DataGeneratorConfig()
