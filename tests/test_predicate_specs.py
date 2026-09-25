from __future__ import annotations

import pytest

from qdsv_bridge import (
    DomainRequestError,
    PUBLIC_DOMAIN_CONTRACT,
    const,
    field,
    predicate_request,
    score_request,
)


def test_predicate_request_contains_only_the_public_domain_envelope() -> None:
    request = predicate_request(
        candidates=[{"supplier_id": 101, "quality": 820}],
        rule={"op": "gte", "left": field("quality"), "right": const(700)},
        format="qasm2",
    )

    assert request["contract"] == PUBLIC_DOMAIN_CONTRACT
    assert request["problem"]["kind"] == "bounded_predicate"
    assert request["problem"]["candidates"][0]["supplier_id"] == 101
    assert request["delivery"]["format"] == "qasm2"
    assert "problem_spec" not in request
    assert "oracle_spec" not in request


def test_score_request_keeps_decision_data_without_exposing_a_circuit_model() -> None:
    request = score_request(
        candidates=[{"quality": 8, "risk": 2}],
        decision={"operator": "gte", "threshold": 5},
        criteria=[{"name": "quality", "value": field("quality"), "importance": 2}],
    )

    assert request["problem"]["kind"] == "bounded_score"
    assert request["problem"]["model"]["criteria"][0]["name"] == "quality"
    assert "score_model" not in request
    assert "execution_strategy" not in request


@pytest.mark.parametrize("format", ["ir", "oracle_spec", "problem_spec", "qiskit_blueprint"])
def test_rejects_nonportable_delivery_formats(format: str) -> None:
    with pytest.raises(DomainRequestError):
        predicate_request(
            candidates=[{"value": 1}],
            rule={"op": "eq", "left": field("value"), "right": const(1)},
            format=format,
        )


def test_rejects_ambiguous_score_structure() -> None:
    with pytest.raises(DomainRequestError):
        score_request(
            candidates=[{"value": 1}],
            decision={"operator": "gte", "threshold": 1},
        )
