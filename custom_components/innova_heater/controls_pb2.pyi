from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SetDeviceValueRequest(_message.Message):
    __slots__ = ("type", "value")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    type: int
    value: int
    def __init__(self, type: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...

class GetDeviceStatusResponse(_message.Message):
    __slots__ = ("iot_status", "main_status")
    IOT_STATUS_FIELD_NUMBER: _ClassVar[int]
    MAIN_STATUS_FIELD_NUMBER: _ClassVar[int]
    iot_status: IotStatus
    main_status: MainStatus
    def __init__(self, iot_status: _Optional[_Union[IotStatus, _Mapping]] = ..., main_status: _Optional[_Union[MainStatus, _Mapping]] = ...) -> None: ...

class Event(_message.Message):
    __slots__ = ("type", "value")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    type: int
    value: bytes
    def __init__(self, type: _Optional[int] = ..., value: _Optional[bytes] = ...) -> None: ...

class SetpointStatus(_message.Message):
    __slots__ = ("value", "min", "max", "step", "offset")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    MIN_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    value: int
    min: int
    max: int
    step: int
    offset: int
    def __init__(self, value: _Optional[int] = ..., min: _Optional[int] = ..., max: _Optional[int] = ..., step: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class CalendarStatus(_message.Message):
    __slots__ = ("is_active", "override_until_minutes_epoch")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    OVERRIDE_UNTIL_MINUTES_EPOCH_FIELD_NUMBER: _ClassVar[int]
    is_active: bool
    override_until_minutes_epoch: int
    def __init__(self, is_active: bool = ..., override_until_minutes_epoch: _Optional[int] = ...) -> None: ...

class MainStatus(_message.Message):
    __slots__ = ("fw_version", "serial_number", "alarms", "duepuntozero_status", "m7_status", "fancoil_status", "waterloop_status")
    FW_VERSION_FIELD_NUMBER: _ClassVar[int]
    SERIAL_NUMBER_FIELD_NUMBER: _ClassVar[int]
    ALARMS_FIELD_NUMBER: _ClassVar[int]
    DUEPUNTOZERO_STATUS_FIELD_NUMBER: _ClassVar[int]
    M7_STATUS_FIELD_NUMBER: _ClassVar[int]
    FANCOIL_STATUS_FIELD_NUMBER: _ClassVar[int]
    WATERLOOP_STATUS_FIELD_NUMBER: _ClassVar[int]
    fw_version: int
    serial_number: str
    alarms: bytes
    duepuntozero_status: DuepuntozeroStatus
    m7_status: M7Status
    fancoil_status: FancoilStatus
    waterloop_status: WaterloopStatus
    def __init__(self, fw_version: _Optional[int] = ..., serial_number: _Optional[str] = ..., alarms: _Optional[bytes] = ..., duepuntozero_status: _Optional[_Union[DuepuntozeroStatus, _Mapping]] = ..., m7_status: _Optional[_Union[M7Status, _Mapping]] = ..., fancoil_status: _Optional[_Union[FancoilStatus, _Mapping]] = ..., waterloop_status: _Optional[_Union[WaterloopStatus, _Mapping]] = ...) -> None: ...

class DuepuntozeroStatus(_message.Message):
    __slots__ = ("calendar", "power_state", "temperature_setpoint", "room_temperature", "operation_mode", "fan_speed", "flap", "hotel_mode", "keyboard_lock", "mode_lock", "has_uv_lamp", "uv_lamp", "temperature_unit", "has_air_exchange", "air_exchange", "has_bms", "additional_data")
    CALENDAR_FIELD_NUMBER: _ClassVar[int]
    POWER_STATE_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_SETPOINT_FIELD_NUMBER: _ClassVar[int]
    ROOM_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    OPERATION_MODE_FIELD_NUMBER: _ClassVar[int]
    FAN_SPEED_FIELD_NUMBER: _ClassVar[int]
    FLAP_FIELD_NUMBER: _ClassVar[int]
    HOTEL_MODE_FIELD_NUMBER: _ClassVar[int]
    KEYBOARD_LOCK_FIELD_NUMBER: _ClassVar[int]
    MODE_LOCK_FIELD_NUMBER: _ClassVar[int]
    HAS_UV_LAMP_FIELD_NUMBER: _ClassVar[int]
    UV_LAMP_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_UNIT_FIELD_NUMBER: _ClassVar[int]
    HAS_AIR_EXCHANGE_FIELD_NUMBER: _ClassVar[int]
    AIR_EXCHANGE_FIELD_NUMBER: _ClassVar[int]
    HAS_BMS_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_DATA_FIELD_NUMBER: _ClassVar[int]
    calendar: CalendarStatus
    power_state: bool
    temperature_setpoint: SetpointStatus
    room_temperature: int
    operation_mode: int
    fan_speed: int
    flap: int
    hotel_mode: bool
    keyboard_lock: bool
    mode_lock: int
    has_uv_lamp: bool
    uv_lamp: bool
    temperature_unit: int
    has_air_exchange: bool
    air_exchange: bool
    has_bms: bool
    additional_data: bytes
    def __init__(self, calendar: _Optional[_Union[CalendarStatus, _Mapping]] = ..., power_state: bool = ..., temperature_setpoint: _Optional[_Union[SetpointStatus, _Mapping]] = ..., room_temperature: _Optional[int] = ..., operation_mode: _Optional[int] = ..., fan_speed: _Optional[int] = ..., flap: _Optional[int] = ..., hotel_mode: bool = ..., keyboard_lock: bool = ..., mode_lock: _Optional[int] = ..., has_uv_lamp: bool = ..., uv_lamp: bool = ..., temperature_unit: _Optional[int] = ..., has_air_exchange: bool = ..., air_exchange: bool = ..., has_bms: bool = ..., additional_data: _Optional[bytes] = ...) -> None: ...

class M7Status(_message.Message):
    __slots__ = ("calendar", "power_state", "active_setpoint_type", "temperature_setpoint", "has_air_quality", "air_quality_setpoint", "has_air_humidity", "air_humidity_setpoint", "room_temperature", "operation_mode", "fan_speed", "has_flap", "flap", "hotel_mode", "has_uv_lamp", "uv_lamp", "temperature_unit", "has_air_exchange", "air_exchange", "has_bms", "managed_device_type", "additional_data")
    CALENDAR_FIELD_NUMBER: _ClassVar[int]
    POWER_STATE_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_SETPOINT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_SETPOINT_FIELD_NUMBER: _ClassVar[int]
    HAS_AIR_QUALITY_FIELD_NUMBER: _ClassVar[int]
    AIR_QUALITY_SETPOINT_FIELD_NUMBER: _ClassVar[int]
    HAS_AIR_HUMIDITY_FIELD_NUMBER: _ClassVar[int]
    AIR_HUMIDITY_SETPOINT_FIELD_NUMBER: _ClassVar[int]
    ROOM_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    OPERATION_MODE_FIELD_NUMBER: _ClassVar[int]
    FAN_SPEED_FIELD_NUMBER: _ClassVar[int]
    HAS_FLAP_FIELD_NUMBER: _ClassVar[int]
    FLAP_FIELD_NUMBER: _ClassVar[int]
    HOTEL_MODE_FIELD_NUMBER: _ClassVar[int]
    HAS_UV_LAMP_FIELD_NUMBER: _ClassVar[int]
    UV_LAMP_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_UNIT_FIELD_NUMBER: _ClassVar[int]
    HAS_AIR_EXCHANGE_FIELD_NUMBER: _ClassVar[int]
    AIR_EXCHANGE_FIELD_NUMBER: _ClassVar[int]
    HAS_BMS_FIELD_NUMBER: _ClassVar[int]
    MANAGED_DEVICE_TYPE_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_DATA_FIELD_NUMBER: _ClassVar[int]
    calendar: CalendarStatus
    power_state: bool
    active_setpoint_type: int
    temperature_setpoint: SetpointStatus
    has_air_quality: bool
    air_quality_setpoint: SetpointStatus
    has_air_humidity: bool
    air_humidity_setpoint: SetpointStatus
    room_temperature: int
    operation_mode: int
    fan_speed: int
    has_flap: bool
    flap: int
    hotel_mode: bool
    has_uv_lamp: bool
    uv_lamp: bool
    temperature_unit: int
    has_air_exchange: bool
    air_exchange: bool
    has_bms: bool
    managed_device_type: int
    additional_data: bytes
    def __init__(self, calendar: _Optional[_Union[CalendarStatus, _Mapping]] = ..., power_state: bool = ..., active_setpoint_type: _Optional[int] = ..., temperature_setpoint: _Optional[_Union[SetpointStatus, _Mapping]] = ..., has_air_quality: bool = ..., air_quality_setpoint: _Optional[_Union[SetpointStatus, _Mapping]] = ..., has_air_humidity: bool = ..., air_humidity_setpoint: _Optional[_Union[SetpointStatus, _Mapping]] = ..., room_temperature: _Optional[int] = ..., operation_mode: _Optional[int] = ..., fan_speed: _Optional[int] = ..., has_flap: bool = ..., flap: _Optional[int] = ..., hotel_mode: bool = ..., has_uv_lamp: bool = ..., uv_lamp: bool = ..., temperature_unit: _Optional[int] = ..., has_air_exchange: bool = ..., air_exchange: bool = ..., has_bms: bool = ..., managed_device_type: _Optional[int] = ..., additional_data: _Optional[bytes] = ...) -> None: ...

class FancoilStatus(_message.Message):
    __slots__ = ("calendar", "power_state", "temperature_setpoint", "room_temperature", "operation_mode", "fan_speed", "flap", "has_flap", "hotel_mode", "keyboard_lock", "mode_lock", "has_uv_lamp", "uv_lamp", "temperature_unit", "has_bms", "additional_data")
    CALENDAR_FIELD_NUMBER: _ClassVar[int]
    POWER_STATE_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_SETPOINT_FIELD_NUMBER: _ClassVar[int]
    ROOM_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    OPERATION_MODE_FIELD_NUMBER: _ClassVar[int]
    FAN_SPEED_FIELD_NUMBER: _ClassVar[int]
    FLAP_FIELD_NUMBER: _ClassVar[int]
    HAS_FLAP_FIELD_NUMBER: _ClassVar[int]
    HOTEL_MODE_FIELD_NUMBER: _ClassVar[int]
    KEYBOARD_LOCK_FIELD_NUMBER: _ClassVar[int]
    MODE_LOCK_FIELD_NUMBER: _ClassVar[int]
    HAS_UV_LAMP_FIELD_NUMBER: _ClassVar[int]
    UV_LAMP_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_UNIT_FIELD_NUMBER: _ClassVar[int]
    HAS_BMS_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_DATA_FIELD_NUMBER: _ClassVar[int]
    calendar: CalendarStatus
    power_state: bool
    temperature_setpoint: SetpointStatus
    room_temperature: int
    operation_mode: int
    fan_speed: int
    flap: int
    has_flap: bool
    hotel_mode: bool
    keyboard_lock: bool
    mode_lock: int
    has_uv_lamp: bool
    uv_lamp: bool
    temperature_unit: int
    has_bms: bool
    additional_data: bytes
    def __init__(self, calendar: _Optional[_Union[CalendarStatus, _Mapping]] = ..., power_state: bool = ..., temperature_setpoint: _Optional[_Union[SetpointStatus, _Mapping]] = ..., room_temperature: _Optional[int] = ..., operation_mode: _Optional[int] = ..., fan_speed: _Optional[int] = ..., flap: _Optional[int] = ..., has_flap: bool = ..., hotel_mode: bool = ..., keyboard_lock: bool = ..., mode_lock: _Optional[int] = ..., has_uv_lamp: bool = ..., uv_lamp: bool = ..., temperature_unit: _Optional[int] = ..., has_bms: bool = ..., additional_data: _Optional[bytes] = ...) -> None: ...

class WaterloopStatus(_message.Message):
    __slots__ = ("calendar", "power_state", "temperature_setpoint", "room_temperature", "operation_mode", "fan_speed", "hotel_mode", "keyboard_lock", "mode_lock", "has_uv_lamp", "uv_lamp", "temperature_unit", "has_bms", "additional_data")
    CALENDAR_FIELD_NUMBER: _ClassVar[int]
    POWER_STATE_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_SETPOINT_FIELD_NUMBER: _ClassVar[int]
    ROOM_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    OPERATION_MODE_FIELD_NUMBER: _ClassVar[int]
    FAN_SPEED_FIELD_NUMBER: _ClassVar[int]
    HOTEL_MODE_FIELD_NUMBER: _ClassVar[int]
    KEYBOARD_LOCK_FIELD_NUMBER: _ClassVar[int]
    MODE_LOCK_FIELD_NUMBER: _ClassVar[int]
    HAS_UV_LAMP_FIELD_NUMBER: _ClassVar[int]
    UV_LAMP_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_UNIT_FIELD_NUMBER: _ClassVar[int]
    HAS_BMS_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_DATA_FIELD_NUMBER: _ClassVar[int]
    calendar: CalendarStatus
    power_state: bool
    temperature_setpoint: SetpointStatus
    room_temperature: int
    operation_mode: int
    fan_speed: int
    hotel_mode: bool
    keyboard_lock: bool
    mode_lock: int
    has_uv_lamp: bool
    uv_lamp: bool
    temperature_unit: int
    has_bms: bool
    additional_data: bytes
    def __init__(self, calendar: _Optional[_Union[CalendarStatus, _Mapping]] = ..., power_state: bool = ..., temperature_setpoint: _Optional[_Union[SetpointStatus, _Mapping]] = ..., room_temperature: _Optional[int] = ..., operation_mode: _Optional[int] = ..., fan_speed: _Optional[int] = ..., hotel_mode: bool = ..., keyboard_lock: bool = ..., mode_lock: _Optional[int] = ..., has_uv_lamp: bool = ..., uv_lamp: bool = ..., temperature_unit: _Optional[int] = ..., has_bms: bool = ..., additional_data: _Optional[bytes] = ...) -> None: ...

class IotStatus(_message.Message):
    __slots__ = ("fw_version", "alarms", "power_supply_type", "battery_status", "wifi", "ethernet", "thread")
    class PowerSupplyType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        EXTERNAL: _ClassVar[IotStatus.PowerSupplyType]
        BATTERY: _ClassVar[IotStatus.PowerSupplyType]
    EXTERNAL: IotStatus.PowerSupplyType
    BATTERY: IotStatus.PowerSupplyType
    class BatteryStatus(_message.Message):
        __slots__ = ("percentage", "is_charging", "is_faulty")
        PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
        IS_CHARGING_FIELD_NUMBER: _ClassVar[int]
        IS_FAULTY_FIELD_NUMBER: _ClassVar[int]
        percentage: int
        is_charging: bool
        is_faulty: bool
        def __init__(self, percentage: _Optional[int] = ..., is_charging: bool = ..., is_faulty: bool = ...) -> None: ...
    class WiFiStatus(_message.Message):
        __slots__ = ("ssid", "rssi")
        SSID_FIELD_NUMBER: _ClassVar[int]
        RSSI_FIELD_NUMBER: _ClassVar[int]
        ssid: str
        rssi: int
        def __init__(self, ssid: _Optional[str] = ..., rssi: _Optional[int] = ...) -> None: ...
    class EthernetStatus(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class ThreadStatus(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    FW_VERSION_FIELD_NUMBER: _ClassVar[int]
    ALARMS_FIELD_NUMBER: _ClassVar[int]
    POWER_SUPPLY_TYPE_FIELD_NUMBER: _ClassVar[int]
    BATTERY_STATUS_FIELD_NUMBER: _ClassVar[int]
    WIFI_FIELD_NUMBER: _ClassVar[int]
    ETHERNET_FIELD_NUMBER: _ClassVar[int]
    THREAD_FIELD_NUMBER: _ClassVar[int]
    fw_version: int
    alarms: bytes
    power_supply_type: IotStatus.PowerSupplyType
    battery_status: IotStatus.BatteryStatus
    wifi: IotStatus.WiFiStatus
    ethernet: IotStatus.EthernetStatus
    thread: IotStatus.ThreadStatus
    def __init__(self, fw_version: _Optional[int] = ..., alarms: _Optional[bytes] = ..., power_supply_type: _Optional[_Union[IotStatus.PowerSupplyType, str]] = ..., battery_status: _Optional[_Union[IotStatus.BatteryStatus, _Mapping]] = ..., wifi: _Optional[_Union[IotStatus.WiFiStatus, _Mapping]] = ..., ethernet: _Optional[_Union[IotStatus.EthernetStatus, _Mapping]] = ..., thread: _Optional[_Union[IotStatus.ThreadStatus, _Mapping]] = ...) -> None: ...
