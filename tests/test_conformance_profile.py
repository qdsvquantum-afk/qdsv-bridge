from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "benchmarks" / "conformance" / "bridge-v0.7.0"


def test_070_conformance_profile_declares_the_frozen_public_boundary() -> None:
    boundary = json.loads((ROOT / "spec" / "public-boundary.json").read_text(encoding="utf-8"))

    assert boundary["status"] == "PUBLIC_BOUNDARY_FROZEN_FOR_CONFORMANCE"
    assert boundary["domain_contract"] == "qdsv_bridge_domain.v1"
    assert boundary["response_contract"] == "qdsv_bridge_public.v1"
    assert boundary["sdk_version"] == "0.7.0"
    assert "problem_spec" in boundary["privacy"]["forbidden_response_keys"]


def test_070_runner_is_black_box_and_keeps_expected_answers_separate() -> None:
    runner = (ROOT / "suite" / "run_conformance.py").read_text(encoding="utf-8")
    public_inputs = json.loads((ROOT / "fixtures" / "public_inputs.json").read_text(encoding="utf-8"))
    expected = json.loads((ROOT / "fixtures" / "expected_outputs.json").read_text(encoding="utf-8"))

    assert "import qdsv_bridge" not in runner
    assert "from qdsv_bridge" not in runner
    assert all("decisions" not in case["spec"] for case in public_inputs["cases"])
    assert set(expected["cases"]) == {case["case_id"] for case in public_inputs["cases"]}
