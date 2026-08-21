from __future__ import annotations

from copy import deepcopy
import math
from typing import Any, Mapping, Sequence


class PredicateSpecError(ValueError):
    """Raised when a public bounded-predicate specification is malformed."""


_NARY_BOOLEAN_OPERATIONS = frozenset({"and", "or", "xor"})
_UNARY_OPERATIONS = frozenset(
    {"abs", "ceil", "floor", "is_null", "not", "not_null", "round", "sign"}
)


def _normalized_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    candidate_id_field: str,
) -> list[dict[str, Any]]:
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        raise PredicateSpecError("rows must be a non-empty sequence of mappings.")
    if not str(candidate_id_field).strip():
        raise PredicateSpecError("candidate_id_field must be non-empty.")

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
    return normalized_rows


def _logical_optimization_contract(value: bool | Mapping[str, Any]) -> bool | dict[str, Any]:
    if not isinstance(value, (bool, Mapping)):
        raise PredicateSpecError("logical_optimization must be a boolean or a mapping.")
    return deepcopy(value)


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

    if operation in _UNARY_OPERATIONS:
        declared = [key for key in ("arg", "value", "operand", "args") if key in payload]
        if len(declared) != 1:
            raise PredicateSpecError(
                f"Unary operation {operation!r} requires exactly one of "
                "'arg', 'value', 'operand' or 'args'."
            )
        raw_value = payload[declared[0]]
        if declared[0] == "args":
            if not isinstance(raw_value, list) or len(raw_value) != 1:
                raise PredicateSpecError(
                    f"Unary operation {operation!r} requires exactly one item in 'args'."
                )
            raw_value = raw_value[0]
        return {
            "op": operation,
            "value": _normalize_expression(
                raw_value,
                dataset_id=dataset_id,
                row_variable=row_variable,
            ),
        }

    if operation == "weighted_sum" and ("values" in payload or "weights" in payload):
        values = payload.get("values")
        weights = payload.get("weights")
        if not isinstance(values, list) or not values:
            raise PredicateSpecError("weighted_sum.values must be a non-empty list.")
        if not isinstance(weights, list) or len(weights) != len(values):
            raise PredicateSpecError(
                "weighted_sum.weights must be a list with the same length as values."
            )
        return {
            "op": "weighted_sum",
            "args": [
                {
                    "op": "vector",
                    "args": [
                        _normalize_expression(
                            value,
                            dataset_id=dataset_id,
                            row_variable=row_variable,
                        )
                        for value in values
                    ],
                },
                {"op": "vector", "args": [deepcopy(weight) for weight in weights]},
            ],
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
    add expected answers. ``logical_optimization`` accepts ``True`` for the
    default public contract, ``False`` for canonical-only delivery, or a
    mapping that freezes ``mode``, ``profile`` and ``acceptance_policy``.

    Args:
        rows: Prepared business inputs in stable candidate order.
        predicate: Public predicate expression to normalize without evaluating.
        candidate_id_field: Stable integer identity field added to each row.
        dataset_id: Identifier used by the generated data binding.
        row_variable: Variable name used by the bounded candidate domain.
        artifact_format: Requested Bridge artifact format.
        backend_family: Portable framework family for the logical artifact.
        shots: Evidence request recorded in the specification.
        materialization_mode: Public circuit materialization mode.
        max_qubits: Logical qubit guardrail for materialization.
        max_depth: Logical depth guardrail for materialization.
        logical_optimization: Default, disabled, or explicitly frozen public
            logical-optimization contract.

    Returns:
        A new Bridge specification with copied rows and predicate data.

    Raises:
        PredicateSpecError: If the bounded predicate contract is malformed.
    """

    if not isinstance(predicate, Mapping):
        raise PredicateSpecError("predicate must be a mapping.")
    if not str(dataset_id).strip() or not str(row_variable).strip():
        raise PredicateSpecError("dataset_id and row_variable must be non-empty.")
    if int(shots) < 1 or int(max_qubits) < 1 or int(max_depth) < 1:
        raise PredicateSpecError("shots, max_qubits and max_depth must be positive integers.")
    normalized_rows = _normalized_rows(rows, candidate_id_field=candidate_id_field)

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
            "logical_optimization": _logical_optimization_contract(logical_optimization),
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


def build_score_model_spec(
    *,
    rows: Sequence[Mapping[str, Any]],
    threshold: Any,
    terms: Sequence[Mapping[str, Any]] | None = None,
    blocks: Sequence[Mapping[str, Any]] | None = None,
    decision: str = "gte",
    candidate_id_field: str = "candidate_index",
    dataset_id: str = "input_0",
    row_variable: str = "x",
    output_scale: int = 1000,
    max_function_states: int = 1024,
    max_input_qubits: int | None = None,
    penalty: Any = 0,
    epsilon: Any = "0.000000001",
    artifact_format: str = "qasm2",
    backend_family: str = "qiskit",
    shots: int = 1024,
    materialization_mode: str = "superposition_oracle",
    max_qubits: int = 256,
    max_depth: int = 1_000_000,
    logical_optimization: bool | Mapping[str, Any] = True,
) -> dict[str, Any]:
    """Build an outcome-blind public ScoreModel v2 specification.

    Exactly one of ``terms`` or ``blocks`` must be supplied. Values and
    adjustments are normalized as public semantic expressions; this helper
    does not evaluate scores, decisions or expected answers.
    """

    if (terms is None) == (blocks is None):
        raise PredicateSpecError("Exactly one of terms or blocks must be provided.")
    if str(decision) not in {"eq", "ne", "lt", "lte", "gt", "gte"}:
        raise PredicateSpecError("decision must be one of eq, ne, lt, lte, gt or gte.")
    if int(output_scale) < 1 or int(max_function_states) < 1:
        raise PredicateSpecError("output_scale and max_function_states must be positive integers.")
    if int(shots) < 1 or int(max_qubits) < 1 or int(max_depth) < 1:
        raise PredicateSpecError("shots, max_qubits and max_depth must be positive integers.")
    if not str(dataset_id).strip() or not str(row_variable).strip():
        raise PredicateSpecError("dataset_id and row_variable must be non-empty.")

    normalized_rows = _normalized_rows(rows, candidate_id_field=candidate_id_field)
    resolved_input_qubits = (
        int(max_input_qubits)
        if max_input_qubits is not None
        else max(1, math.ceil(math.log2(max(1, len(normalized_rows)))))
    )
    if resolved_input_qubits < 1:
        raise PredicateSpecError("max_input_qubits must be a positive integer.")

    def normalize_term(raw_term: Mapping[str, Any], *, path: str) -> dict[str, Any]:
        if not isinstance(raw_term, Mapping):
            raise PredicateSpecError(f"{path} must be a mapping.")
        term = deepcopy(dict(raw_term))
        if "value" not in term:
            raise PredicateSpecError(f"{path}.value is required.")
        raw_adjustments = term.get("adjustments", [])
        if not isinstance(raw_adjustments, list):
            raise PredicateSpecError(f"{path}.adjustments must be a list.")
        normalized = {
            "name": str(term.get("name") or path.replace(".", "_")),
            "value": _normalize_expression(
                term["value"], dataset_id=dataset_id, row_variable=row_variable
            ),
            "importance": deepcopy(term.get("importance", term.get("weight", 1))),
            "priority": deepcopy(term.get("priority", term.get("criticality", 1))),
            "adjustments": [],
        }
        for index, raw_adjustment in enumerate(raw_adjustments):
            if not isinstance(raw_adjustment, Mapping):
                raise PredicateSpecError(f"{path}.adjustments[{index}] must be a mapping.")
            adjustment = dict(raw_adjustment)
            if "value" not in adjustment:
                raise PredicateSpecError(f"{path}.adjustments[{index}].value is required.")
            normalized["adjustments"].append(
                {
                    "lambda": deepcopy(adjustment.get("lambda", 1)),
                    "value": _normalize_expression(
                        adjustment["value"],
                        dataset_id=dataset_id,
                        row_variable=row_variable,
                    ),
                }
            )
        return normalized

    score: dict[str, Any] = {
        "decision": str(decision),
        "threshold": deepcopy(threshold),
        "penalty": deepcopy(penalty),
        "epsilon": deepcopy(epsilon),
        "execution_strategy": "semantic_auto",
    }
    if terms is not None:
        if not isinstance(terms, Sequence) or isinstance(terms, (str, bytes)) or not terms:
            raise PredicateSpecError("terms must be a non-empty sequence.")
        score["terms"] = [
            normalize_term(term, path=f"terms[{index}]")
            for index, term in enumerate(terms)
        ]
    else:
        if not isinstance(blocks, Sequence) or isinstance(blocks, (str, bytes)) or not blocks:
            raise PredicateSpecError("blocks must be a non-empty sequence.")
        normalized_blocks: list[dict[str, Any]] = []
        for block_index, raw_block in enumerate(blocks):
            if not isinstance(raw_block, Mapping):
                raise PredicateSpecError(f"blocks[{block_index}] must be a mapping.")
            block = deepcopy(dict(raw_block))
            raw_terms = block.get("terms")
            if not isinstance(raw_terms, Sequence) or isinstance(raw_terms, (str, bytes)) or not raw_terms:
                raise PredicateSpecError(f"blocks[{block_index}].terms must be a non-empty sequence.")
            normalized_blocks.append(
                {
                    "name": str(block.get("name") or f"block_{block_index}"),
                    "terms": [
                        normalize_term(
                            term,
                            path=f"blocks[{block_index}].terms[{term_index}]",
                        )
                        for term_index, term in enumerate(raw_terms)
                    ],
                    "importance": deepcopy(block.get("importance", block.get("weight", 1))),
                    "priority": deepcopy(block.get("priority", block.get("criticality", 1))),
                    "penalty": deepcopy(block.get("penalty", 0)),
                }
            )
        score["blocks"] = normalized_blocks

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
            "model": {
                "kind": "score_model",
                "version": "2.0",
                "numeric_contract": {
                    "output_scale": int(output_scale),
                    "max_function_states": int(max_function_states),
                    "max_input_qubits": resolved_input_qubits,
                },
                "score": score,
            },
            "query": {"kind": "find_any"},
            "evidence": {"shots": int(shots)},
        },
        "target": {
            "format": str(artifact_format),
            "backend_family": str(backend_family),
            "logical_optimization": _logical_optimization_contract(logical_optimization),
        },
        "limits": {"max_qubits": int(max_qubits), "max_depth": int(max_depth)},
        "materialization_policy": {
            "mode": str(materialization_mode),
            "shots": int(shots),
        },
    }


def build_score_expression_spec(
    *,
    rows: Sequence[Mapping[str, Any]],
    expression: Mapping[str, Any],
    threshold: Any,
    decision: str = "gte",
    candidate_id_field: str = "candidate_index",
    dataset_id: str = "input_0",
    row_variable: str = "x",
    output_scale: int = 1000,
    max_function_states: int = 1024,
    max_input_qubits: int | None = None,
    penalty: Any = 0,
    epsilon: Any = "0.000000001",
    artifact_format: str = "qasm2",
    backend_family: str = "qiskit",
    shots: int = 1024,
    materialization_mode: str = "superposition_oracle",
    max_qubits: int = 256,
    max_depth: int = 1_000_000,
    logical_optimization: bool | Mapping[str, Any] = True,
) -> dict[str, Any]:
    """Build a one-expression ScoreModel v2 specification without evaluating it."""

    if not isinstance(expression, Mapping):
        raise PredicateSpecError("expression must be a mapping.")
    return build_score_model_spec(
        rows=rows,
        threshold=threshold,
        terms=[
            {
                "name": "semantic_expression",
                "value": expression,
                "importance": 1,
                "priority": 1,
                "adjustments": [],
            }
        ],
        decision=decision,
        candidate_id_field=candidate_id_field,
        dataset_id=dataset_id,
        row_variable=row_variable,
        output_scale=output_scale,
        max_function_states=max_function_states,
        max_input_qubits=max_input_qubits,
        penalty=penalty,
        epsilon=epsilon,
        artifact_format=artifact_format,
        backend_family=backend_family,
        shots=shots,
        materialization_mode=materialization_mode,
        max_qubits=max_qubits,
        max_depth=max_depth,
        logical_optimization=logical_optimization,
    )


__all__ = [
    "PredicateSpecError",
    "build_predicate_spec",
    "build_score_expression_spec",
    "build_score_model_spec",
]
