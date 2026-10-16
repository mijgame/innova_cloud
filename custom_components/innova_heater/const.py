"""Constants for the Innova Cloud integration."""

from homeassistant.components.climate import HVACMode

DOMAIN = "innova_heater"

# Config flow
CONF_EMAIL = "email"
CONF_PASSWORD = "password"
CONF_MAC_ADDRESS = "mac_address"
CONF_NODE_ID = "node_id"
CONF_HOME_ID = "home_id"
CONF_DEVICE_TYPE = "device_type"  # v1 entries only; v2 reads capabilities from the device

# API (v2, as used by the Innova app 3.x)
API_BASE_URL = "https://v2.api.innova.solutiontech.tech/app"
GRPC_HOST = "v2.grpc.innova.solutiontech.tech"
GRPC_PORT = 443

# Update intervals
UPDATE_INTERVAL = 60  # seconds; full status re-sync, real-time changes come via events
COMMAND_TIMEOUT = 10  # seconds; the app uses 5

# HvacMode enum values on the wire (see app_service.proto)
HVAC_MODE_AUTO = 1
HVAC_MODE_HEAT = 2
HVAC_MODE_COOL = 3
HVAC_MODE_DRY = 4
HVAC_MODE_FAN = 5

HVAC_MODE_NAMES = {
    HVAC_MODE_AUTO: "Auto",
    HVAC_MODE_HEAT: "Heat",
    HVAC_MODE_COOL: "Cool",
    HVAC_MODE_DRY: "Dry",
    HVAC_MODE_FAN: "Fan Only",
}

# FanSpeed enum values on the wire
FAN_SPEED_AUTO = 1
FAN_SPEED_MIN = 2
FAN_SPEED_MID = 3
FAN_SPEED_MAX = 4
FAN_SPEED_BOOST = 5

# OperationModeType enum values on the wire
OPERATION_MODE_CALENDAR = 1
OPERATION_MODE_MANUAL = 2
OPERATION_MODE_ANTIFREEZE = 3

# Modes to offer when the device doesn't report its capabilities
DEFAULT_HVAC_MODES = [
    HVACMode.OFF,
    HVACMode.AUTO,
    HVACMode.HEAT,
    HVACMode.COOL,
]
