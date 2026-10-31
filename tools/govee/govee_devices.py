#!/usr/bin/env python3
"""List Govee devices (and optionally their live state) via the Govee Open API v2.

Usage:
  GOVEE_API_KEY=... python3 govee_devices.py            # table of devices + capabilities
  GOVEE_API_KEY=... python3 govee_devices.py --state    # also query each device's current state
  GOVEE_API_KEY=... python3 govee_devices.py --json     # raw JSON

Docs: https://developer.govee.com/reference/get-you-devices
"""
import json
import os
import sys
import urllib.request
import uuid

BASE = "https://openapi.api.govee.com/router/api/v1"


def call(method, path, key, body=None):
    req = urllib.request.Request(
        BASE + path,
        method=method,
        headers={"Govee-API-Key": key, "Content-Type": "application/json"},
        data=json.dumps(body).encode() if body else None,
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def main():
    key = os.environ.get("GOVEE_API_KEY")
    if not key:
        sys.exit("Set GOVEE_API_KEY")
    args = set(sys.argv[1:])

    devices = call("GET", "/user/devices", key).get("data", [])
    if "--state" in args:
        for d in devices:
            body = {"requestId": str(uuid.uuid4()), "payload": {"sku": d["sku"], "device": d["device"]}}
            d["state"] = call("POST", "/device/state", key, body).get("payload", {}).get("capabilities", [])

    if "--json" in args:
        print(json.dumps(devices, indent=2))
        return

    print(f"{len(devices)} device(s)\n")
    for d in devices:
        print(f"{d.get('deviceName', '?')}  [{d['sku']}]  {d.get('type', '').split('.')[-1]}  id={d['device']}")
        for c in d.get("capabilities", []):
            print(f"    - {c['type'].split('.')[-1]}: {c['instance']}")
        for s in d.get("state", []):
            print(f"    = {s['instance']}: {s.get('state', {}).get('value')}")
        print()


if __name__ == "__main__":
    main()
