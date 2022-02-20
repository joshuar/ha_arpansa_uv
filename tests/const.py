"""Constants for integration_blueprint tests."""
from custom_components.arpansa_uv.const import CONF_NAME, CONF_LOCATIONS, CONF_POLL_INTERVAL

# Mock config data to be used across multiple tests
MOCK_CONFIG = {CONF_NAME: "test_arpansa", CONF_LOCATIONS: ['Brisbane','Sydney','Melbourne','Canberra'], CONF_POLL_INTERVAL: 1}
