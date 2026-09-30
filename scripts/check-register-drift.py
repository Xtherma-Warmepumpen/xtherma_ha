#!/usr/bin/env python3
"""Detect drift between the Fernportal REST API and the quantity/binding tables.

The vendor confirmed that a value can exist either only in the REST API or
only via Modbus TCP, so the API surface evolves independently of the device
model. This tool captures the set of keys the API currently serves
(live, or from a captured response such as ``tests/fixtures/rest_response.json``,
refreshed via ``tests/fixtures/update.sh``) and diffs it against

- the quantity table (``pytherma.quantities.QUANTITY_BY_KEY``) and
- the REST bindings (``pytherma.bindings.REST_BINDINGS``).

Modbus-side drift is intentionally not checked: holding registers always
answer, so an unsupported address is indistinguishable from a zero value.

Exit codes: 0 = no drift, 1 = drift found, 2 = capture/usage error.

Usage (from the repository root, in the HA venv)::

    python scripts/check-register-drift.py                  # captured fixture
    python scripts/check-register-drift.py --fixture F.json # other capture
    API_KEY=... SERIAL_NO=... python scripts/check-register-drift.py --live
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from custom_components.xtherma_fp.const import FERNPORTAL_URL
from custom_components.xtherma_fp.pytherma.bindings import (
    REST_BINDINGS,
)
from custom_components.xtherma_fp.pytherma.quantities import QUANTITY_BY_KEY

DEFAULT_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "rest_response.json"


def _fetch_live(
    url: str, api_key: str, serial: str, timeout_s: int = 30
) -> dict[str, Any]:
    """Fetch one device response from the live Fernportal API.

    Same request shape as ``xtherma_client_rest.async_get_data``.
    """
    request = urllib.request.Request(  # noqa: S310 - fixed https portal URL
        f"{url}/{serial}",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    with urllib.request.urlopen(request, timeout=timeout_s) as response:  # noqa: S310 - fixed https portal URL
        response.raise_for_status()
        payload: dict[str, Any] = json.load(response)
        return payload


def _api_entries(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Collect the ``telemetry`` + ``settings`` entries of a response by key."""
    entries: dict[str, dict[str, Any]] = {}
    for section in ("telemetry", "settings"):
        for entry in payload.get(section) or []:
            key = entry.get("key")
            if key:
                entries[key] = entry
    return entries


def _drift_sections(
    entries: dict[str, dict[str, Any]],
) -> list[tuple[str, list[str]]]:
    """Compare the captured API keys against the quantity and REST binding tables."""
    api_keys = set(entries)
    quantity_keys = set(QUANTITY_BY_KEY)
    rest_api_keys = {binding.resolved_api_key for binding in REST_BINDINGS}
    sections: list[tuple[str, list[str]]] = [
        (
            "exposed via REST but no longer served by the API",
            sorted(rest_api_keys - api_keys),
        ),
        (
            "served by the API but missing a quantity",
            sorted(api_keys - quantity_keys),
        ),
        (
            "served by the API with a known quantity, but missing a REST binding",
            sorted((api_keys & quantity_keys) - rest_api_keys),
        ),
        (
            "REST binding api_key diverges from the quantity key (wire rename)",
            sorted(
                f"{binding.resolved_api_key}: quantity key={binding.quantity.key!r}"
                for binding in REST_BINDINGS
                if binding.api_key is not None
                and binding.api_key != binding.quantity.key
            ),
        ),
    ]

    factor_drift: list[str] = []
    unit_drift: list[str] = []
    for key, entry in sorted(entries.items()):
        quantity = QUANTITY_BY_KEY.get(key)
        if quantity is None:
            continue
        api_factor = str(entry.get("output_factor") or "").strip()
        if api_factor and api_factor != (quantity.factor or ""):
            factor_drift.append(f"{key}: api={api_factor!r} qty={quantity.factor!r}")
        api_unit = str(entry.get("unit") or "").strip()
        if api_unit and quantity.unit and api_unit != quantity.unit:
            unit_drift.append(f"{key}: api={api_unit!r} qty={quantity.unit!r}")
    sections.append(
        ("factor mismatch (API self-description vs quantity table)", factor_drift)
    )
    sections.append(
        ("unit mismatch (API self-description vs quantity table)", unit_drift)
    )
    return sections


def main(argv: list[str] | None = None) -> int:
    """Run the drift check and print a report."""
    parser = argparse.ArgumentParser(
        description=(
            "Detect drift between the Fernportal REST API and the register "
            "map / REST key set."
        )
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        default=DEFAULT_FIXTURE,
        help="captured REST response JSON (default: %(default)s)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help=(
            "query the live API instead of the fixture (env API_KEY/SERIAL_NO "
            f"or --api-key/--serial, same as {DEFAULT_FIXTURE.parent}/update.sh)"
        ),
    )
    parser.add_argument("--url", help="API base URL (default: integration const)")
    parser.add_argument("--api-key", default=os.environ.get("API_KEY", ""))
    parser.add_argument("--serial", default=os.environ.get("SERIAL_NO", ""))
    args = parser.parse_args(argv)

    if args.live:
        if not (args.api_key and args.serial):
            print("live mode requires API_KEY/SERIAL_NO (or --api-key/--serial)")
            return 2
        payload = _fetch_live(args.url or FERNPORTAL_URL, args.api_key, args.serial)
    else:
        if not args.fixture.is_file():
            print(f"fixture not found: {args.fixture}")
            return 2
        payload = json.loads(args.fixture.read_text(encoding="utf-8"))

    entries = _api_entries(payload)
    if not entries:
        print("capture contains no telemetry/settings entries")
        return 2

    sections = _drift_sections(entries)
    drift = any(items for _, items in sections)
    print(
        f"capture: {len(entries)} API keys, "
        f"quantities: {len(QUANTITY_BY_KEY)}, "
        f"REST bindings: {len(REST_BINDINGS)}"
    )
    for title, items in sections:
        if not items:
            continue
        print(f"\n{title}:")
        for item in items:
            print(f"  {item}")
    print("\nDRIFT DETECTED" if drift else "\nno drift detected")
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
