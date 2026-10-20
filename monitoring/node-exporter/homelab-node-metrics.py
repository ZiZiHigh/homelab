#!/usr/bin/env python3
"""Write SMART and temperature metrics for the node-exporter textfile collector.

The script intentionally exports only device paths and numeric values. It does
not export model names, serial numbers, WWNs, or raw SMART output.

Environment:
  HOMELAB_TEXTFILE_DIR   output directory (default: repo node-exporter textfile)
  HOMELAB_SMART_DEVICES  comma-separated device paths (default: /dev/sda)
"""

import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

TEXTFILE_DIR = Path(
    os.environ.get(
        "HOMELAB_TEXTFILE_DIR",
        "/opt/homelab/monitoring/node-exporter/textfile",
    )
)
OUTPUT = TEXTFILE_DIR / "homelab.prom"
SMART_DEVICES = [
    item.strip()
    for item in os.environ.get("HOMELAB_SMART_DEVICES", "/dev/sda").split(",")
    if item.strip()
]


def run(command):
    return subprocess.run(command, capture_output=True, text=True, check=False)


def json_from(command):
    result = run(command)
    if not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def raw_attribute(attributes, attribute_id):
    for attribute in attributes:
        if attribute.get("id") != attribute_id:
            continue
        raw = attribute.get("raw", {})
        value = raw.get("value")
        if isinstance(value, int):
            return value
        match = re.match(r"\s*(\d+)", str(raw.get("string", "")))
        return int(match.group(1)) if match else None
    return None


def smart_values(device):
    smartctl = shutil.which("smartctl")
    if smartctl is None:
        return None
    result = run([smartctl, "-H", "-A", "-j", device])
    if not result.stdout.strip():
        return None
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

    passed = data.get("smart_status", {}).get("passed")
    if passed is True:
        health = 1
    elif passed is False:
        health = 0
    else:
        health = -1

    values = {"health": health}

    temperature = data.get("temperature", {}).get("current")
    if isinstance(temperature, (int, float)):
        values["temperature"] = float(temperature)

    attributes = data.get("ata_smart_attributes", {}).get("table", [])
    if isinstance(attributes, list):
        for name, attribute_id in (
            ("reallocated", 5),
            ("pending", 197),
            ("offline_uncorrectable", 198),
        ):
            value = raw_attribute(attributes, attribute_id)
            if value is not None:
                values[name] = value

    return values


def cpu_temperature():
    sensors = shutil.which("sensors")
    if sensors is not None:
        data = json_from([sensors, "-j"])
        if isinstance(data, dict):
            readings = []
            for chip in data.values():
                if not isinstance(chip, dict):
                    continue
                for sensor in chip.values():
                    if not isinstance(sensor, dict):
                        continue
                    for key, value in sensor.items():
                        if (
                            key.startswith("temp")
                            and key.endswith("_input")
                            and isinstance(value, (int, float))
                            and 0 < value < 150
                        ):
                            readings.append(float(value))
            if readings:
                return max(readings)

    # Fallback for hosts where the hwmon driver is unavailable.
    readings = []
    for path in Path("/sys/class/thermal").glob("thermal_zone*/temp"):
        try:
            value = int(path.read_text(encoding="ascii").strip()) / 1000.0
        except (OSError, ValueError):
            continue
        if 0 < value < 150:
            readings.append(value)
    return max(readings) if readings else None


def main():
    lines = []
    families = set()

    def add(name, value, help_text, labels=None):
        if name not in families:
            lines.append(f"# HELP {name} {help_text}")
            lines.append(f"# TYPE {name} gauge")
            families.add(name)
        label_text = ""
        if labels:
            encoded = ",".join(
                f'{key}="{str(val).replace(chr(92), chr(92) * 2).replace(chr(34), chr(92) + chr(34))}"'
                for key, val in labels.items()
            )
            label_text = "{" + encoded + "}"
        lines.append(f"{name}{label_text} {value}")

    for device in SMART_DEVICES:
        values = smart_values(device)
        if values is None:
            add(
                "homelab_smart_health",
                -1,
                "SMART overall-health: 1 passed, 0 failing, -1 unknown.",
                {"device": device},
            )
            continue

        add(
            "homelab_smart_health",
            values["health"],
            "SMART overall-health: 1 passed, 0 failing, -1 unknown.",
            {"device": device},
        )
        if "temperature" in values:
            add(
                "homelab_smart_temperature_celsius",
                values["temperature"],
                "SMART device temperature in degrees Celsius.",
                {"device": device},
            )
        for metric, help_text in (
            ("reallocated", "SMART reallocated sector count."),
            ("pending", "SMART current pending sector count."),
            ("offline_uncorrectable", "SMART offline uncorrectable sector count."),
        ):
            if metric in values:
                add(
                    f"homelab_smart_{metric}_sectors",
                    values[metric],
                    help_text,
                    {"device": device},
                )

    temperature = cpu_temperature()
    if temperature is not None:
        add(
            "homelab_cpu_temperature_celsius",
            temperature,
            "Highest CPU/hwmon temperature in degrees Celsius.",
        )

    add(
        "homelab_node_metrics_last_run_timestamp_seconds",
        int(time.time()),
        "Unix timestamp of the last successful SMART/temperature metric run.",
    )

    TEXTFILE_DIR.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_name(OUTPUT.name + ".tmp")
    temporary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.chmod(temporary, 0o644)
    os.replace(temporary, OUTPUT)
    print(f"wrote {OUTPUT} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
