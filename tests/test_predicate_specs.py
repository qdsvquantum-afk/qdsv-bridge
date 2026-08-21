from __future__ import annotations

from copy import deepcopy

import pytest

from qdsv_bridge import (
    PredicateSpecError,
    build_predicate_spec,
    build_score_expression_spec,
    build_score_model_spec,
)


def field(name: str) -> dict:
    return {"op": "field", "name": name}


def const(value: int) -> dict:
    return {"op": "const", "value": value}


def test_builds_nary_compound_predicate_without_answers() -> None:
    rows = [
        {"quality": 800, "delivery": 700, "compliance": 1},
        {"quality": 720, "delivery": 600, "compliance": 1},
    ]
    predicate = {
        "op": "and",
        "args": [
            {"op": "gte", "left": field("quality"), "right": const(700)},
            {"op": "gte", "left": field("delivery"), "right": const(650)},
            {"op": "eq", "left": field("compliance"), "right": const(1)},
        ],
    }

    spec = build_predicate_spec(rows=rows, predicate=predicate, shots=256)

    problem = spec["problem_spec"]
    assert problem["domain"]["end"] == 1
    assert problem["predicate"]["op"] == "and"
    assert problem["predicate"]["args"][0]["op"] == "and"
    assert problem["predicate"]["execution_strategy"] == "semantic_auto"
    assert [row["candidate_index"] for row in problem["data_binding"]["datasets"][0]["rows"]] == [0, 1]
    assert "expected" not in repr(spec).lower()
    assert "decision" not in repr(spec).lower()


def test_preserves_field_to_field_comparisons() -> None:
    predicate = {
        "op": "and",
        "args": [
            {"op": "lte", "left": field("cost"), "right": field("budget")},
            {"op": "gte", "left": field("benefit"), "right": field("minimum")},
        ],
    }
    spec = build_predicate_spec(
        rows=[{"cost": 400, "budget": 600, "benefit": 750, "minimum": 700}],
        predicate=predicate,
    )

    comparisons = spec["problem_spec"]["predicate"]["args"]
    assert comparisons[0]["args"][1]["column"] == "budget"
    assert comparisons[1]["args"][1]["column"] == "minimum"


def test_building_spec_does_not_mutate_inputs() -> None:
    rows = [{"candidate_index": 0, "risk": 800}]
    predicate = {"op": "gte", "left": field("risk"), "right": const(700)}
    original_rows = deepcopy(rows)
    original_predicate = deepcopy(predicate)

    build_predicate_spec(rows=rows, predicate=predicate)

    assert rows == original_rows
    assert predicate == original_predicate


def test_freezes_explicit_logical_optimization_contract() -> None:
    contract = {
        "mode": "auto",
        "profile": "qiskit_structural_exact_v1",
        "acceptance_policy": "pareto_no_regression_v1",
    }

    spec = build_predicate_spec(
        rows=[{"candidate_index": 0, "risk": 1}],
        predicate={"op": "gte", "left": field("risk"), "right": const(1)},
        logical_optimization=contract,
    )

    assert spec["target"]["logical_optimization"] == contract
    contract["mode"] = "off"
    assert spec["target"]["logical_optimization"]["mode"] == "auto"


@pytest.mark.parametrize("operation", ["not", "is_null", "not_null", "floor", "ceil", "round"])
def test_unary_operations_use_the_canonical_value_operand(operation: str) -> None:
    spec = build_predicate_spec(
        rows=[{"candidate_index": 0, "value": 1}],
        predicate={"op": operation, "arg": field("value")},
    )

    predicate = spec["problem_spec"]["predicate"]
    assert predicate["op"] == operation
    assert predicate["value"]["op"] == "field"
    assert "args" not in predicate


def test_weighted_sum_has_an_unambiguous_vector_contract() -> None:
    spec = build_score_expression_spec(
        rows=[{"a": 2, "b": 3}],
        expression={
            "op": "weighted_sum",
            "values": [field("a"), field("b")],
            "weights": [2, 3],
        },
        threshold=10,
        output_scale=100,
    )

    expression = spec["problem_spec"]["model"]["score"]["terms"][0]["value"]
    assert expression["op"] == "weighted_sum"
    assert [item["op"] for item in expression["args"]] == ["vector", "vector"]
    assert expression["args"][1]["args"] == [2, 3]
    assert "expected" not in repr(spec).lower()


def test_builds_public_hierarchical_score_model_without_answers() -> None:
    spec = build_score_model_spec(
        rows=[{"quality": 8, "risk": 2}, {"quality": 4, "risk": 7}],
        threshold=5,
        blocks=[
            {
                "name": "performance",
                "importance": 2,
                "priority": 1,
                "terms": [{"name": "quality", "value": field("quality")}],
            },
            {
                "name": "exposure",
                "importance": 1,
                "priority": 2,
                "terms": [{"name": "risk", "value": field("risk")}],
            },
        ],
        output_scale=10,
    )

    model = spec["problem_spec"]["model"]
    assert model["version"] == "2.0"
    assert [block["name"] for block in model["score"]["blocks"]] == [
        "performance",
        "exposure",
    ]
    assert model["score"]["blocks"][0]["terms"][0]["value"]["column"] == "quality"
    assert "expected" not in repr(spec).lower()
    assert "answer" not in repr(spec).lower()


def test_score_model_requires_exactly_one_structure() -> None:
    with pytest.raises(PredicateSpecError, match="Exactly one"):
        build_score_model_spec(rows=[{"x": 1}], threshold=1)


@pytest.mark.parametrize(
    ("rows", "predicate", "message"),
    [
        ([], {"op": "eq", "args": [1, 1]}, "non-empty"),
        ([{"candidate_index": 4}], {"op": "eq", "args": [1, 1]}, "stable row index"),
        ([{}], {"op": "and", "args": [True]}, "at least two"),
    ],
)
def test_rejects_ambiguous_public_specs(rows, predicate, message: str) -> None:
    with pytest.raises(PredicateSpecError, match=message):
        build_predicate_spec(rows=rows, predicate=predicate)
