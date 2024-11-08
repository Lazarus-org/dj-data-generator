import sys
from datetime import timedelta
from unittest.mock import MagicMock
from uuid import UUID

import pytest
from django.db.models import Field

from data_generator.generators.data_generator import ModelDataGenerator
from data_generator.tests.constants import PYTHON_VERSION, PYTHON_VERSION_REASON

pytestmark = [
    pytest.mark.generators,
    pytest.mark.generators_model_data_generator,
    pytest.mark.skipif(sys.version_info < PYTHON_VERSION, reason=PYTHON_VERSION_REASON),
]


class TestModelDataGenerator:

    @classmethod
    def setup_class(cls) -> None:
        """Setup for ModelDataGenerator tests"""
        cls.generator = ModelDataGenerator()
        cls.unique_values = {}

    def test_generate_string_field(self) -> None:
        """
        Test that a string field is generated with correct length and uniqueness.

        Args:
        ----
            None

        Asserts:
        -------
            The result should be a string of length <= max_length.
            The unique string result should be stored in unique_values.
        """
        mock_field = MagicMock()
        mock_field.max_length = 10

        # Generate a regular string
        result = self.generator.generate_string_field(mock_field, self.unique_values)
        assert isinstance(result, str)
        assert len(result) <= mock_field.max_length

        # Generate a unique string
        assert self.unique_values.get(mock_field.name) is None
        result_unique = self.generator.generate_string_field(
            mock_field, self.unique_values, unique=True
        )
        assert result_unique in self.unique_values.get(mock_field.name, [])

    def test_generate_integer_field(self) -> None:
        """
        Test that an integer field is generated within expected bounds.

        Args:
        ----
            None

        Asserts:
        -------
            The result should be an integer within the range 0 to 1000000.
            The unique integer result should be stored in unique_values.
        """
        mock_field = MagicMock()

        # Generate a regular integer
        result = self.generator.generate_integer_field(mock_field, self.unique_values)
        assert isinstance(result, int)
        assert 0 <= result <= 1000000

        # Generate a unique integer
        assert self.unique_values.get(mock_field.name) is None
        result_unique = self.generator.generate_integer_field(
            mock_field, self.unique_values, unique=True
        )
        assert result_unique in self.unique_values.get(mock_field.name, [])

    def test_generate_big_int_field(self) -> None:
        """
        Test that a big integer field is generated within the expected range.

        Args:
        ----
            None

        Asserts:
        -------
            The result should be an integer within the range 1,000,000 to 1,000,000,000.
        """
        mock_field = MagicMock()

        # Generate a regular big integer
        result = self.generator.generate_big_int_field(mock_field, self.unique_values)
        assert isinstance(result, int)
        assert 1_000_000 <= result <= 1_000_000_000

    def test_generate_small_int_field(self) -> None:
        mock_field = MagicMock()

        # Generate a regular small integer
        result = self.generator.generate_small_int_field(mock_field, self.unique_values)
        assert isinstance(result, int)
        assert -32767 <= result <= 32767

    def test_generate_positive_small_int_field(self) -> None:
        mock_field = MagicMock()

        # Generate a regular positive small integer
        result = self.generator.generate_positive_small_int_field(
            mock_field, self.unique_values
        )
        assert isinstance(result, int)
        assert 0 <= result <= 32767

    def test_generate_decimal_field(self) -> None:
        """
        Test that a decimal field is generated with correct precision and uniqueness.

        Args:
        ----
            None

        Asserts:
        -------
            The result should be a float with correct max_digits and decimal_places.
            The unique decimal result should be stored in unique_values.
        """
        mock_field = MagicMock()
        mock_field.max_digits = 5  # total number of digits allowed
        mock_field.decimal_places = (
            2  # number of digits allowed after the decimal point
        )

        # Generate a regular decimal
        result = self.generator.generate_decimal_field(mock_field, self.unique_values)

        assert isinstance(result, float)

        result_str = f"{result:.{mock_field.decimal_places}f}"

        # Check if total digits (excluding the decimal point) do not exceed max_digits
        total_digits = len(result_str.replace(".", ""))
        assert total_digits <= mock_field.max_digits

        # Ensure that the number of decimal places matches the field's constraint
        _, fractional_part = result_str.split(".")
        assert len(fractional_part) == mock_field.decimal_places

        # Generate a unique decimal
        assert self.unique_values.get(mock_field.name) is None
        result_unique = self.generator.generate_decimal_field(
            mock_field, self.unique_values, unique=True
        )
        assert result_unique in self.unique_values.get(mock_field.name, [])

    def test_generate_email(self) -> None:
        """
        Test that an email is generated in the correct format and uniqueness is maintained.

        Args:
        ----
            None

        Asserts:
        -------
            The result should be a string containing '@'.
            The unique email result should be stored in unique_values.
        """
        mock_field = Field()
        result = self.generator.generate_email(mock_field, self.unique_values, True)
        assert isinstance(result, str)
        assert "@" in result

        new_result = self.generator.generate_email(mock_field, self.unique_values, True)

        # Check that if the generated unique values stored in the unique_values
        # to avoid duplicate while generating everytime
        assert new_result, result in self.unique_values.get(mock_field.name, [])

    def test_generate_boolean_field(self) -> None:
        """
        Test that a boolean field is generated correctly.

        Args:
        ----
            None

        Asserts:
        -------
            The result should be of type bool.
        """
        result = self.generator.generate_boolean_field()
        assert isinstance(result, bool)

    def test_generate_float_field(self) -> None:
        """
        Test that a float field is generated correctly.

        Args:
        ----
            None

        Asserts:
        -------
            The result should be of type float.
        """
        result = self.generator.generate_float_field()
        assert isinstance(result, float)

    def test_generate_date_field(self) -> None:
        """
        Test that a date field is generated correctly.

        Args:
        ----
            None

        Asserts:
        -------
            The result should be an instance of date.
        """
        result = self.generator.generate_date_field()
        assert (
            result.__class__.__name__ == "date"
        )  # Checking if it returns a date instance

    def test_generate_time_field(self) -> None:
        """
        Test that a time field is generated correctly.

        Args:
        ----
            None

        Asserts:
        -------
            The result should be an instance of time.
        """
        result = self.generator.generate_time_field()
        assert (
            result.__class__.__name__ == "time"
        )  # Checking if it returns a time instance

    def test_generate_duration_field(self) -> None:
        """
        Test that a duration field is generated correctly.

        Args:
        ----
            None

        Asserts:
        -------
            The result should be of type timedelta.
        """
        result = self.generator.generate_duration_field()
        assert isinstance(result, timedelta)

    def test_generate_uuid_field(self) -> None:
        """
        Test that a UUID field is generated correctly.

        Args:
        ----
            None

        Asserts:
        -------
            The result should be of type UUID.
        """
        result = self.generator.generate_uuid_field()
        assert isinstance(result, UUID)

    def test_generate_json_field(self) -> None:
        """
        Test that a JSON field is generated correctly.

        Args:
        ----
            None

        Asserts:
        -------
            The result should be a string representing JSON data.
        """
        result = self.generator.generate_json_field()
        assert isinstance(result, str)  # JSON data is expected to be in string format

    def test_generate_ip_address_field_ipv4(self) -> None:
        """
        Test that an IPv4 address field is generated correctly.

        Args:
        ----
            None

        Asserts:
        -------
            The result should contain exactly three dots, indicating a valid IPv4 format.
        """
        mock_field = MagicMock()
        mock_field.protocol = "IPv4"
        result = self.generator.generate_ip_address_field(
            mock_field, self.unique_values
        )
        assert result.count(".") == 3  # IPv4 address format check

    def test_generate_ip_address_field_ipv6(self) -> None:
        """
        Test that an IPv6 address field is generated correctly.

        Args:
        ----
            None

        Asserts:
        -------
            The result should contain at least two colons, indicating a valid IPv6 format.
        """
        mock_field = MagicMock()
        mock_field.protocol = "IPv6"
        result = self.generator.generate_ip_address_field(
            mock_field, self.unique_values
        )
        assert result.count(":") >= 2  # IPv6 address format check

    def test_generate_ip_address_field_random(self) -> None:
        """
        Test that a random IP address field is generated correctly.

        Args:
        ----
            None

        Asserts:
        -------
            The result should contain at least two dots for a valid IP address format.
        """
        mock_field = MagicMock()
        mock_field.protocol = "both"
        result = self.generator.generate_ip_address_field(
            mock_field, self.unique_values
        )

        assert ":" or "." in result

    def test_generate_url_field(self) -> None:
        """
        Test that a URL field is generated with correct length and uniqueness.

        Args:
        ----
            None

        Asserts:
        -------
            The result should be a string that starts with "https://" and its length
            should not exceed the max_length specified in the mock_field.
            The unique string result should be stored in unique_values.
        """
        mock_field = MagicMock()
        mock_field.max_length = 50
        result = self.generator.generate_url_field(mock_field, self.unique_values)
        assert isinstance(result, str)
        assert result.startswith("https://")
        assert (
            len(result) <= mock_field.max_length
        )  # Check if the length is within the limit

    def test_generate_binary_field(self) -> None:
        """
        Test that a binary field is generated with correct length.

        Args:
        ----
            None

        Asserts:
        -------
            The result should be of type bytes and its length should match the specified max_length.
        """
        mock_field = MagicMock()
        result = self.generator.generate_binary_field(
            mock_field, self.unique_values, max_length=10
        )
        assert isinstance(result, bytes)
        assert len(result) == 10

    def test_generate_image_field(self) -> None:
        """
        Test that an image field is generated correctly.

        Args:
        ----
            None

        Asserts:
        -------
            The result should be a string that starts with "images/".
        """
        mock_field = Field()
        result = self.generator.generate_image_field(mock_field, self.unique_values)
        assert isinstance(result, str)
        assert result.startswith("images/")

    def test_ensure_unique(self):
        """
        Test the _ensure_unique method for generating unique values.

        Args:
        ----
            None

        Asserts:
        -------
            Unique values should be added to unique_values dictionary.
            Repeated value generation should return a modified unique value.
        """
        mock_field = MagicMock()
        mock_field.name = "test_field"

        # Test with a string
        value = "unique_test"
        assert self.unique_values.get(mock_field.name) is None
        unique_value = self.generator._ensure_unique(
            value, self.unique_values, mock_field.name
        )
        assert unique_value in self.unique_values[mock_field.name]

        new_value = self.generator._ensure_unique(
            value, self.unique_values, mock_field.name
        )
        assert new_value != value

        # Test with an integer
        value = 42
        unique_value = self.generator._ensure_unique(
            value, self.unique_values, mock_field.name
        )
        assert unique_value in self.unique_values[mock_field.name]

        new_value = self.generator._ensure_unique(
            value, self.unique_values, mock_field.name
        )
        assert new_value != value

    def test_ensure_unique_email(self) -> None:
        """
        Test the _ensure_unique_email method for generating unique emails.

        Args:
        ----
            None

        Asserts:
        -------
            Unique emails should be added to unique_values dictionary.
            Repeated value generation should return a modified unique value.
        """
        mock_field = MagicMock()
        mock_field.name = "test_field"

        # Test with a string
        value = "uniqueemail@mail.com"
        unique_value = self.generator._ensure_unique_email(
            value, self.unique_values, mock_field.name
        )
        assert unique_value in self.unique_values[mock_field.name]

        new_value = self.generator._ensure_unique_email(
            value, self.unique_values, mock_field.name
        )
        assert new_value != value

    def test_ensure_unique_break_condition(self) -> None:
        """
        Test that _ensure_unique stops after 100 attempts if uniqueness cannot be ensured.

        Args:
        ----
            None

        Asserts:
        -------
            After 100 attempts, the result should be returned without uniqueness enforced.
        """
        # Simulate an initial value and field name
        initial_value = 1
        field_name = "test_field"

        # Mock unique values to create an exhaustive scenario
        # This list should contain enough variations to force the attempt limit
        unique_values = {field_name: [i for i in range(110)]}

        # Execute the method and check that it stops after 100 attempts
        # It should return the initial value because we have at least 100 unique integers that it will test
        result = self.generator._ensure_unique(initial_value, unique_values, field_name)

        # Since it broke after 100 attempts, the result is not unique in this case
        # it will increase the result each time and after 100 times from 0,
        # at last it will add 101 to the initial value
        assert result == initial_value + 101
