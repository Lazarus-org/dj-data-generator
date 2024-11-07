import sys
from random import choice
from typing import Any, Dict, List, Optional

from django.apps import apps
from django.core.management.base import BaseCommand

from data_generator.constants.ansi_colors import colors
from data_generator.generators.data_generator import model_data_generator
from data_generator.settings.conf import config


class Command(BaseCommand):
    """Management command to generate fake data for all models within a Django project.

    This command generates a specified number of records per model, skipping
    internal Django models, and provides options to skip confirmation prompts
    and customize the number of records per model.
    """

    help = "Generate fake data for all models"

    def add_arguments(self, parser) -> None:
        """Add optional arguments to the command parser.

        Args:
        ----
            parser: The argument parser instance to which the arguments are added.

        """
        parser.add_argument(
            "--num-records",
            type=int,
            default=100,
            help="Number of records to generate per model",
        )
        parser.add_argument(
            "--skip-confirmation",
            action="store_true",
            help="Skip the confirmation prompt if no needed.",
        )
        parser.add_argument(
            "--model",
            type=str,
            help="Name of a specific model to generate data for (e.g., 'app_name.ModelName').",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Handle the command execution.

        Args:
        ----
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.
        """
        self.num_records = options.get("num_records")
        skip_confirm = options.get("skip_confirmation")
        specified_model = options.get("model")
        self.records_threshold = 100000
        self.processed_models = set()
        self.related_instance_cache = dict()
        self.django_models = [
            "admin.LogEntry",
            "auth.Permission",
            "contenttypes.ContentType",
            "sessions.Session",
        ]

        if self.num_records < 1:
            self.stdout.write(
                self.style.ERROR(
                    f"Invalid value for 'num-records': {self.num_records}. "
                    "The minimum allowed value is 1. Please enter a value greater than or equal to 1."
                )
            )
            return

        if specified_model:
            model = self._get_model(specified_model)
            if model:
                if not skip_confirm and not self._check_record_threshold():
                    return
                self.generate_data_for_model(model)
            return

        models = self._get_target_models()
        if not models:
            self.stdout.write(
                self.style.WARNING("No models found to generate fake data.")
            )
            return

        if not skip_confirm:
            if not self._confirm_models(models):
                self._display_exclude_instructions()
                return

            if not self._check_record_threshold():
                return

        for model in models:
            self.generate_data_for_model(model)

    def _get_model(self, model_name: str) -> Any:
        """Retrieve a specific model by its name.

        Args:
        ----
            model_name: The name of the model in 'app_label.ModelName' format.

        Returns:
        -------
            Model class if found, else None.
        """
        try:
            return apps.get_model(model_name)
        except (ValueError, LookupError):
            error_message = (
                f"Error: The model '{model_name}' could not be found."
                f"\nPlease ensure that the model name is in the correct format "
                f"'app_label.ModelName' and the app is installed."
            )
            self.stdout.write(self.style.ERROR(error_message))

    def _get_target_models(self) -> List[Any]:
        """Retrieve a list of models for data generation, excluding internal Django models.

        Returns:
        -------
            List[Model]: List of Django models for data generation.
        """
        return [
            model
            for model in apps.get_models()
            if f"{model._meta.app_label}.{model.__name__}"
            not in config.exclude_models + self.django_models
            and model._meta.app_label not in config.exclude_apps
        ]

    def generate_data_for_model(self, model: Any) -> None:
        """Generate and bulk-create data instances for a specific model.

        Args:
        ----
            model (Model): The Django model class to generate data for.
        """
        model_name = model.__name__
        if model in self.processed_models or model_name in self.django_models:
            return

        batch_size = max(100, self.num_records // 10)

        self.stdout.write(f"\nGenerating data for model: {model_name}")
        unique_values: Dict = {}
        self._display_progress(0, self.num_records, model_name)
        for i in range(0, self.num_records, batch_size):
            instances = [
                model(**self._generate_model_data(model, unique_values))
                for _ in range(min(batch_size, self.num_records - i))
            ]
            model.objects.bulk_create(instances, ignore_conflicts=True)
            self._display_progress(i + len(instances), self.num_records, model_name)

        self.stdout.write(f"\nDone!")

        # Mark the model as processed
        self.processed_models.add(model)
        # Clear the related instances cache after generating data
        self.related_instance_cache.clear()

    def _generate_model_data(self, model: Any, unique_values: Dict) -> Dict[str, Any]:
        """Generate a dictionary of field data for a model instance, handling unique and related fields.

        Args:
        ----
            model (Model): The Django model for which data is generated.

        Returns:
        -------
            Dict[str, Any]: A dictionary of field values for model instantiation.
        """
        data: Dict = {}
        model_name = model.__name__

        for field in model._meta.fields:
            field_name = field.name

            if (
                model_name in config.custom_field_values
                and field_name in config.custom_field_values[model_name]
            ):
                data[field_name] = config.custom_field_values[model_name][field_name]
                continue

            if field.primary_key:
                continue

            generator = model_data_generator.field_generators.get(type(field).__name__)
            if field.is_relation:
                related_model = field.related_model
                self.generate_data_for_model(related_model)
                if related_model not in self.related_instance_cache:
                    self.related_instance_cache[related_model] = list(
                        related_model.objects.order_by("-id").values_list(
                            "id", flat=True
                        )[: self.num_records]
                    )

                rel_id_field = f"{field.name}_id"
                if field.one_to_one:
                    data[rel_id_field] = self.get_unique_rel_instance(related_model)
                elif field.many_to_one:
                    data[rel_id_field] = self.get_random_rel_instance(related_model)

            elif field.unique:
                data[field_name] = generator(field, unique_values, True)

            elif field.has_default():
                continue

            else:
                data[field_name] = generator(field, unique_values)

        return data

    def get_random_rel_instance(self, model: Any) -> Optional[int]:
        """Retrieve a random related instance ID from the cache for a model.

        Args:
        ----
            model (Model): The related Django model.

        Returns:
        -------
            Optional[int]: A random instance ID or None if no instances exist.
        """
        return (
            choice(self.related_instance_cache[model])
            if self.related_instance_cache[model]
            else None
        )

    def get_unique_rel_instance(self, model: Any) -> Optional[int]:
        """Retrieve a unique related instance ID and remove it from the cache to avoid duplication.

        Args:
        ----
            model (Model): The related Django model.

        Returns:
        -------
            Optional[int]: A unique instance ID or None if no instances exist.
        """
        if self.related_instance_cache[model]:
            instance_id = choice(self.related_instance_cache[model])
            self.related_instance_cache[model].remove(instance_id)
            return instance_id
        return None

    def _confirm_models(self, related_models: List[Any]) -> bool:
        """Display the list of models for the user to review and ask for confirmation.

        Args:
        ----
            models (List): A list of models to be displayed.

        Returns:
            bool: True if the user confirms, False otherwise.
        ------

        """
        self.stdout.write(self.style.WARNING("The following models were found:"))
        for i, model in enumerate(related_models, 1):
            self.stdout.write(f"{i}. {model}")
        self.stdout.write("\nAre these the correct target models?", ending="")
        return self._confirm_proceed()

    def _warn_high_record_count(self) -> bool:
        """Warn the user if a large record count is specified, prompting confirmation.

        Returns:
        -------
            bool: True if the user confirms, False otherwise.
        """
        warning_message = (
            "\nWARNING: You have set --num-records to a large value "
            "and may have multiple models to generate data for.\nThis may require a significant amount of memory "
            "and system resources. Are you sure you want to continue?\n"
        )
        self.stdout.write(self.style.WARNING(warning_message))
        return self._confirm_proceed()

    def _confirm_proceed(self) -> bool:
        """Prompt the user for confirmation to proceed with the data
        generation.

        Returns:
        -------
            bool: True if the user confirms, False otherwise.

        """
        while True:
            user_input = (
                input("\nType 'y' to proceed or 'n' to cancel the operation:")
                .strip()
                .lower()
            )
            if user_input in ["y", "yes"]:
                return True
            elif user_input in ["n", "no"]:
                return False
            self.stdout.write(
                self.style.ERROR("Invalid input. Please type 'y' (Yes) or 'n' (No).")
            )

    def _check_record_threshold(self) -> bool:
        """Check if the number of records exceeds the threshold and warn the user.

        Returns:
        -------
            bool: True if the user confirms to proceed, False if they cancel.
        """
        if self.num_records > self.records_threshold:
            if not self._warn_high_record_count():
                self.stdout.write(self.style.WARNING("Operation canceled by user."))
                return False

        return True

    def _display_exclude_instructions(self) -> None:
        """Display instructions for excluding apps or models from data generation."""
        self.stdout.write(
            self.style.WARNING(
                "\nTo exclude certain apps or models, modify the settings:"
            )
        )
        self.stdout.write("1. Adjust 'DATA_GENERATOR_EXCLUDE_APPS'")
        self.stdout.write("2. Adjust 'DJANGO_GENERATOR_EXCLUDE_MODELS'")
        self.stdout.write("3. Re-run this command after adjusting the settings.")

    def _display_progress(self, current: int, total: int, model_name: str) -> None:
        """Display a progress bar for data generation in the terminal.

        Args:
        ----
            current (int): The current number of records generated.
            total (int): The total number of records to generate.
            model_name (str): The name of the model being processed.
        """
        bar_length = 10  # Length of the progress bar
        progress = current / total
        block = int(bar_length * progress)
        bar = f"{colors.GREEN}█ {colors.RESET}" * block + "─ " * (bar_length - block)
        sys.stdout.write(
            f"\r[ {bar}] {int(progress * 100)}% completed for {model_name}"
        )
        sys.stdout.flush()
