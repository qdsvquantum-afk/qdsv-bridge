from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_public_distribution_policy_is_frozen_for_070() -> None:
    policy = json.loads((ROOT / "packaging" / "public-distribution-policy.json").read_text(encoding="utf-8"))

    assert policy["schema_version"] == "qdsv_bridge_public_distribution.v1"
    assert policy["sdk_version"] == "0.7.0"
    assert {"domain.py", "qiskit.py", "release_manifest.json"}.issubset(policy["allowed_package_files"])
    assert {"compiler", "lowering", "intermediate", "ir"}.issubset(policy["forbidden_module_stems"])
    assert "semantic_ir" in policy["forbidden_content_markers"]
