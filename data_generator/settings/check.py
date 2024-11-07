from typing import Any, List

from django.core.checks import Error, register

from data_generator.settings.conf import config
from data_generator.validators.config_validators import (
    validate_custom_field_values,
    validate_str_list,
)


@register()
def check_data_generator_settings(app_configs: Any, **kwargs: Any) -> List[Error]:
    """Check and validate data generator settings in the Django configuration.

    This function performs validation of various related settings
    defined in the Django settings. It returns a list of errors if any issues are found.

    Parameters:
    -----------
    app_configs : Any
        Passed by Django during checks (not used here).

    kwargs : Any
        Additional keyword arguments for flexibility.

    Returns:
    --------
    List[Error]
        A list of `Error` objects for any detected configuration issues.

    """
    errors: List[Error] = []

    errors.extend(
        validate_str_list(
            config.exclude_apps,
            f"{config.prefix}EXCLUDE_APPS",
            True,
        )
    )
    errors.extend(
        validate_str_list(
            config.exclude_models,
            f"{config.prefix}EXCLUDE_MODELS",
            True,
            True,
        )
    )
    errors.extend(
        validate_custom_field_values(
            config.custom_field_values, f"{config.prefix}CUSTOM_FIELD_VALUES"
        )
    )

    return errors
