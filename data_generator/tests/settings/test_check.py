import sys
from unittest.mock import MagicMock, patch

import pytest

from data_generator.settings.check import check_data_generator_settings
from data_generator.tests.constants import PYTHON_VERSION, PYTHON_VERSION_REASON

pytestmark = [
    pytest.mark.settings,
    pytest.mark.settings_check,
    pytest.mark.skipif(sys.version_info < PYTHON_VERSION, reason=PYTHON_VERSION_REASON),
]


class TestCheckNotificationSettings:
    @patch("data_generator.settings.check.config")
    def test_valid_settings(self, mock_config: MagicMock) -> None:
        """
        Test that valid settings produce no errors.

        Args:
        ----
            mock_config (MagicMock): Mocked configuration object with valid settings.

        Asserts:
        -------
            No errors are returned when all settings are valid.
        """
        mock_config.exclude_apps = []
        mock_config.exclude_models = []
        mock_config.custom_field_values = {}
        mock_config.get_setting.side_effect = lambda name, default: None

        errors = check_data_generator_settings(None)

        # There should be no errors for valid settings
        assert not errors
