# Innova Cloud Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A custom Home Assistant integration for Innova HVAC devices (heaters, fan coils, and climate control units) connected to the Innova Cloud service.

## Features

### Climate Control
- Full thermostat integration with Home Assistant climate entity
- Real-time temperature monitoring (0.1°C precision)
- Multiple operation modes: Auto, Heat, Cool, Fan Only, Dry (device-dependent)
- Fan mode control: Auto, Night, Max (for Fancoil devices)
- Power control (on/off)
- Temperature setpoint control (5-40°C, adjustable in 0.5°C steps)
- Accurate HVAC action reporting (heating/cooling/idle/off)

### Real-time Updates
- Event-driven updates via gRPC stream (no polling)
- Instant response to device state changes
- Live temperature readings
- Immediate feedback on control actions

### Additional Controls
- Air flap position control (for supported devices)
- Device reboot button
- Calendar/schedule status monitoring
- Keyboard lock status
- Hotel mode detection

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
6. **Important:** Choose your device model type for correct operation mode support:
   - **Fancoil / Osmo**: Supports Auto, Heat, Cool
   - **Duepuntozero**: Supports Auto, Heat, Cool, Fan Only, Dry
   - **M7**: Supports Auto, Heat, Cool, Fan Only, Dry
   - **M6**: Supports Auto, Heat, Cool
   - **Fancoil Legacy**: Supports Heat, Cool (no Auto)
   - **Waterloop**: Supports Auto, Heat, Cool, Fan Only, Dry
7. The integration will create all entities automatically

## Entities

After configuration, the following entities will be created:

### Climate Entity
- `climate.[device_name]`
  - Full thermostat control with temperature and mode selection
  - Temperature range: 5-40°C (adjustable in 0.5°C steps)
  - Fan mode control: Auto, Night, Max (for Fancoil devices)
  - HVAC action: Off, Heating, Cooling, Idle, Fan, Drying

### Sensors
- `sensor.[device_name]_current_temperature` - Current room temperature
- `sensor.[device_name]_target_temperature` - Target setpoint
- `sensor.[device_name]_operation_mode` - Current operation mode (Auto/Heat/Cool/Fan/Dry)
- `sensor.[device_name]_connection_type` - Connection type (WiFi/Ethernet/Thread)
- `sensor.[device_name]_wifi_ssid` - WiFi network name (if connected via WiFi)
- `sensor.[device_name]_wifi_rssi` - WiFi signal strength in dBm (if connected via WiFi)
- `sensor.[device_name]_flap_position` - Current flap position 0-7 (if device has flap)

### Binary Sensors
- `binary_sensor.[device_name]_calendar_active` - Calendar/schedule active status
- `binary_sensor.[device_name]_keyboard_lock` - Keyboard lock status
- `binary_sensor.[device_name]_hotel_mode` - Hotel mode status

### Number Entities
- `number.[device_name]_flap_position` - Control air flap position (0-7, if device has flap)

### Buttons
- `button.[device_name]_reboot_device` - Reboot the device

### Diagnostic Sensors
- `sensor.[device_name]_firmware_version` - Device firmware version
- `sensor.[device_name]_serial_number` - Device serial number

## Supported Devices

This integration supports all Innova devices connected to the Innova Cloud service:
- Fancoil / Osmo units
- Duepuntozero series
- M6 and M7 models
- Fancoil Legacy units
- Waterloop systems

## License

MIT License - Use at your own risk.
