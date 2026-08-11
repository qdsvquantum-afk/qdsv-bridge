from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence


class PredicateSpecError(ValueError):
    """Raised when a public bounded-predicate specification is malformed."""


_NARY_BOOLEAN_OPERATIONS = frozenset({"and", "or", "xor"})


def _normalize_expression(node: Any, *, dataset_id: str, row_variable: str) -> Any:
    if not isinstance(node, Mapping):
        return deepcopy(node)

    payload = dict(node)
    operation = str(payload.get("op") or "").strip()
    if not operation:
        raise PredicateSpecError("Every predicate node must declare a non-empty 'op'.")

    if operation == "const":
        if "value" not in payload:
            raise PredicateSpecError("A const node must declare 'value'.")
        return deepcopy(payload["value"])

    if operation == "field":
        field_name = str(payload.get("name") or payload.get("column") or "").strip()
        if not field_name:
            raise PredicateSpecError("A field node must declare 'name' or 'column'.")
        return {
            "op": "field",
            "dataset": dataset_id,
            "row": {"var": row_variable},
            "column": field_name,
        }

    if "args" in payload:
        raw_args = payload["args"]
        if not isinstance(raw_args, list):
            raise PredicateSpecError(f"Operation {operation!r} requires 'args' to be a list.")
    elif "arg" in payload:
        raw_args = [payload["arg"]]
    else:
        raw_args = [payload[key] for key in ("left", "right") if key in payload]
        if "upper" in payload:
            raw_args.append(payload["upper"])
        elif "max" in payload and operation in {"between", "outside"}:
            raw_args.append(payload["max"])

    if not raw_args:
        raise PredicateSpecError(f"Operation {operation!r} must declare operands.")

    args = [
        _normalize_expression(arg, dataset_id=dataset_id, row_variable=row_variable)
        for arg in raw_args
    ]
    if operation in _NARY_BOOLEAN_OPERATIONS:
        if len(args) < 2:
            raise PredicateSpecError(f"Boolean operation {operation!r} requires at least two operands.")
        result: Any = {"op": operation, "args": args[:2]}
        for arg in args[2:]:
            result = {"op": operation, "args": [result, arg]}
        return result

    return {"op": operation, "args": args}


def build_predicate_spec(
    *,
    rows: Sequence[Mapping[str, Any]],
    predicate: Mapping[str, Any],
    candidate_id_field: str = "candidate_index",
    dataset_id: str = "input_0",
    row_variable: str = "x",
    artifact_format: str = "qasm2",
    backend_family: str = "qiskit",
    shots: int = 1024,
    materialization_mode: str = "superposition_oracle",
    max_qubits: int = 256,
    max_depth: int = 1_000_000,
    logical_optimization: bool | Mapping[str, Any] = True,
) -> dict[str, Any]:
    """Build a canonical Bridge spec for a bounded public predicate.

    Candidate identifiers are derived only from stable row order. The helper
    translates the declared expression; it does not evaluate the predicate or
    add expected answers.
    """

    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        raise PredicateSpecError("rows must be a non-empty sequence of mappings.")
    if not isinstance(predicate, Mapping):
        raise PredicateSpecError("predicate must be a mapping.")
    if not str(candidate_id_field).strip():
        raise PredicateSpecError("candidate_id_field must be non-empty.")
    if not str(dataset_id).strip() or not str(row_variable).strip():
        raise PredicateSpecError("dataset_id and row_variable must be non-empty.")
    if int(shots) < 1 or int(max_qubits) < 1 or int(max_depth) < 1:
        raise PredicateSpecError("shots, max_qubits and max_depth must be positive integers.")
    if not isinstance(logical_optimization, (bool, Mapping)):
        raise PredicateSpecError("logical_optimization must be a boolean or a mapping.")

    normalized_rows: list[dict[str, Any]] = []
    for index, raw_row in enumerate(rows):
        if not isinstance(raw_row, Mapping):
            raise PredicateSpecError(f"rows[{index}] must be a mapping.")
        row = deepcopy(dict(raw_row))
        existing_id = row.get(candidate_id_field)
        if existing_id is not None and existing_id != index:
            raise PredicateSpecError(
                f"rows[{index}].{candidate_id_field} must equal its stable row index {index}."
            )
        row[candidate_id_field] = index
        normalized_rows.append(row)

    normalized_predicate = _normalize_expression(
        predicate,
        dataset_id=str(dataset_id),
        row_variable=str(row_variable),
    )
    if not isinstance(normalized_predicate, dict):
        raise PredicateSpecError("The predicate root must be an operation.")
    normalized_predicate["execution_strategy"] = "semantic_auto"

    return {
        "problem_spec": {
            "target": "quantum_hardware",
            "domain": {
                "variable": str(row_variable),
                "type": "int_range",
                "start": 0,
                "end": len(normalized_rows) - 1,
            },
            "data_binding": {
                "kind": "data_binding.v1",
                "default_dataset": str(dataset_id),
                "datasets": [
                    {
                        "id": str(dataset_id),
                        "row_variable": str(row_variable),
                        "index_field": str(candidate_id_field),
                        "rows": normalized_rows,
                    }
                ],
            },
            "predicate": normalized_predicate,
            "query": {"kind": "find_any"},
            "evidence": {"shots": int(shots)},
        },
        "target": {
            "format": str(artifact_format),
            "backend_family": str(backend_family),
            "logical_optimization": deepcopy(logical_optimization),
        },
        "limits": {
            "max_qubits": int(max_qubits),
            "max_depth": int(max_depth),
        },
        "materialization_policy": {
            "mode": str(materialization_mode),
            "shots": int(shots),
        },
    }


__all__ = ["PredicateSpecError", "build_predicate_spec"]
