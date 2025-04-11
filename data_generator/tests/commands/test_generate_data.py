import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db.models import CASCADE, BooleanField, ForeignKey, OneToOneField

from data_generator.management.commands.generate_data import Command
from data_generator.tests.constants import PYTHON_VERSION, PYTHON_VERSION_REASON

pytestmark = [
    pytest.mark.commands,
    pytest.mark.commands_generate_data,
    pytest.mark.skipif(sys.version_info < PYTHON_VERSION, reason=PYTHON_VERSION_REASON),
]


@pytest.mark.django_db
class TestGenerateDataCommand:
    @patch("builtins.input", side_effect=["y"])
    def test_command_with_defaults(self, mock_input: MagicMock) -> None:
        """
        Test command execution with default arguments.

        Args:
        ----
            None

        Asserts:
        -------
            The output should indicate that data generation has started and completed.
        """
        out = StringIO()
        call_command("generate_data", num_records=2, stdout=out)

        assert "Generating data for model:" in out.getvalue()
        assert "Done!" in out.getvalue()

    @patch("builtins.input", side_effect=["n"])
    def test_command_confirmation_rejection(self, mock_confirm: MagicMock) -> None:
        """
        Test command execution when the user rejects the confirmation prompt.

        Args:
        ----
            None

        Asserts:
        -------
            The output should indicate that the command was canceled and settings need adjustment.
        """
        out = StringIO()
        call_command("generate_data", stdout=out)

        assert "Re-run this command after adjusting the settings." in out.getvalue()

    @patch("builtins.input", side_effect=["invalid", "n"])
    def test_invalid_input(self, mock_input: MagicMock) -> None:
        """
        Test that the command handles invalid user input and prompts again.

        Args:
        ----
            None

        Asserts:
        -------
            The output should indicate that the input was invalid and prompt for correct input.
        """
        out = StringIO()
        call_command("generate_data", stdout=out)

        assert "Invalid input. Please type 'y' (Yes) or 'n' (No)." in out.getvalue()

    def test_invalid_num_records(self) -> None:
        """
        Test command with an invalid number of records.

        Args:
        ----
            None

        Asserts:
        -------
            The output should indicate that the number of records is invalid.
        """
        out = StringIO()
        call_command("generate_data", num_records=-1, stdout=out)

        assert "Invalid value for 'num-records': -1" in out.getvalue()

    def test_skip_confirmation_flag(self) -> None:
        """
        Test command with the --skip-confirmation flag.

        Args:
        ----
            None

        Asserts:
        -------
            The output should indicate that data generation has started and completed without confirmation.
        """
        out = StringIO()
        call_command("generate_data", num_records=2, skip_confirmation=True, stdout=out)

        assert "Generating data for model:" in out.getvalue()
        assert "Done!" in out.getvalue()

    def test_no_models_found(self) -> None:
        """
        Test behavior when no models are found to generate data.

        Args:
        ----
            None

        Asserts:
        -------
            The output should indicate that no models were found for data generation.
        """
        with patch("django.apps.apps.get_models", return_value=[]):
            out = StringIO()
            call_command("generate_data", stdout=out)

        assert "No models found to generate fake data." in out.getvalue()

    def test_with_specific_model(self) -> None:
        """
        Test behavior when specific model is passed to generate data.

        Args:
        ----
            None

        Asserts:
        -------
            The output should indicate that the data were generated for the specific model.
        """
        out = StringIO()
        call_command("generate_data", num_records=1, model="auth.User", stdout=out)

        assert "Done!" in out.getvalue()

    def test_invalid_model(self) -> None:
        """
        Test behavior when invalid model passed to generate data.

        Args:
        ----
            None

        Asserts:
        -------
            The output should indicate that the model were not found for data generation.
        """
        out = StringIO()
        call_command("generate_data", model="Invalid", stdout=out)

        assert (
            "Please ensure that the model name is in the correct format"
            in out.getvalue()
        )

    @patch(
        "data_generator.management.commands.generate_data.Command._warn_high_record_count",
        return_value=False,
    )
    def test_warn_with_specific_model(self, mock_warning: MagicMock) -> None:
        """
        Test behavior when specific model is passed to generate data with large num record.

        Args:
        ----
            None

        Asserts:
        -------
            The output should indicate that the warning returns about large num records.
        """
        out = StringIO()
        call_command("generate_data", num_records=110000, model="auth.User", stdout=out)

        assert "Operation canceled by user." in out.getvalue()

    @patch(
        "data_generator.management.commands.generate_data.Command._warn_high_record_count",
        return_value=False,
    )
    @patch(
        "data_generator.management.commands.generate_data.Command._confirm_models",
        return_value=True,
    )
    def test_high_num_records_warning_with_confirmation_rejection(
        self, mock_confirm: MagicMock, mock_warning: MagicMock
    ) -> None:
        """
        Test that the command stops operation if the user rejects the high record count warning.

        Args:
        ----
            None

        Asserts:
        -------
            The output should indicate that the operation was canceled by the user.
        """
        out = StringIO()
        call_command("generate_data", num_records=110000, stdout=out)

        assert "Operation canceled by user." in out.getvalue()

    @patch("builtins.input", side_effect=["n"])
    def test_high_num_records_warning(self, mock_input: MagicMock) -> None:
        """
        Test that the command returns correct output if the user passes a high number of records.

        Args:
        ----
            None

        Asserts:
        -------
            The output should indicate that the warning for high record count was not confirmed.
        """
        out = StringIO()
        cmd = Command()
        cmd.stdout = out

        result = cmd._warn_high_record_count()
        assert result is False

    @patch("builtins.input", side_effect=["y"])
    @patch("django.apps.apps.get_models")
    def test_generate_data_with_mock_model(
        self, mock_get_models: MagicMock, mock_input: MagicMock
    ) -> None:
        """
        Test data generation with a mock model object that handles OneToOne relation.

        Args:
        ----
            None

        Asserts:
        -------
            The output should indicate that data generation has started and completed for both models
        """
        # Create a mock model-like object
        mock_model = MagicMock()
        mock_model.__name__ = "MockModel"
        mock_model._meta.app_label = "app"

        # Related model mock
        rel_model = MagicMock()
        rel_model.__name__ = "MockRelModel"
        rel_model._meta.app_label = "app"
        rel_model._meta.fields = [BooleanField(default=True)]
        rel_model._default_manager.bulk_create = MagicMock()
        rel_model._default_manager.order_by.return_value.values_list.return_value = [
            1
        ]  # a test id

        mock_model._meta.fields = [OneToOneField(rel_model, on_delete=CASCADE)]
        mock_model._default_manager.bulk_create = MagicMock()

        mock_get_models.return_value = [mock_model, LogEntry]

        out = StringIO()
        call_command("generate_data", num_records=2, stdout=out)

        assert "Generating data for model: app.MockModel" in out.getvalue()
        assert "Generating data for model: app.MockRelModel" in out.getvalue()
        assert "Done!" in out.getvalue()

    @patch("builtins.input", side_effect=["y"])
    @patch("django.apps.apps.get_models")
    def test_generate_data_with_foreign_key(
        self, mock_get_models: MagicMock, mock_input: MagicMock
    ) -> None:
        """
        Test data generation with a mock model object that handles ForeignKey relation.

        Args:
        ----
            None

        Asserts:
        -------
            The output should indicate that data generation has started and completed for both models.
        """
        # Create a mock model-like object
        mock_model = MagicMock()
        mock_model.__name__ = "MockModel"
        mock_model._meta.app_label = "app"

        # Related model mock
        rel_model = MagicMock()
        rel_model.__name__ = "MockRelModel"
        rel_model._meta.app_label = "app"
        rel_model._meta.fields = [BooleanField(default=True)]
        rel_model._default_manager.bulk_create = MagicMock()

        mock_model._meta.fields = [
            ForeignKey(rel_model, on_delete=CASCADE),
            ForeignKey(User, on_delete=CASCADE),

        ]
        mock_model._default_manager.bulk_create = MagicMock()

        mock_get_models.return_value = [mock_model, rel_model]

        out = StringIO()
        call_command("generate_data", num_records=1, stdout=out)

        assert "Generating data for model: app.MockModel" in out.getvalue()
        assert "Generating data for model: app.MockRelModel" in out.getvalue()
        assert "Done!" in out.getvalue()

    @patch("builtins.input", side_effect=["y"])
    @patch("django.apps.apps.get_models")
    def test_generate_data_with_foreign_key_user_model(
        self, mock_get_models: MagicMock, mock_input: MagicMock
    ) -> None:
        """
        Test data generation with User model object that handles ForeignKey relation.

        Args:
        ----
            None

        Asserts:
        -------
            The output should indicate that data generation has started and completed for both models.
        """
        # Create a mock model-like object
        mock_model = MagicMock()
        mock_model.__name__ = "MockModel"
        mock_model._meta.app_label = "app"

        mock_model._meta.fields = [
            ForeignKey(User, on_delete=CASCADE),

        ]
        mock_model._default_manager.bulk_create = MagicMock()

        mock_get_models.return_value = [mock_model]

        out = StringIO()
        call_command("generate_data", num_records=1, stdout=out)

        assert "Generating data for model: app.MockModel" in out.getvalue()
        assert "Generating data for model: auth.User" in out.getvalue()
        assert "Done!" in out.getvalue()
