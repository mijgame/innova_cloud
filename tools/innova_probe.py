#!/usr/bin/env python3
"""Probe the Innova Cloud v2 API outside Home Assistant.

Logs in, lists homes/devices, dumps each device's state and optionally listens
to the event stream or sends a command. Useful to check whether the
integration's assumptions still hold.

Requires: pip install grpcio protobuf

Credentials are read from INNOVA_EMAIL / INNOVA_PASSWORD, or prompted for.

Examples:
  python tools/innova_probe.py                     # login, list devices, dump state
  python tools/innova_probe.py --events 120        # also print events for 2 minutes
  python tools/innova_probe.py --set hvac_mode=3   # send a set_state (here: COOL)
  python tools/innova_probe.py --set power=1 --set temperature_setpoint=21.5
"""
import argparse
import asyncio
import getpass
import json
import os
import sys
import types
import urllib.error
import urllib.request
import uuid
from pathlib import Path

try:
    import grpc
    from google.protobuf import text_format
except ImportError:
    sys.exit("Missing dependencies; run with a Python that has them: pip install grpcio protobuf")

API_BASE_URL = "https://v2.api.innova.solutiontech.tech/app"
GRPC_TARGET = "v2.grpc.innova.solutiontech.tech:443"

# Load the generated protobuf modules from the integration without importing
# its __init__.py (which needs Home Assistant).
_PKG_DIR = Path(__file__).resolve().parent.parent / "custom_components" / "innova_heater"
_pkg = types.ModuleType("innova_proto")
_pkg.__path__ = [str(_PKG_DIR)]
sys.modules["innova_proto"] = _pkg
from innova_proto import app_service_pb2 as pb, app_service_pb2_grpc as pb_grpc  # noqa: E402


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
    return token


def list_homes(token: str) -> list[dict]:
    status, homes = http_json("GET", f"{API_BASE_URL}/homes", token=token)
    if status != 200:
        print(f"GET /homes FAILED: HTTP {status}: {homes}")
        sys.exit(1)
    for home in homes:
        rooms = {r.get("id"): r.get("name") for r in home.get("rooms", [])}
        print(f"home {home.get('name')!r} id={home.get('id')} keys={sorted(home)}")
        for device in home.get("devices", []):
            print(f"  device {device.get('name')!r} mac={device.get('macAddress')} node={device.get('nodeId')} "
                  f"room={rooms.get(device.get('roomId'))!r} uid={device.get('uid')} "
                  f"fw={device.get('fwVersionCode')} serial={device.get('serialNumber')}")
    return homes


def mac_bytes(mac: str) -> bytes:
    return bytes(int(part, 16) for part in mac.split(":"))


def coerce(value: str):
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    return float(value) if "." in value else int(value)


async def run_grpc(token: str, homes: list[dict], mac_filter, events_seconds: int, sets: dict):
    metadata = [("authorization", f"Bearer {token}")]
    async with grpc.aio.secure_channel(GRPC_TARGET, grpc.ssl_channel_credentials()) as channel:
        stub = pb_grpc.AppServiceStub(channel)
        devices = [(h, d) for h in homes for d in h.get("devices", [])
                   if not mac_filter or d.get("macAddress", "").lower() == mac_filter.lower()]

        node_types = {}
        for home, device in devices:
            print(f"\n=== get_state {device['name']!r} ({device['macAddress']} node {device.get('nodeId', 0)}) ===")
            request = pb.SendDeviceRequest(
                mac_address=mac_bytes(device["macAddress"]),
                node_id=device.get("nodeId", 0),
                request=pb.DeviceRequest(shared=pb.SharedRequest(get_state=pb.SharedRequest.GetState())),
            )
            response = await stub.SendDevice(request, metadata=metadata, timeout=10)
            print(text_format.MessageToString(response))
            if response.WhichOneof("type") == "device":
                node = response.device.shared.state.nodes.get(device.get("nodeId", 0))
                if node is not None:
                    node_types[device["macAddress"]] = node.WhichOneof("type")

        if sets and devices:
            home, device = devices[0]
            state = pb.ClimateRequest.SetState(**{k: coerce(v) for k, v in sets.items()})
            # Use the node type reported by get_state; default to fancoil
            node_type = node_types.get(device["macAddress"])
            if node_type not in ("ac", "fancoil", "thermostat"):
                node_type = "fancoil"
            print(f"\n=== set_state ({node_type}) {text_format.MessageToString(state, as_one_line=True)} ===")
            request = pb.SendDeviceRequest(
                mac_address=mac_bytes(device["macAddress"]),
                node_id=device.get("nodeId", 0),
                request=pb.DeviceRequest(**{node_type: pb.ClimateRequest(set_state=state)}),
            )
            print(text_format.MessageToString(await stub.SendDevice(request, metadata=metadata, timeout=10)) or "(empty response)")

        if events_seconds:
            for home in homes:
                print(f"\n=== Events for home {home.get('name')!r} for {events_seconds}s (change things in the app now) ===")
                call = stub.SubscribeEvents(pb.SubscribeEventsRequest(home_id=uuid.UUID(home["id"]).bytes), metadata=metadata)
                try:
                    async with asyncio.timeout(events_seconds):
                        async for event in call:
                            d = event.device
                            print(f"  mac={d.mac_address.hex(':')} node={d.node_id}: "
                                  f"{text_format.MessageToString(d.event, as_one_line=True)}")
                except TimeoutError:
                    call.cancel()
                    print("  (done)")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mac", help="only this device MAC (AA:BB:CC:DD:EE:FF)")
    parser.add_argument("--events", type=int, default=0, metavar="SECONDS", help="listen to events")
    parser.add_argument("--set", action="append", default=[], metavar="FIELD=VALUE",
                        help="set_state field: power, temperature_setpoint, hvac_mode (1=auto 2=heat "
                             "3=cool 4=dry 5=fan), fan_speed (1=auto 2=min 3=mid 4=max 5=boost), flap_swing")
    args = parser.parse_args()
    sets = dict(s.split("=", 1) for s in args.set)

    email = os.environ.get("INNOVA_EMAIL") or input("Email: ")
    password = os.environ.get("INNOVA_PASSWORD") or getpass.getpass("Password: ")

    token = login(email.strip().lower(), password)
    homes = list_homes(token)
    if not any(h.get("devices") for h in homes):
        print("No devices found")
        sys.exit(1)

    try:
        asyncio.run(run_grpc(token, homes, args.mac, args.events, sets))
    except grpc.aio.AioRpcError as err:
        print(f"gRPC error: {err.code().name}: {err.details()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
