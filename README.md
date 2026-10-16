# Innova Cloud Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A custom Home Assistant integration for Innova HVAC devices (heaters, fan coils, and climate control units) connected to the Innova Cloud service.

## Features

### Climate Control
- Full thermostat integration with Home Assistant climate entity
- Real-time temperature monitoring (0.1°C precision)
- Operation modes (Auto, Heat, Cool, Dry, Fan Only) and fan speeds (Auto, Low, Medium, High, Boost), as reported by the device itself
- Flap swing control (swing mode on/off)
- Power control (on/off)
- Temperature setpoint control, with range and step reported by the device
- HVAC action reporting, using the mode the unit is actually running (e.g. heating while in Auto)
- Current humidity (if the device measures it)

### Real-time Updates
- Event-driven updates via gRPC stream, with a full state re-sync every minute
- Instant response to device state changes
- Live temperature readings
- Immediate feedback on control actions

### Additional Controls
- Device reboot button
- Calendar/schedule status monitoring

### Authentication
- Your credentials are stored so the integration can log in again when the session token expires
- If the login is rejected, Home Assistant asks you to re-authenticate under **Settings** → **Devices & Services**

## Installation

### Via HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on **Integrations**
3. Click the three dots in the top right corner and select **Custom repositories**
4. Add the repository URL: `https://github.com/mijgame/innova_cloud`
5. Select **Integration** as the category
6. Click **Add**
7. Search for "Innova Cloud" in HACS integrations
8. Click **Download**
9. Restart Home Assistant

### Manual Installation

1. Download or clone this repository
2. Copy the `custom_components/innova_heater` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **Innova Cloud**
4. Enter your Innova account credentials (email and password)
5. Select your device from the list
6. The integration will create all entities automatically; supported modes and fan speeds are read from the device

## Entities

After configuration, the following entities will be created:

### Climate Entity
- `climate.[device_name]`
  - Full thermostat control with temperature and mode selection
  - Temperature range and step as reported by the device
  - Fan mode and swing mode control (if supported)
  - HVAC action: Off, Heating, Cooling, Idle, Fan, Drying

### Sensors
- `sensor.[device_name]_current_temperature` - Current room temperature
- `sensor.[device_name]_target_temperature` - Target setpoint
- `sensor.[device_name]_operation_mode` - Current operation mode (Auto/Heat/Cool/Fan/Dry)
- `sensor.[device_name]_connection_type` - Connection type (WiFi/Ethernet/Thread)
- `sensor.[device_name]_wifi_ssid` - WiFi network name (if connected via WiFi)
- `sensor.[device_name]_wifi_rssi` - WiFi signal strength in dBm (if connected via WiFi)

### Binary Sensors
- `binary_sensor.[device_name]_calendar_active` - Calendar/schedule active status

### Buttons
- `button.[device_name]_reboot_device` - Reboot the device

### Diagnostic Sensors
- `sensor.[device_name]_firmware_version` - Device firmware version
- `sensor.[device_name]_serial_number` - Device serial number

## Supported Devices

This integration uses the Innova Cloud v2 API (as used by the Innova app 3.x) and supports:
- Fancoils
- Air conditioners
- Thermostats

Heat pumps and Butler devices are not supported yet.

## Upgrading from 1.x

Version 2.0 switches to the Innova Cloud v2 API; the old API no longer accepts current accounts.
After updating, Home Assistant will ask you to re-authenticate once. The flap position, keyboard lock
and hotel mode entities no longer exist in the v2 API; you can delete them from the device page.

## Development

`tools/innova_probe.py` talks to the API directly (login, device list, state, events, commands)
without Home Assistant. `app_service.proto` is the gRPC schema, reconstructed from the Innova app;
regenerate the Python modules with `grpcio-tools==1.72.1`:

```
python -m grpc_tools.protoc -I. --python_out=custom_components/innova_heater \
    --pyi_out=custom_components/innova_heater --grpc_python_out=custom_components/innova_heater app_service.proto
```

and change the import in `app_service_pb2_grpc.py` to `from . import app_service_pb2 as app__service__pb2`.

## License

MIT License - Use at your own risk.
