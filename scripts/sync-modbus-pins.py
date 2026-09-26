#!/usr/bin/env python3
"""Install the core ``modbus`` integration's requirements into the current env.

The test suite imports ``homeassistant.components.modbus`` (it is a declared
dependency of the integration, and its ``async_get_unit`` seam is patched in
tests), which transitively imports the Modbus backends pinned by the core
``modbus`` integration. Rather than mirroring those pins by hand in
``dev-requirements.txt`` — where they go stale when HA bumps them — read them
from the installed HA core manifest and install exactly that set.

Run after ``requirements.txt`` (which pins ``homeassistant``) is installed.
"""

import json
import subprocess
import sys
from pathlib import Path

import homeassistant

manifest = (
    Path(homeassistant.__file__).parent / "components" / "modbus" / "manifest.json"
)
requirements = json.loads(manifest.read_text(encoding="utf-8"))["requirements"]

print(f"Installing core modbus requirements: {', '.join(requirements)}", flush=True)
sys.exit(subprocess.call([sys.executable, "-m", "pip", "install", *requirements]))
