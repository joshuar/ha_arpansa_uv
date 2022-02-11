NAME = "ARPANSA UV"
DOMAIN = "arpansa_uv"
VERSION = "0.0.1"
ATTRIBUTION = "UV observations courtesy of ARPANSA"
ARPANSA_URL = "https://uvdata.arpansa.gov.au/xml/uvvalues.xml"
ISSUE_URL = "https://github.com/joshuar/ha_arpansa_uv/issues"

DEFAULT_SCAN_INTERVAL = 1
DEFAULT_NAME = NAME

SENSOR = "sensor"
PLATFORMS = [SENSOR]

CONF_NAME = "name"
CONF_API = "arpansa"
CONF_LOCATIONS = "locations"
CONF_POLL_INTERVAL = "poll_interval"

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""