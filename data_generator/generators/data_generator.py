import json
from datetime import timedelta
from ipaddress import IPv4Address, IPv6Address
from random import choice, getrandbits, randint, sample, uniform
from string import ascii_letters, digits
from typing import Any, Dict
from uuid import UUID, uuid4

from django.db.models import Field
from django.utils.timezone import now


class ModelDataGenerator:
    """A class to handle generation of fake data for various Django field
    types.

    Attributes:
    ----------
    field_generators: dict
        Mapping of field type names to their respective generator methods.

    """

    def __init__(self):
        """Initialize the field generators."""
        self.field_generators = {
            "AutoField": self.generate_integer_field,
            "BigAutoField": self.generate_big_int_field,
            "BigIntegerField": self.generate_big_int_field,
            "BinaryField": self.generate_binary_field,
            "BooleanField": self.generate_boolean_field,
            "CharField": self.generate_string_field,
            "DateField": self.generate_date_field,
            "DateTimeField": self.generate_datetime_field,
            "DecimalField": self.generate_integer_field,
            "DurationField": self.generate_duration_field,
            "EmailField": self.generate_email,
            "FileField": self.generate_string_field,
            "FilePathField": self.generate_string_field,
            "FloatField": self.generate_float_field,
            "GenericIPAddressField": self.generate_ip_address_field,
            "ImageField": self.generate_image_field,
            "IntegerField": self.generate_integer_field,
            "JSONField": self.generate_json_field,
            "PositiveBigIntegerField": self.generate_integer_field,
            "PositiveIntegerField": self.generate_integer_field,
            "PositiveSmallIntegerField": self.generate_positive_small_int_field,
            "SlugField": self.generate_string_field,
            "SmallAutoField": self.generate_small_int_field,
            "SmallIntegerField": self.generate_small_int_field,
            "TextField": self.generate_string_field,
            "TimeField": self.generate_time_field,
            "URLField": self.generate_url_field,
            "UUIDField": self.generate_uuid_field,
        }

    def generate_string_field(
        self, field: Field, unique_values: Dict[str, Any], unique: bool = False
    ) -> str:
        """Generates a random string for CharField or similar string fields.

        Parameters
        ----------
        field : Field
            The field object, containing attributes like `max_length` to set string length limits.
        unique_values : Dict[str, Any]
            A dictionary to track previously generated values for ensuring uniqueness if needed.
        unique : bool, optional
            Indicates if the value must be unique (default is False).

        Returns
        -------
        str
            A randomly generated string.

        """
        charset = ascii_letters + digits
        default_length = 32 if unique else 16
        max_length = field.max_length or default_length
        value = "".join(choice(charset) for _ in range(min(max_length, default_length)))
        return (
            self._ensure_unique(value, unique_values, field.name) if unique else value
        )

    def generate_integer_field(
        self,
        field: Field,
        unique_values: Dict[str, Any],
        unique: bool = False,
        min_value: int = 0,
        max_value: int = 1000000,
    ) -> int:
        """Generates a random integer for IntegerField or similar fields.

        Parameters
        ----------
        field : Field
            The field object, for information purposes.
        unique_values : Dict[str, Any]
            A dictionary to track previously generated values for ensuring uniqueness if needed.
        unique : bool, optional
            Indicates if the value must be unique (default is False).
        min_value : int, optional
            Minimum value for the generated integer (default is 0).
        max_value : int, optional
            Maximum value for the generated integer (default is 1,000,000).

        Returns
        -------
        int
            A randomly generated integer within the specified range.

        """
        value = randint(min_value, max_value)
        return (
            self._ensure_unique(value, unique_values, field.name) if unique else value
        )

    def generate_big_int_field(
        self, field: Field, unique_values: Dict[str, Any], unique: bool = False
    ) -> int:
        """Generates a large integer, typically for BigIntegerField.

        Parameters
        ----------
        field : Field
            The field object, for information purposes.
        unique_values : Dict[str, Any]
            A dictionary to track previously generated values for ensuring uniqueness if needed.
        unique : bool, optional
            Indicates if the value must be unique (default is False).

        Returns
        -------
        int
            A randomly generated large integer.

        """
        return self.generate_integer_field(
            min_value=1_000_000,
            max_value=1_000_000_000,
            unique=unique,
            unique_values=unique_values,
            field=field,
        )

    def generate_small_int_field(
        self, field: Field, unique_values: Dict[str, Any], unique: bool = False
    ) -> int:
        """Generates a small integer, typically for SmallIntegerField.

        Parameters
        ----------
        field : Field
            The field object, for information purposes.
        unique_values : Dict[str, Any]
            A dictionary to track previously generated values for ensuring uniqueness if needed.
        unique : bool, optional
            Indicates if the value must be unique (default is False).

        Returns
        -------
        int
            A randomly generated small integer.

        """
        return self.generate_integer_field(
            min_value=-32767,
            max_value=32767,
            unique=unique,
            unique_values=unique_values,
            field=field,
        )

    def generate_positive_small_int_field(
        self, field: Field, unique_values: Dict[str, Any], unique: bool = False
    ) -> int:
        """Generates a positive small integer, typically for
        PositiveSmallIntegerField.

        Parameters
        ----------
        field : Field
            The field object, for information purposes.
        unique_values : Dict[str, Any]
            A dictionary to track previously generated values for ensuring uniqueness if needed.
        unique : bool, optional
            Indicates if the value must be unique (default is False).

        Returns
        -------
        int
            A randomly generated positive small integer.

        """
        return self.generate_integer_field(
            min_value=0,
            max_value=32767,
            unique=unique,
            unique_values=unique_values,
            field=field,
        )

    def generate_decimal_field(
        self,
        field: Field,
        unique_values: Dict[str, Any],
        unique: bool = False,
    ) -> float:
        """Generates a random decimal number for DecimalField with specific
        precision.

        Parameters
        ----------
        field : Field
            The field object, which includes attributes like `max_digits` and `decimal_places` for precision.
        unique_values : Dict[str, Any]
            A dictionary to track previously generated values for ensuring uniqueness if needed.
        unique : bool, optional
            Indicates if the value must be unique (default is False).

        Returns
        -------
        float
            A randomly generated decimal number rounded to the specified decimal places.

        """
        max_digits = field.max_digits
        decimal_places = field.decimal_places
        value = round(uniform(0, 10 ** (max_digits - decimal_places)), decimal_places)
        return (
            self._ensure_unique(value, unique_values, field.name) if unique else value
        )

    def generate_url_field(
        self, field: Field, unique_values: Dict[str, Any], unique: bool = False
    ) -> str:
        """Generates a random URL string, typically for URLField.

        Parameters
        ----------
        field : Field
            The field object, for information purposes.
        unique_values : Dict[str, Any]
            A dictionary to track previously generated values for ensuring uniqueness if needed.
        unique : bool, optional
            Indicates if the value must be unique (default is False).

        Returns
        -------
        str
            A randomly generated URL string.

        """
        domains = ["example.com", "testsite.org", "samplepage.net"]
        return f"https://{choice(domains)}/{self.generate_string_field(field, unique_values, unique)}"[
            : field.max_length
        ]

    @staticmethod
    def generate_float_field(*args, **kwargs) -> float:
        """Generates a random floating-point number for FloatField.

        Returns
        -------
        float
            A randomly generated floating-point number.

        """
        return uniform(0, 1000)

    @staticmethod
    def generate_binary_field(
        field: Field,
        unique_values: Dict[str, Any],
        unique: bool = False,
        max_length: int = 10,
    ) -> bytes:
        """Generates a random binary value, typically for BinaryField.

        Parameters
        ----------
        field : Field
            The field object, for information purposes.
        unique_values : Dict[str, Any]
            A dictionary to track previously generated values for ensuring uniqueness if needed.
        unique : bool, optional
            Indicates if the value must be unique (default is False).
        max_length : int, optional
            The maximum length of the binary data (default is 10).

        Returns
        -------
        bytes
            Randomly generated binary data of specified length.

        """
        return bytes(getrandbits(8) for _ in range(max_length))

    @staticmethod
    def generate_boolean_field(*args: Any, **kwargs: Any) -> bool:
        """Generates a random boolean value, typically for BooleanField.

        Returns
        -------
        bool
            A randomly generated boolean value (True or False).

        """
        return choice([True, False])

    @staticmethod
    def generate_date_field(*args: Any, **kwargs: Any) -> Any:
        """Generates the current date, typically for DateField.

        Returns
        -------
        datetime.date
            The current date.

        """
        return now().date()

    @staticmethod
    def generate_time_field(*args: Any, **kwargs: Any) -> Any:
        """Generates the current time, typically for TimeField.

        Returns
        -------
        datetime.time
            The current time.

        """
        return now().time()

    @staticmethod
    def generate_datetime_field(*args: Any, **kwargs: Any) -> Any:
        """Generates the current date and time, typically for DateTimeField.

        Returns
        -------
        datetime.datetime
            The current date and time.

        """
        return now()

    @staticmethod
    def generate_duration_field(*args: Any, **kwargs: Any) -> Any:
        """Generates a random time duration, typically for DurationField.

        Returns
        -------
        datetime.timedelta
            A randomly generated time duration.

        """
        return timedelta(seconds=randint(0, 86400))

    @staticmethod
    def generate_uuid_field(*args: Any, **kwargs: Any) -> UUID:
        """Generates a random UUID value, typically for UUIDField.

        Returns
        -------
        UUID
            A randomly generated UUID.

        """
        return uuid4()

    @staticmethod
    def generate_json_field(*args: Any, **kwargs: Any) -> str:
        """Generates a sample JSON structure as a string, typically for
        JSONField.

        Returns
        -------
        str
            A randomly generated JSON-formatted string.

        """
        sample_json = {
            "id": randint(1, 100),
            f"name_{randint(1, 100)}": "Sample-name",
            "status": choice(["active", "inactive", "pending"]),
            "score": round(uniform(0, 100), 2),
        }
        return json.dumps(sample_json)

    def generate_ip_address_field(
        self, field: Field, unique_values: Dict[str, Any], unique: bool = False
    ) -> str:
        """Generates a random IP address for GenericIPAddressField.

        Parameters
        ----------
        field : Field
            The field object, containing protocol information ('IPv4', 'IPv6', or 'both').
        unique_values : Dict[str, Any]
            A dictionary to track previously generated values for ensuring uniqueness if needed.
        unique : bool, optional
            Indicates if the value must be unique (default is False).

        Returns
        -------
        str
            A randomly generated IP address based on the specified protocol.

        """
        protocol = field.protocol  # 'both', 'IPv4', or 'IPv6'

        if protocol == "IPv4":
            ip_address = str(IPv4Address(randint(0, (1 << 32) - 1)))
        elif protocol == "IPv6":
            ip_address = str(IPv6Address(randint(0, (1 << 128) - 1)))
        else:  # 'both', pick randomly between IPv4 and IPv6
            ip_address = (
                str(IPv4Address(randint(0, (1 << 32) - 1)))
                if choice([True, False])
                else str(IPv6Address(randint(0, (1 << 128) - 1)))
            )

        return ip_address

    def generate_email(
        self, field: Field, unique_values: Dict[str, Any], unique: bool = False
    ) -> str:
        """Generates a random email address, typically for EmailField.

        Parameters
        ----------
        field : Field
            The field object, for information purposes.
        unique_values : Dict[str, Any]
            A dictionary to track previously generated values for ensuring uniqueness if needed.
        unique : bool, optional
            Indicates if the value must be unique (default is False).

        Returns
        -------
        str
            A randomly generated email address.

        """
        domains = [
            "example.com",
            "sample.org",
            "test.net",
            "mail.com",
            "gmail.com",
            "yahoo.com",
            "outlook.com",
            "hotmail.com",
            "protonmail.com",
            "aol.com",
        ]
        domain = choice(domains)
        username = f"user{self.generate_string_field(field, unique_values, unique)}"
        email = f"{username}@{domain}"
        return (
            self._ensure_unique_email(email, unique_values, field.name)
            if unique
            else email
        )

    def generate_image_field(
        self, field: Field, unique_values: Dict[str, Any], unique: bool = False
    ) -> str:
        """Generates a realistic image file path for ImageField.

        Parameters
        ----------
        field : Field
            The field object, for information purposes.
        unique_values : Dict[str, Any]
            A dictionary to track previously generated values for ensuring uniqueness if needed.
        unique : bool, optional
            Indicates if the value must be unique (default is False).

        Returns
        -------
        str
            A randomly generated file path for an image with a random extension.

        """
        extensions = ["jpg", "png", "gif"]
        return f"images/{self.generate_string_field(field, unique_values, unique)}.{choice(extensions)}"

    def _ensure_unique(
        self, value: Any, unique_values: Dict[str, Any], field_name: str
    ) -> Any:
        """Ensures that the generated value is unique for the specified field.

        If the generated value already exists in the unique_values dictionary,
        this method modifies it slightly to create a unique variant. It does this
        by either scrambling the characters in the case of a string or incrementing
        the value in the case of an integer.

        Parameters
        ----------
        value : Any
            The value to be checked for uniqueness.
        unique_values : Dict[str, Any]
            A dictionary to track previously generated values for ensuring uniqueness.
        field_name : str
            The name of the field for which uniqueness is being enforced.

        Returns
        -------
        Any
            A unique value for the specified field.

        Raises
        ------
        ValueError
            If the uniqueness cannot be ensured after 100 attempts.

        """
        attempt_count = 0
        while value in unique_values.get(field_name, []):
            if isinstance(value, str):
                value = "".join(sample(value, len(value)))
            elif isinstance(value, int):
                value += 1

            attempt_count += 1
            if attempt_count > 100:  # Fail-safe to avoid infinite loop
                break

        unique_values.setdefault(field_name, []).append(value)
        return value

    def _ensure_unique_email(
        self, email: str, unique_values: Dict[str, Any], field_name: str
    ) -> str:
        """Ensures that the generated email address is unique.

        If the generated email already exists in the unique_values dictionary,
        this method modifies the username part of the email to create a unique variant.

        Parameters
        ----------
        email : str
            The email address to be checked for uniqueness.
        unique_values : Dict[str, Any]
            A dictionary to track previously generated values for ensuring uniqueness.
        field_name : str
            The name of the field for which uniqueness is being enforced.

        Returns
        -------
        str
            A unique email address.

        """
        username, domain = email.split("@")
        counter = 1

        # Generate a unique email by appending a number to the username if it already exists
        while email in unique_values.get(field_name, []):
            unique_username = f"{username}{counter}"
            email = f"{unique_username}@{domain}"
            counter += 1

        unique_values.setdefault(field_name, []).append(email)
        return email


model_data_generator = ModelDataGenerator()
