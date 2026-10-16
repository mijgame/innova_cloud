#!/usr/bin/env python3
"""Probe the Innova Cloud API outside Home Assistant.

Logs in, lists devices, dumps GetDeviceStatus and optionally listens to the
event stream or sends a SetDeviceValue command. Useful to check whether the
integration's assumptions (mode numbers, event types, ...) still hold.

Requires: pip install grpcio protobuf

Credentials are read from INNOVA_EMAIL / INNOVA_PASSWORD, or prompted for.

Examples:
  python tools/innova_probe.py                      # login, list devices, dump status
  python tools/innova_probe.py --events 120         # also print events for 2 minutes
  python tools/innova_probe.py --set 3 2            # send type=3 (operation mode) value=2
"""
import argparse
import asyncio
import getpass
import json
import os
import struct
import sys
import types
import urllib.error
import urllib.request
from pathlib import Path

try:
    import grpc
    from google.protobuf import empty_pb2, text_format
except ImportError:
    sys.exit("Missing dependencies; run with a Python that has them: pip install grpcio protobuf")

API_BASE_URL = "https://api.innova.solutiontech.tech/api"
GRPC_TARGET = "grpc.innova.solutiontech.tech:443"

# Load the generated protobuf modules from the integration without importing
# its __init__.py (which needs Home Assistant).
_PKG_DIR = Path(__file__).resolve().parent.parent / "custom_components" / "innova_heater"
_pkg = types.ModuleType("innova_proto")
_pkg.__path__ = [str(_PKG_DIR)]
sys.modules["innova_proto"] = _pkg
from innova_proto import controls_pb2, controls_pb2_grpc  # noqa: E402

EVENT_NAMES = {
    1: "power_state (legacy)",
    3: "operation_mode (legacy)",
    4: "fan_speed (legacy)",
    249: "manual_mode",
    250: "flap",
    251: "fan_speed",
    252: "operation_mode",
    253: "room_temp",
    254: "setpoint",
    255: "power_state",
}


def http_json(method: str, url: str, body=None, token=None):
    """Do an HTTP request and return (status, parsed body or raw text)."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            status, raw = resp.status, resp.read().decode()
    except urllib.error.HTTPError as err:
        status, raw = err.code, err.read().decode()
    try:
        return status, json.loads(raw)
    except ValueError:
        return status, raw


def login(email: str, password: str) -> str:
    status, body = http_json("POST", f"{API_BASE_URL}/users/login", {"email": email, "password": password})
    if status != 200 or not isinstance(body, dict) or not body.get("token"):
        print(f"Login FAILED: HTTP {status}: {body}")
        sys.exit(1)
    token = body["token"]
    print(f"Login OK (token {token[:12]}..., {len(token)} chars)")
    print(f"  response keys: {sorted(body)}")
    return token


def list_devices(token: str) -> list[dict]:
    status, homes = http_json("GET", f"{API_BASE_URL}/homes", token=token)
    if status != 200:
        print(f"GET /homes FAILED: HTTP {status}: {homes}")
        sys.exit(1)
    devices = []
    for home in homes:
        for room in home.get("rooms", []):
            for device in room.get("devices", []):
                devices.append(device)
                print(f"  device: {device.get('name')!r} mac={device.get('macAddress')} "
                      f"room={room.get('name')!r} home={home.get('name')!r}")
                extra = {k: v for k, v in device.items() if k not in ("name", "macAddress")}
                if extra:
                    print(f"    other fields: {json.dumps(extra)}")
    return devices


async def run_grpc(token: str, mac: str, events_seconds: int, set_value):
    metadata = [("mac_address", mac), ("authorization", f"Bearer {token}")]
    async with grpc.aio.secure_channel(GRPC_TARGET, grpc.ssl_channel_credentials()) as channel:
        stub = controls_pb2_grpc.ControlsStub(channel)

        status = await stub.GetDeviceStatus(empty_pb2.Empty(), metadata=metadata)
        print("\n=== GetDeviceStatus ===")
        print(text_format.MessageToString(status))
        main = status.main_status
        print(f"device_status oneof: {main.WhichOneof('device_status')}")
        # Fields the server sent that our .proto doesn't know about = API drift
        unknown = []
        for msg in (status, main, getattr(main, main.WhichOneof('device_status') or "", None)):
            if msg is not None and msg.UnknownFields():
                unknown.append((type(msg).__name__, [f.field_number for f in msg.UnknownFields()]))
        print(f"unknown (not in controls.proto) fields: {unknown or 'none'}")

        if set_value:
            op_type, value = set_value
            print(f"\n=== SetDeviceValue type={op_type} value={value} ===")
            await stub.SetDeviceValue(controls_pb2.SetDeviceValueRequest(type=op_type, value=value),
                                      metadata=metadata)
            print("sent OK")

        if events_seconds:
            print(f"\n=== Events for {events_seconds}s (change things in the app now) ===")
            call = stub.SubscribeToDeviceEvents(empty_pb2.Empty(), metadata=metadata)
            try:
                async with asyncio.timeout(events_seconds):
                    async for event in call:
                        value = event.value
                        as_int = struct.unpack(">H", value[:2])[0] if len(value) >= 2 else None
                        print(f"  type={event.type:<4} {EVENT_NAMES.get(event.type, '?'):<24} "
                              f"raw={value.hex():<12} as_u16={as_int}")
            except TimeoutError:
                call.cancel()
                print("  (done)")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mac", help="device MAC (default: first device on the account)")
    parser.add_argument("--events", type=int, default=0, metavar="SECONDS", help="listen to events")
    parser.add_argument("--set", type=int, nargs=2, metavar=("TYPE", "VALUE"),
                        help="send SetDeviceValue (1=power 2=setpoint*10 3=mode 4=fan 5=flap)")
    args = parser.parse_args()

    email = os.environ.get("INNOVA_EMAIL") or input("Email: ")
    password = os.environ.get("INNOVA_PASSWORD") or getpass.getpass("Password: ")

    token = login(email.strip(), password)
    devices = list_devices(token)
    mac = args.mac or (devices[0].get("macAddress") if devices else None)
    if not mac:
        print("No devices found")
        sys.exit(1)
    print(f"Using device {mac}")

    try:
        asyncio.run(run_grpc(token, mac, args.events, args.set))
    except grpc.aio.AioRpcError as err:
        print(f"gRPC error: {err.code().name}: {err.details()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
