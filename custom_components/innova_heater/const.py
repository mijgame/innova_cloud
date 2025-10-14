"""Constants for the Innova Cloud integration."""

from homeassistant.components.climate import HVACMode

DOMAIN = "innova_heater"

# Config flow
CONF_EMAIL = "email"
CONF_PASSWORD = "password"
CONF_MAC_ADDRESS = "mac_address"
CONF_DEVICE_TYPE = "device_type"

# API
API_BASE_URL = "https://api.innova.solutiontech.tech/api"
GRPC_HOST = "grpc.innova.solutiontech.tech"
GRPC_PORT = 443

# Update intervals
UPDATE_INTERVAL = 30  # seconds

# Event types (received from device)
# Fancoil-specific event types
EVENT_TYPE_FANCOIL_MANUAL_MODE = 249
EVENT_TYPE_FANCOIL_FLAP = 250
EVENT_TYPE_FANCOIL_FAN_SPEED = 251
EVENT_TYPE_FANCOIL_OPERATION_MODE = 252
EVENT_TYPE_FANCOIL_ROOM_TEMP = 253
EVENT_TYPE_FANCOIL_SETPOINT = 254
EVENT_TYPE_FANCOIL_POWER_STATE = 255

# Legacy event types (may still be used by some devices)
EVENT_TYPE_POWER_STATE = 1
EVENT_TYPE_OPERATION_MODE = 3
EVENT_TYPE_FAN_SPEED = 4
EVENT_TYPE_CURRENT_TEMP = 253
EVENT_TYPE_TARGET_TEMP = 254

# Operation types (SetDeviceValue - sent to device)
OP_TYPE_POWER_STATE = 1
OP_TYPE_SETPOINT = 2
OP_TYPE_OPERATION_MODE = 3
OP_TYPE_FAN_SPEED = 4
OP_TYPE_FLAP = 5
# Type 6 appears unused
OP_TYPE_REBOOT = 7
OP_TYPE_CALENDAR = 8
OP_TYPE_MANUAL_MODE = 9

# Device types (from APK DeviceType enum)
DEVICE_TYPE_DUEPUNTOZERO = "duepuntozero"
DEVICE_TYPE_M7 = "m7"
DEVICE_TYPE_FANCOIL = "fancoil"
DEVICE_TYPE_M6 = "m6"
DEVICE_TYPE_FANCOIL_LEGACY = "fancoil_legacy"
DEVICE_TYPE_WATERLOOP = "waterloop"

DEVICE_TYPES = {
    DEVICE_TYPE_FANCOIL: "Fancoil / Osmo",
    DEVICE_TYPE_DUEPUNTOZERO: "Duepuntozero",
    DEVICE_TYPE_M7: "M7",
    DEVICE_TYPE_M6: "M6",
    DEVICE_TYPE_FANCOIL_LEGACY: "Fancoil Legacy",
    DEVICE_TYPE_WATERLOOP: "Waterloop",
}

# Supported modes per device type (from APK operation mode enums)
DEVICE_TYPE_MODES = {
    DEVICE_TYPE_FANCOIL: [
        HVACMode.OFF,
        HVACMode.AUTO,
        HVACMode.HEAT,
        HVACMode.COOL,
    ],
    DEVICE_TYPE_DUEPUNTOZERO: [
        HVACMode.OFF,
        HVACMode.AUTO,
        HVACMode.HEAT,
        HVACMode.COOL,
        HVACMode.FAN_ONLY,
        HVACMode.DRY,
    ],
    DEVICE_TYPE_M7: [
        HVACMode.OFF,
        HVACMode.AUTO,
        HVACMode.HEAT,
        HVACMode.COOL,
        HVACMode.FAN_ONLY,
        HVACMode.DRY,
    ],
    DEVICE_TYPE_M6: [
        HVACMode.OFF,
        HVACMode.AUTO,
        HVACMode.HEAT,
        HVACMode.COOL,
    ],
    DEVICE_TYPE_FANCOIL_LEGACY: [
        HVACMode.OFF,
        HVACMode.HEAT,
        HVACMode.COOL,
    ],
    DEVICE_TYPE_WATERLOOP: [
        HVACMode.OFF,
        HVACMode.AUTO,
        HVACMode.HEAT,
        HVACMode.COOL,
        HVACMode.FAN_ONLY,
        HVACMode.DRY,
    ],
}
