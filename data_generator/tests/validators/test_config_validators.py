import sys

import pytest

from data_generator.tests.constants import PYTHON_VERSION, PYTHON_VERSION_REASON
from data_generator.validators.config_validators import (
    validate_custom_field_values,
    validate_str_list,
)

pytestmark = [
    pytest.mark.validators,
    pytest.mark.config_validators,
    pytest.mark.skipif(sys.version_info < PYTHON_VERSION, reason=PYTHON_VERSION_REASON),
]


class TestConfigValidators:
    def test_valid_list(self) -> None:
        """
        Test that a valid list of strings returns no errors.

        Args:
        ----
            None

        Asserts:
        -------
            The result should have no errors.
        """
        errors = validate_str_list(["field1", "field2"], "SOME_LIST_SETTING")
        assert not errors  # No errors should be returned

    def test_invalid_list_type(self) -> None:
        """
        Test that a non-list setting returns an error.

        Args:
        ----
            None

        Asserts:
        -------
            The result should contain one error with the expected error ID.
        """
        errors = validate_str_list("not_a_list", "SOME_LIST_SETTING")  # type: ignore
        assert len(errors) == 1
        assert errors[0].id == "data_generator.E002_SOME_LIST_SETTING"

    def test_empty_list(self) -> None:
        """
        Test that an empty list returns an error.

        Args:
        ----
            None

        Asserts:
        -------
            The result should contain one error with the expected error ID.
        """
        errors = validate_str_list([], "SOME_LIST_SETTING")
        assert len(errors) == 1
        assert errors[0].id == "data_generator.E003_SOME_LIST_SETTING"

    def test_invalid_element_in_list(self) -> None:
        """
        Test that a list containing a non-string element returns an error.

        Args:
        ----
            None

        Asserts:
        -------
            The result should contain one error with the expected error ID.
        """
        errors = validate_str_list([123, "valid_field"], "SOME_LIST_SETTING")
        assert len(errors) == 1
        assert errors[0].id == "data_generator.E004_SOME_LIST_SETTING"

    def test_invalid_model_in_list(self) -> None:
        """
        Test that a list containing a invalid model element returns an error.

        Args:
        ----
            None

        Asserts:
        -------
            The result should contain one error with the expected error ID.
        """
        errors = validate_str_list(
            ["InvalidModel"], "SOME_LIST_SETTING", is_for_model=True
        )
        assert len(errors) == 1
        assert errors[0].id == "data_generator.E007_SOME_LIST_SETTING"

    def test_valid_custom_field_values(self) -> None:
        """
        Test that a valid custom field values configuration returns no errors.

        Args:
        ----
            None

        Asserts:
        -------
            The result should have no errors.
        """
        config = {"auth.User": {"first_name": "value1", "last_name": "value2"}}
        errors = validate_custom_field_values(config, "CUSTOM_FIELD_VALUES")
        assert not errors

    def test_invalid_custom_field_type(self) -> None:
        """
        Test that a non-dictionary config returns an error.

        Args:
        ----
            None

        Asserts:
        -------
            The result should contain one error with the expected error ID.
        """
        errors = validate_custom_field_values("not_a_dict", "CUSTOM_FIELD_VALUES")  # type: ignore
        assert len(errors) == 1
        assert errors[0].id == "data_generator.E005_CUSTOM_FIELD_VALUES"

    def test_non_string_model_name(self) -> None:
        """
        Test that a non-string model name in the config returns an error.

        Args:
        ----
            None

        Asserts:
        -------
            The result should contain one error with the expected error ID.
        """
        config = {123: {"field1": "value1"}}  # Invalid model name
        errors = validate_custom_field_values(config, "CUSTOM_FIELD_VALUES")  # type: ignore
        assert len(errors) == 1
        assert errors[0].id == "data_generator.E006_CUSTOM_FIELD_VALUES"

    def test_non_existent_model(self) -> None:
        """
        Test that specifying a model that does not exist returns an error.

        Args:
        ----
            None

        Asserts:
        -------
            The result should contain one error with the expected error ID.
        """
        config = {"NonExistentModel": {"field1": "value1"}}
        errors = validate_custom_field_values(config, "CUSTOM_FIELD_VALUES")
        assert len(errors) == 1
        assert errors[0].id == "data_generator.E007_CUSTOM_FIELD_VALUES"

    def test_invalid_fields_type(self) -> None:
        """
        Test that a non-dictionary fields configuration returns an error.

        Args:
        ----
            None

        Asserts:
        -------
            The result should contain one error with the expected error ID.
        """
        config = {"auth.User": "not_a_dict"}
        errors = validate_custom_field_values(config, "CUSTOM_FIELD_VALUES")  # type: ignore
        assert len(errors) == 1
        assert errors[0].id == "data_generator.E008_CUSTOM_FIELD_VALUES"

    def test_non_string_field_name(self) -> None:
        """
        Test that a non-string field name returns an error.

        Args:
        ----
            None

        Asserts:
        -------
            The result should contain one error with the expected error ID.
        """
        config = {"auth.User": {123: "value"}}  # Non-string field name
        errors = validate_custom_field_values(config, "CUSTOM_FIELD_VALUES")  # type: ignore
        assert len(errors) == 1
        assert errors[0].id == "data_generator.E009_CUSTOM_FIELD_VALUES"

    def test_non_existent_field(self) -> None:
        """
        Test that specifying a field that does not exist on the model returns an error.

        Args:
        ----
            None

        Asserts:
        -------
            The result should contain one error with the expected error ID.
        """
        config = {"auth.User": {"non_existent_field": "value"}}
        errors = validate_custom_field_values(config, "CUSTOM_FIELD_VALUES")
        assert len(errors) == 1
        assert errors[0].id == "data_generator.E0010_CUSTOM_FIELD_VALUES"
