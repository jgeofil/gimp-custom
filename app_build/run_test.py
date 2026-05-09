from tests.test_integration import test_plugin_registration_and_execution_in_gimp

# Run the plugin test (integration test)
try:
    test_plugin_registration_and_execution_in_gimp()
except Exception as e:
    pass

import pytest

# Run all tests
pytest.main()
