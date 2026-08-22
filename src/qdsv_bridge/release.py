from __future__ import annotations

import json
from copy import deepcopy
from importlib.resources import files
from typing import Any


def get_release_manifest() -> dict[str, Any]:
    """Return the packaged public identity and validation record for this release."""

    manifest_path = files("qdsv_bridge").joinpath("release_manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return deepcopy(manifest)
