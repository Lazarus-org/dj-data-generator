from typing import List

from django.apps import apps
from django.core.checks import Error

from data_generator.constants.types import CustomFieldValues


def validate_str_list(
    elements: List[str],
    config_name: str,
    allow_empty: bool = False,
    is_for_model: bool = False,
) -> List[Error]:
    errors = []
    if not isinstance(elements, list):
        errors.append(
            Error(
                f"{config_name} is not a list.",
                hint=f"Ensure {config_name} is a list of strings.",
                id=f"data_generator.E002_{config_name}",
            )
        )
    elif not elements and not allow_empty:
        errors.append(
            Error(
                f"{config_name} is an empty list.",
                hint=f"Ensure {config_name} contains at least one valid string.",
                id=f"data_generator.E003_{config_name}",
            )
        )
    else:
        for element in elements:
            if not isinstance(element, str):
                errors.append(
                    Error(
                        f"Invalid type(s) in {config_name}: {element} is not an string.",
                        hint=f"Ensure all elements in {config_name} are strings.",
                        id=f"data_generator.E004_{config_name}",
                    )
                )
                continue

            if is_for_model:
                error = validate_model_existence(element, config_name)
                if error:
                    errors.append(error)
                    continue

    return errors


def validate_custom_field_values(
    config: CustomFieldValues, config_name: str
) -> List[Error]:
    errors = []

    if not isinstance(config, dict):
        errors.append(
            Error(
                f"{config_name} should be a dictionary.",
                hint=f"Ensure {config_name} is a dictionary where each key is a model name.",
                id=f"data_generator.E005_{config_name}",
            )
        )
        return errors

    for model_name, fields in config.items():
        if not isinstance(model_name, str):
            errors.append(
                Error(
                    f"Model name '{model_name}' in {config_name} is not a string.",
                    hint="Each model name should be a string.",
                    id=f"data_generator.E006_{config_name}",
                )
            )
            continue

        error = validate_model_existence(model_name, config_name)
        if error:
            errors.append(error)
            continue

        if not isinstance(fields, dict):
            errors.append(
                Error(
                    f"Fields configuration for model '{model_name}' in {config_name} should be a dictionary.",
                    hint="Each model's fields configuration should be a dictionary of field-value pairs.",
                    id=f"data_generator.E008_{config_name}",
                )
            )
            continue
        model = apps.get_model(model_name)
        model_field_names = {f.name for f in model._meta.fields}
        for field_name, value in fields.items():
            if not isinstance(field_name, str):
                errors.append(
                    Error(
                        f"Field name '{field_name}' in model '{model_name}' is not a string.",
                        hint="Each field name should be a string.",
                        id=f"data_generator.E009_{config_name}",
                    )
                )
                continue

            if field_name not in model_field_names:
                errors.append(
                    Error(
                        f"Field '{field_name}' does not exist in model '{model_name}'.",
                        hint="Ensure the field name is correct and exists in the model.",
                        id=f"data_generator.E0010_{config_name}",
                    )
                )

    return errors


def validate_model_existence(model: str, config_name: str) -> Error:
    """Validate that the specified model exists in the Django project.

    Args:
    ----
        model (str): The model name in 'app_label.ModelName' format.
        config_name (str): The configuration name where the model is specified.

    Returns:
    -------
        Optional[Error]: An error object if the model is not found; otherwise, None.
    """
    try:
        apps.get_model(model)
    except (LookupError, ValueError):
        return Error(
            f"Model '{model}' specified in {config_name} does not exist.",
            hint="Ensure the model name is correct and defined with 'app_label.ModelName' in your project.",
            id=f"data_generator.E007_{config_name}",
        )
