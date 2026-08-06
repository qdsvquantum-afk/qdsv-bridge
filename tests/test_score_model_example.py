from __future__ import annotations

import importlib.util
from pathlib import Path


EXAMPLE_PATH = Path(__file__).parents[1] / "examples" / "score_model_v2.py"


def _load_example_module():
    spec = importlib.util.spec_from_file_location("score_model_v2_example", EXAMPLE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_score_model_example_uses_only_the_public_high_level_contract() -> None:
    payload = _load_example_module().build_spec()

    assert "problem_spec" not in payload
    assert payload["state_space"]["candidate_count"] == 2
    assert payload["signals"] == ["readiness", "reliability"]
    assert len(payload["prepared_candidates"]) == 2
    assert all("decision" not in candidate for candidate in payload["prepared_candidates"])
    assert all("expected" not in candidate for candidate in payload["prepared_candidates"])
    assert all(item["priority"] == 1 for item in payload["goal"]["criteria"])
    assert payload["target"]["format"] == "qasm3"


def test_score_model_example_keeps_inputs_and_cutoff_on_one_declared_scale() -> None:
    payload = _load_example_module().build_spec()
    cutoff = payload["goal"]["threshold"]

    assert 0 <= cutoff <= 1000
    assert all(
        isinstance(value, int) and 0 <= value <= 1000
        for candidate in payload["prepared_candidates"]
        for value in candidate.values()
    )


def test_score_model_tutorial_does_not_publish_aggregation_mechanics() -> None:
    tutorial = (
        Path(__file__).parents[1] / "docs" / "tutorials" / "score_model_v2.rst"
    ).read_text(encoding="utf-8")

    forbidden = ("weighted numerator", "normalization mass", "their product is used")
    assert not any(phrase in tutorial.lower() for phrase in forbidden)
