"""Stable domain requests for the QDSV Bridge service.

This module deliberately describes a user's prepared decision problem, rather
than QDSV's internal representation or compilation pipeline. The service is
the only component that translates this request into a portable circuit.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence


PUBLIC_DOMAIN_CONTRACT = "qdsv_bridge_domain.v1"
_DELIVERY_FORMATS = {"qasm2", "qasm3", "qiskit_blueprint"}


class DomainRequestError(ValueError):
    """Raised when a public Bridge domain request is malformed."""


def field(name: str) -> dict[str, str]:
    """Refer to a field in each prepared candidate record."""

    clean = str(name).strip()
    if not clean:
        raise DomainRequestError("field name must be non-empty.")
    return {"op": "field", "name": clean}


def const(value: Any) -> dict[str, Any]:
    """Embed a literal in a public decision rule."""

    return {"op": "const", "value": deepcopy(value)}


def predicate_request(
    *,
    candidates: Sequence[Mapping[str, Any]],
    rule: Mapping[str, Any],
    candidate_id_field: str = "candidate_index",
    format: str = "qasm3",
    framework: str = "qiskit",
    mode: str = "build",
    shots: int = 1024,
    max_qubits: int | None = None,
    max_depth: int | None = None,
    logical_optimization: bool | Mapping[str, Any] = True,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a bounded predicate request without constructing a circuit."""

    if not isinstance(rule, Mapping):
        raise DomainRequestError("rule must be a JSON object.")
    return _base_request(
        candidates=candidates,
        candidate_id_field=candidate_id_field,
        format=format,
        framework=framework,
        mode=mode,
        shots=shots,
        max_qubits=max_qubits,
        max_depth=max_depth,
        logical_optimization=logical_optimization,
        metadata=metadata,
        problem={"kind": "bounded_predicate", "rule": deepcopy(dict(rule))},
    )


def score_request(
    *,
    candidates: Sequence[Mapping[str, Any]],
    decision: Mapping[str, Any],
    criteria: Sequence[Mapping[str, Any]] | None = None,
    groups: Sequence[Mapping[str, Any]] | None = None,
    candidate_id_field: str = "candidate_index",
    format: str = "qasm3",
    framework: str = "qiskit",
    mode: str = "build",
    shots: int = 1024,
    penalty: Any = 0,
    numeric_preferences: Mapping[str, Any] | None = None,
    max_qubits: int | None = None,
    max_depth: int | None = None,
    logical_optimization: bool | Mapping[str, Any] = True,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a bounded multi-criterion decision request without computing scores."""

    if not isinstance(decision, Mapping) or "threshold" not in decision:
        raise DomainRequestError("decision must include an operator and threshold.")
    if (criteria is None) == (groups is None):
        raise DomainRequestError("Provide exactly one of criteria or groups.")
    model: dict[str, Any] = {
        "decision": deepcopy(dict(decision)),
        "penalty": deepcopy(penalty),
        "numeric_preferences": deepcopy(dict(numeric_preferences or {})),
    }
    if criteria is not None:
        model["criteria"] = _object_list(criteria, "criteria")
    else:
        model["groups"] = _object_list(groups or [], "groups")
    return _base_request(
        candidates=candidates,
        candidate_id_field=candidate_id_field,
        format=format,
        framework=framework,
        mode=mode,
        shots=shots,
        max_qubits=max_qubits,
        max_depth=max_depth,
        logical_optimization=logical_optimization,
        metadata=metadata,
        problem={"kind": "bounded_score", "model": model},
    )


def _base_request(
    *,
    candidates: Sequence[Mapping[str, Any]],
    candidate_id_field: str,
    format: str,
    framework: str,
    mode: str,
    shots: int,
    max_qubits: int | None,
    max_depth: int | None,
    logical_optimization: bool | Mapping[str, Any],
    metadata: Mapping[str, Any] | None,
    problem: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes)) or not candidates:
        raise DomainRequestError("candidates must be a non-empty sequence of objects.")
    prepared = _object_list(candidates, "candidates")
    delivery_format = str(format).strip().lower()
    if delivery_format not in _DELIVERY_FORMATS:
        raise DomainRequestError(f"format must be one of {sorted(_DELIVERY_FORMATS)}.")
    if str(mode).strip().lower() not in {"use", "build"}:
        raise DomainRequestError("mode must be use or build.")
    if int(shots) < 1:
        raise DomainRequestError("shots must be a positive integer.")
    guardrails = {
        key: int(value)
        for key, value in (("max_qubits", max_qubits), ("max_depth", max_depth))
        if value is not None
    }
    if any(value < 1 for value in guardrails.values()):
        raise DomainRequestError("guardrails must be positive integers.")
    return {
        "contract": PUBLIC_DOMAIN_CONTRACT,
        "problem": {**deepcopy(dict(problem)), "candidates": prepared, "candidate_id_field": str(candidate_id_field)},
        "delivery": {
            "format": delivery_format,
            "framework": str(framework),
            "mode": str(mode).strip().lower(),
            "logical_optimization": deepcopy(logical_optimization),
        },
        "guardrails": guardrails,
        "evidence": {"shots": int(shots)},
        "metadata": deepcopy(dict(metadata or {})),
    }


def _object_list(values: Sequence[Mapping[str, Any]], name: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for index, value in enumerate(values):
        if not isinstance(value, Mapping):
            raise DomainRequestError(f"{name}[{index}] must be a JSON object.")
        result.append(deepcopy(dict(value)))
    return result


__all__ = [
    "PUBLIC_DOMAIN_CONTRACT",
    "DomainRequestError",
    "const",
    "field",
    "predicate_request",
    "score_request",
]
