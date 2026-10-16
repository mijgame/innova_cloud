from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HvacMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    HVAC_MODE_UNSPECIFIED: _ClassVar[HvacMode]
    HVAC_MODE_AUTO: _ClassVar[HvacMode]
    HVAC_MODE_HEAT: _ClassVar[HvacMode]
    HVAC_MODE_COOL: _ClassVar[HvacMode]
    HVAC_MODE_DRY: _ClassVar[HvacMode]
    HVAC_MODE_FAN: _ClassVar[HvacMode]

class FanSpeed(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FAN_SPEED_UNSPECIFIED: _ClassVar[FanSpeed]
    FAN_SPEED_AUTO: _ClassVar[FanSpeed]
    FAN_SPEED_MIN: _ClassVar[FanSpeed]
    FAN_SPEED_MID: _ClassVar[FanSpeed]
    FAN_SPEED_MAX: _ClassVar[FanSpeed]
    FAN_SPEED_BOOST: _ClassVar[FanSpeed]

class OperationModeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPERATION_MODE_UNSPECIFIED: _ClassVar[OperationModeType]
    OPERATION_MODE_CALENDAR: _ClassVar[OperationModeType]
    OPERATION_MODE_MANUAL: _ClassVar[OperationModeType]
    OPERATION_MODE_ANTIFREEZE: _ClassVar[OperationModeType]

class Preset(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRESET_UNSPECIFIED: _ClassVar[Preset]
    PRESET_NIGHT: _ClassVar[Preset]
    PRESET_ECO: _ClassVar[Preset]
    PRESET_COMFORT: _ClassVar[Preset]
    PRESET_AWAY: _ClassVar[Preset]
    PRESET_FREEZE: _ClassVar[Preset]

class NodeErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NODE_ERROR_UNSPECIFIED: _ClassVar[NodeErrorCode]
    NODE_ERROR_OFFLINE: _ClassVar[NodeErrorCode]
    NODE_ERROR_CACHE_NOT_READY: _ClassVar[NodeErrorCode]
    NODE_ERROR_INTERNAL: _ClassVar[NodeErrorCode]

class ResponseErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESPONSE_ERROR_UNSPECIFIED: _ClassVar[ResponseErrorCode]
    RESPONSE_ERROR_RESPONSE_TIMEOUT: _ClassVar[ResponseErrorCode]
    RESPONSE_ERROR_CACHE_NOT_READY: _ClassVar[ResponseErrorCode]
HVAC_MODE_UNSPECIFIED: HvacMode
HVAC_MODE_AUTO: HvacMode
HVAC_MODE_HEAT: HvacMode
HVAC_MODE_COOL: HvacMode
HVAC_MODE_DRY: HvacMode
HVAC_MODE_FAN: HvacMode
FAN_SPEED_UNSPECIFIED: FanSpeed
FAN_SPEED_AUTO: FanSpeed
FAN_SPEED_MIN: FanSpeed
FAN_SPEED_MID: FanSpeed
FAN_SPEED_MAX: FanSpeed
FAN_SPEED_BOOST: FanSpeed
OPERATION_MODE_UNSPECIFIED: OperationModeType
OPERATION_MODE_CALENDAR: OperationModeType
OPERATION_MODE_MANUAL: OperationModeType
OPERATION_MODE_ANTIFREEZE: OperationModeType
PRESET_UNSPECIFIED: Preset
PRESET_NIGHT: Preset
PRESET_ECO: Preset
PRESET_COMFORT: Preset
PRESET_AWAY: Preset
PRESET_FREEZE: Preset
NODE_ERROR_UNSPECIFIED: NodeErrorCode
NODE_ERROR_OFFLINE: NodeErrorCode
NODE_ERROR_CACHE_NOT_READY: NodeErrorCode
NODE_ERROR_INTERNAL: NodeErrorCode
RESPONSE_ERROR_UNSPECIFIED: ResponseErrorCode
RESPONSE_ERROR_RESPONSE_TIMEOUT: ResponseErrorCode
RESPONSE_ERROR_CACHE_NOT_READY: ResponseErrorCode

class SendDeviceRequest(_message.Message):
    __slots__ = ("mac_address", "node_id", "request")
    MAC_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    mac_address: bytes
    node_id: int
    request: DeviceRequest
    def __init__(self, mac_address: _Optional[bytes] = ..., node_id: _Optional[int] = ..., request: _Optional[_Union[DeviceRequest, _Mapping]] = ...) -> None: ...

class DeviceRequest(_message.Message):
    __slots__ = ("system", "shared", "ac", "fancoil", "thermostat")
    SYSTEM_FIELD_NUMBER: _ClassVar[int]
    SHARED_FIELD_NUMBER: _ClassVar[int]
    AC_FIELD_NUMBER: _ClassVar[int]
    FANCOIL_FIELD_NUMBER: _ClassVar[int]
    THERMOSTAT_FIELD_NUMBER: _ClassVar[int]
    system: SystemRequest
    shared: SharedRequest
    ac: ClimateRequest
    fancoil: ClimateRequest
    thermostat: ClimateRequest
    def __init__(self, system: _Optional[_Union[SystemRequest, _Mapping]] = ..., shared: _Optional[_Union[SharedRequest, _Mapping]] = ..., ac: _Optional[_Union[ClimateRequest, _Mapping]] = ..., fancoil: _Optional[_Union[ClimateRequest, _Mapping]] = ..., thermostat: _Optional[_Union[ClimateRequest, _Mapping]] = ...) -> None: ...

class SystemRequest(_message.Message):
    __slots__ = ("reboot",)
    class Reboot(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    REBOOT_FIELD_NUMBER: _ClassVar[int]
    reboot: SystemRequest.Reboot
    def __init__(self, reboot: _Optional[_Union[SystemRequest.Reboot, _Mapping]] = ...) -> None: ...

class SharedRequest(_message.Message):
    __slots__ = ("get_state", "set_operation_mode")
    class GetState(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class SetOperationMode(_message.Message):
        __slots__ = ("manual",)
        class Manual(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        MANUAL_FIELD_NUMBER: _ClassVar[int]
        manual: SharedRequest.SetOperationMode.Manual
        def __init__(self, manual: _Optional[_Union[SharedRequest.SetOperationMode.Manual, _Mapping]] = ...) -> None: ...
    GET_STATE_FIELD_NUMBER: _ClassVar[int]
    SET_OPERATION_MODE_FIELD_NUMBER: _ClassVar[int]
    get_state: SharedRequest.GetState
    set_operation_mode: SharedRequest.SetOperationMode
    def __init__(self, get_state: _Optional[_Union[SharedRequest.GetState, _Mapping]] = ..., set_operation_mode: _Optional[_Union[SharedRequest.SetOperationMode, _Mapping]] = ...) -> None: ...

class ClimateRequest(_message.Message):
    __slots__ = ("set_state",)
    class SetState(_message.Message):
        __slots__ = ("power", "temperature_setpoint", "hvac_mode", "fan_speed", "flap_swing", "erv", "silent_mode")
        POWER_FIELD_NUMBER: _ClassVar[int]
        TEMPERATURE_SETPOINT_FIELD_NUMBER: _ClassVar[int]
        HVAC_MODE_FIELD_NUMBER: _ClassVar[int]
        FAN_SPEED_FIELD_NUMBER: _ClassVar[int]
        FLAP_SWING_FIELD_NUMBER: _ClassVar[int]
        ERV_FIELD_NUMBER: _ClassVar[int]
        SILENT_MODE_FIELD_NUMBER: _ClassVar[int]
        power: bool
        temperature_setpoint: float
        hvac_mode: HvacMode
        fan_speed: FanSpeed
        flap_swing: bool
        erv: bool
        silent_mode: bool
        def __init__(self, power: bool = ..., temperature_setpoint: _Optional[float] = ..., hvac_mode: _Optional[_Union[HvacMode, str]] = ..., fan_speed: _Optional[_Union[FanSpeed, str]] = ..., flap_swing: bool = ..., erv: bool = ..., silent_mode: bool = ...) -> None: ...
    SET_STATE_FIELD_NUMBER: _ClassVar[int]
    set_state: ClimateRequest.SetState
    def __init__(self, set_state: _Optional[_Union[ClimateRequest.SetState, _Mapping]] = ...) -> None: ...

class SendDeviceResponse(_message.Message):
    __slots__ = ("error", "device")
    class Error(_message.Message):
        __slots__ = ("code", "message")
        CODE_FIELD_NUMBER: _ClassVar[int]
        MESSAGE_FIELD_NUMBER: _ClassVar[int]
        code: ResponseErrorCode
        message: str
        def __init__(self, code: _Optional[_Union[ResponseErrorCode, str]] = ..., message: _Optional[str] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    error: SendDeviceResponse.Error
    device: DeviceResponse
    def __init__(self, error: _Optional[_Union[SendDeviceResponse.Error, _Mapping]] = ..., device: _Optional[_Union[DeviceResponse, _Mapping]] = ...) -> None: ...

class DeviceResponse(_message.Message):
    __slots__ = ("shared", "ac", "fancoil", "thermostat")
    class Empty(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    SHARED_FIELD_NUMBER: _ClassVar[int]
    AC_FIELD_NUMBER: _ClassVar[int]
    FANCOIL_FIELD_NUMBER: _ClassVar[int]
    THERMOSTAT_FIELD_NUMBER: _ClassVar[int]
    shared: SharedResponse
    ac: DeviceResponse.Empty
    fancoil: DeviceResponse.Empty
    thermostat: DeviceResponse.Empty
    def __init__(self, shared: _Optional[_Union[SharedResponse, _Mapping]] = ..., ac: _Optional[_Union[DeviceResponse.Empty, _Mapping]] = ..., fancoil: _Optional[_Union[DeviceResponse.Empty, _Mapping]] = ..., thermostat: _Optional[_Union[DeviceResponse.Empty, _Mapping]] = ...) -> None: ...

class SharedResponse(_message.Message):
    __slots__ = ("state",)
    class State(_message.Message):
        __slots__ = ("gateway", "nodes")
        class NodesEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: int
            value: NodeState
            def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[NodeState, _Mapping]] = ...) -> None: ...
        GATEWAY_FIELD_NUMBER: _ClassVar[int]
        NODES_FIELD_NUMBER: _ClassVar[int]
        gateway: GatewayState
        nodes: _containers.MessageMap[int, NodeState]
        def __init__(self, gateway: _Optional[_Union[GatewayState, _Mapping]] = ..., nodes: _Optional[_Mapping[int, NodeState]] = ...) -> None: ...
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: SharedResponse.State
    def __init__(self, state: _Optional[_Union[SharedResponse.State, _Mapping]] = ...) -> None: ...

class GatewayState(_message.Message):
    __slots__ = ("firmware_version_code", "serial_number", "connection")
    class Connection(_message.Message):
        __slots__ = ("wifi", "ethernet")
        class Wifi(_message.Message):
            __slots__ = ("network",)
            class Network(_message.Message):
                __slots__ = ("ssid", "rssi", "snr", "band")
                SSID_FIELD_NUMBER: _ClassVar[int]
                RSSI_FIELD_NUMBER: _ClassVar[int]
                SNR_FIELD_NUMBER: _ClassVar[int]
                BAND_FIELD_NUMBER: _ClassVar[int]
                ssid: str
                rssi: int
                snr: int
                band: int
                def __init__(self, ssid: _Optional[str] = ..., rssi: _Optional[int] = ..., snr: _Optional[int] = ..., band: _Optional[int] = ...) -> None: ...
            NETWORK_FIELD_NUMBER: _ClassVar[int]
            network: GatewayState.Connection.Wifi.Network
            def __init__(self, network: _Optional[_Union[GatewayState.Connection.Wifi.Network, _Mapping]] = ...) -> None: ...
        class Ethernet(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        WIFI_FIELD_NUMBER: _ClassVar[int]
        ETHERNET_FIELD_NUMBER: _ClassVar[int]
        wifi: GatewayState.Connection.Wifi
        ethernet: GatewayState.Connection.Ethernet
        def __init__(self, wifi: _Optional[_Union[GatewayState.Connection.Wifi, _Mapping]] = ..., ethernet: _Optional[_Union[GatewayState.Connection.Ethernet, _Mapping]] = ...) -> None: ...
    FIRMWARE_VERSION_CODE_FIELD_NUMBER: _ClassVar[int]
    SERIAL_NUMBER_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    firmware_version_code: int
    serial_number: str
    connection: GatewayState.Connection
    def __init__(self, firmware_version_code: _Optional[int] = ..., serial_number: _Optional[str] = ..., connection: _Optional[_Union[GatewayState.Connection, _Mapping]] = ...) -> None: ...

class NodeError(_message.Message):
    __slots__ = ("code",)
    CODE_FIELD_NUMBER: _ClassVar[int]
    code: NodeErrorCode
    def __init__(self, code: _Optional[_Union[NodeErrorCode, str]] = ...) -> None: ...

class NodeState(_message.Message):
    __slots__ = ("ac", "fancoil", "thermostat", "error")
    AC_FIELD_NUMBER: _ClassVar[int]
    FANCOIL_FIELD_NUMBER: _ClassVar[int]
    THERMOSTAT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ac: AcState
    fancoil: ClimateState
    thermostat: ClimateState
    error: NodeError
    def __init__(self, ac: _Optional[_Union[AcState, _Mapping]] = ..., fancoil: _Optional[_Union[ClimateState, _Mapping]] = ..., thermostat: _Optional[_Union[ClimateState, _Mapping]] = ..., error: _Optional[_Union[NodeError, _Mapping]] = ...) -> None: ...

class Setpoint(_message.Message):
    __slots__ = ("value", "min", "max", "step")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    MIN_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    value: float
    min: float
    max: float
    step: float
    def __init__(self, value: _Optional[float] = ..., min: _Optional[float] = ..., max: _Optional[float] = ..., step: _Optional[float] = ...) -> None: ...

class HvacModeState(_message.Message):
    __slots__ = ("value", "actual_value", "capabilities")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    ACTUAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    CAPABILITIES_FIELD_NUMBER: _ClassVar[int]
    value: HvacMode
    actual_value: HvacMode
    capabilities: _containers.RepeatedScalarFieldContainer[HvacMode]
    def __init__(self, value: _Optional[_Union[HvacMode, str]] = ..., actual_value: _Optional[_Union[HvacMode, str]] = ..., capabilities: _Optional[_Iterable[_Union[HvacMode, str]]] = ...) -> None: ...

class FanSpeedState(_message.Message):
    __slots__ = ("value", "capabilities")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    CAPABILITIES_FIELD_NUMBER: _ClassVar[int]
    value: FanSpeed
    capabilities: _containers.RepeatedScalarFieldContainer[FanSpeed]
    def __init__(self, value: _Optional[_Union[FanSpeed, str]] = ..., capabilities: _Optional[_Iterable[_Union[FanSpeed, str]]] = ...) -> None: ...

class OperationMode(_message.Message):
    __slots__ = ("active", "calendar")
    class Calendar(_message.Message):
        __slots__ = ("active_preset",)
        ACTIVE_PRESET_FIELD_NUMBER: _ClassVar[int]
        active_preset: Preset
        def __init__(self, active_preset: _Optional[_Union[Preset, str]] = ...) -> None: ...
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CALENDAR_FIELD_NUMBER: _ClassVar[int]
    active: OperationModeType
    calendar: OperationMode.Calendar
    def __init__(self, active: _Optional[_Union[OperationModeType, str]] = ..., calendar: _Optional[_Union[OperationMode.Calendar, _Mapping]] = ...) -> None: ...

class ClimateState(_message.Message):
    __slots__ = ("alarms", "power", "temperature_setpoint", "hvac_mode", "fan_speed", "flap_swing", "air_temperature", "air_humidity", "operation_mode")
    ALARMS_FIELD_NUMBER: _ClassVar[int]
    POWER_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_SETPOINT_FIELD_NUMBER: _ClassVar[int]
    HVAC_MODE_FIELD_NUMBER: _ClassVar[int]
    FAN_SPEED_FIELD_NUMBER: _ClassVar[int]
    FLAP_SWING_FIELD_NUMBER: _ClassVar[int]
    AIR_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    AIR_HUMIDITY_FIELD_NUMBER: _ClassVar[int]
    OPERATION_MODE_FIELD_NUMBER: _ClassVar[int]
    alarms: int
    power: bool
    temperature_setpoint: Setpoint
    hvac_mode: HvacModeState
    fan_speed: FanSpeedState
    flap_swing: bool
    air_temperature: float
    air_humidity: float
    operation_mode: OperationMode
    def __init__(self, alarms: _Optional[int] = ..., power: bool = ..., temperature_setpoint: _Optional[_Union[Setpoint, _Mapping]] = ..., hvac_mode: _Optional[_Union[HvacModeState, _Mapping]] = ..., fan_speed: _Optional[_Union[FanSpeedState, _Mapping]] = ..., flap_swing: bool = ..., air_temperature: _Optional[float] = ..., air_humidity: _Optional[float] = ..., operation_mode: _Optional[_Union[OperationMode, _Mapping]] = ...) -> None: ...

class AcState(_message.Message):
    __slots__ = ("alarms", "power", "temperature_setpoint", "hvac_mode", "fan_speed", "flap_swing", "air_temperature", "air_humidity", "erv", "operation_mode", "silent_mode")
    ALARMS_FIELD_NUMBER: _ClassVar[int]
    POWER_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_SETPOINT_FIELD_NUMBER: _ClassVar[int]
    HVAC_MODE_FIELD_NUMBER: _ClassVar[int]
    FAN_SPEED_FIELD_NUMBER: _ClassVar[int]
    FLAP_SWING_FIELD_NUMBER: _ClassVar[int]
    AIR_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    AIR_HUMIDITY_FIELD_NUMBER: _ClassVar[int]
    ERV_FIELD_NUMBER: _ClassVar[int]
    OPERATION_MODE_FIELD_NUMBER: _ClassVar[int]
    SILENT_MODE_FIELD_NUMBER: _ClassVar[int]
    alarms: int
    power: bool
    temperature_setpoint: Setpoint
    hvac_mode: HvacModeState
    fan_speed: FanSpeedState
    flap_swing: bool
    air_temperature: float
    air_humidity: float
    erv: bool
    operation_mode: OperationMode
    silent_mode: bool
    def __init__(self, alarms: _Optional[int] = ..., power: bool = ..., temperature_setpoint: _Optional[_Union[Setpoint, _Mapping]] = ..., hvac_mode: _Optional[_Union[HvacModeState, _Mapping]] = ..., fan_speed: _Optional[_Union[FanSpeedState, _Mapping]] = ..., flap_swing: bool = ..., air_temperature: _Optional[float] = ..., air_humidity: _Optional[float] = ..., erv: bool = ..., operation_mode: _Optional[_Union[OperationMode, _Mapping]] = ..., silent_mode: bool = ...) -> None: ...

class SubscribeEventsRequest(_message.Message):
    __slots__ = ("home_id",)
    HOME_ID_FIELD_NUMBER: _ClassVar[int]
    home_id: bytes
    def __init__(self, home_id: _Optional[bytes] = ...) -> None: ...

class Event(_message.Message):
    __slots__ = ("device",)
    class Device(_message.Message):
        __slots__ = ("mac_address", "node_id", "event")
        MAC_ADDRESS_FIELD_NUMBER: _ClassVar[int]
        NODE_ID_FIELD_NUMBER: _ClassVar[int]
        EVENT_FIELD_NUMBER: _ClassVar[int]
        mac_address: bytes
        node_id: int
        event: DeviceEvent
        def __init__(self, mac_address: _Optional[bytes] = ..., node_id: _Optional[int] = ..., event: _Optional[_Union[DeviceEvent, _Mapping]] = ...) -> None: ...
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    device: Event.Device
    def __init__(self, device: _Optional[_Union[Event.Device, _Mapping]] = ...) -> None: ...

class DeviceEvent(_message.Message):
    __slots__ = ("system", "device")
    class System(_message.Message):
        __slots__ = ("connection_established", "connection_lost")
        class ConnectionEstablished(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        class ConnectionLost(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        CONNECTION_ESTABLISHED_FIELD_NUMBER: _ClassVar[int]
        CONNECTION_LOST_FIELD_NUMBER: _ClassVar[int]
        connection_established: DeviceEvent.System.ConnectionEstablished
        connection_lost: DeviceEvent.System.ConnectionLost
        def __init__(self, connection_established: _Optional[_Union[DeviceEvent.System.ConnectionEstablished, _Mapping]] = ..., connection_lost: _Optional[_Union[DeviceEvent.System.ConnectionLost, _Mapping]] = ...) -> None: ...
    class State(_message.Message):
        __slots__ = ("ac", "fancoil", "thermostat")
        AC_FIELD_NUMBER: _ClassVar[int]
        FANCOIL_FIELD_NUMBER: _ClassVar[int]
        THERMOSTAT_FIELD_NUMBER: _ClassVar[int]
        ac: AcEvent
        fancoil: ClimateEvent
        thermostat: ClimateEvent
        def __init__(self, ac: _Optional[_Union[AcEvent, _Mapping]] = ..., fancoil: _Optional[_Union[ClimateEvent, _Mapping]] = ..., thermostat: _Optional[_Union[ClimateEvent, _Mapping]] = ...) -> None: ...
    SYSTEM_FIELD_NUMBER: _ClassVar[int]
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    system: DeviceEvent.System
    device: DeviceEvent.State
    def __init__(self, system: _Optional[_Union[DeviceEvent.System, _Mapping]] = ..., device: _Optional[_Union[DeviceEvent.State, _Mapping]] = ...) -> None: ...

class ClimateEventSetpoint(_message.Message):
    __slots__ = ("value", "min", "max", "step")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    MIN_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    value: float
    min: float
    max: float
    step: float
    def __init__(self, value: _Optional[float] = ..., min: _Optional[float] = ..., max: _Optional[float] = ..., step: _Optional[float] = ...) -> None: ...

class ClimateEvent(_message.Message):
    __slots__ = ("alarms", "power", "temperature_setpoint", "air_temperature", "hvac_mode", "fan_speed", "flap_swing", "operation_mode", "air_humidity")
    ALARMS_FIELD_NUMBER: _ClassVar[int]
    POWER_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_SETPOINT_FIELD_NUMBER: _ClassVar[int]
    AIR_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    HVAC_MODE_FIELD_NUMBER: _ClassVar[int]
    FAN_SPEED_FIELD_NUMBER: _ClassVar[int]
    FLAP_SWING_FIELD_NUMBER: _ClassVar[int]
    OPERATION_MODE_FIELD_NUMBER: _ClassVar[int]
    AIR_HUMIDITY_FIELD_NUMBER: _ClassVar[int]
    alarms: int
    power: bool
    temperature_setpoint: ClimateEventSetpoint
    air_temperature: float
    hvac_mode: HvacMode
    fan_speed: FanSpeed
    flap_swing: bool
    operation_mode: OperationMode
    air_humidity: float
    def __init__(self, alarms: _Optional[int] = ..., power: bool = ..., temperature_setpoint: _Optional[_Union[ClimateEventSetpoint, _Mapping]] = ..., air_temperature: _Optional[float] = ..., hvac_mode: _Optional[_Union[HvacMode, str]] = ..., fan_speed: _Optional[_Union[FanSpeed, str]] = ..., flap_swing: bool = ..., operation_mode: _Optional[_Union[OperationMode, _Mapping]] = ..., air_humidity: _Optional[float] = ...) -> None: ...

class AcEvent(_message.Message):
    __slots__ = ("alarms", "power", "temperature_setpoint", "air_temperature", "hvac_mode", "fan_speed", "flap_swing", "erv", "operation_mode", "air_humidity", "silent_mode")
    ALARMS_FIELD_NUMBER: _ClassVar[int]
    POWER_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_SETPOINT_FIELD_NUMBER: _ClassVar[int]
    AIR_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    HVAC_MODE_FIELD_NUMBER: _ClassVar[int]
    FAN_SPEED_FIELD_NUMBER: _ClassVar[int]
    FLAP_SWING_FIELD_NUMBER: _ClassVar[int]
    ERV_FIELD_NUMBER: _ClassVar[int]
    OPERATION_MODE_FIELD_NUMBER: _ClassVar[int]
    AIR_HUMIDITY_FIELD_NUMBER: _ClassVar[int]
    SILENT_MODE_FIELD_NUMBER: _ClassVar[int]
    alarms: int
    power: bool
    temperature_setpoint: ClimateEventSetpoint
    air_temperature: float
    hvac_mode: HvacMode
    fan_speed: FanSpeed
    flap_swing: bool
    erv: bool
    operation_mode: OperationMode
    air_humidity: float
    silent_mode: bool
    def __init__(self, alarms: _Optional[int] = ..., power: bool = ..., temperature_setpoint: _Optional[_Union[ClimateEventSetpoint, _Mapping]] = ..., air_temperature: _Optional[float] = ..., hvac_mode: _Optional[_Union[HvacMode, str]] = ..., fan_speed: _Optional[_Union[FanSpeed, str]] = ..., flap_swing: bool = ..., erv: bool = ..., operation_mode: _Optional[_Union[OperationMode, _Mapping]] = ..., air_humidity: _Optional[float] = ..., silent_mode: bool = ...) -> None: ...
