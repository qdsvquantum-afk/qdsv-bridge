from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import re
import sys
import traceback
from typing import Any, Mapping

import numpy as np
import jsonschema
from qiskit import QuantumCircuit, qasm2
from qiskit.circuit.library import HGate
from qiskit.quantum_info import Operator, Statevector

import qdsv_bridge
from qdsv_bridge import (
    PredicateSpecError,
    QDSVBridgeClient,
    QDSVBridgeHTTPError,
    build_predicate_spec,
    build_score_expression_spec,
    build_score_model_spec,
)


SCHEMA_VERSION = "qdsv_bridge_conformance_report.v0.1"
MANIFEST_VERSION = "qdsv_conformance_run_manifest.v0.1"
TOLERANCE = 1e-9
FORBIDDEN_REQUEST_KEYS = {
    "answer",
    "answers",
    "expected",
    "expected_answer",
    "expected_answers",
    "ground_truth",
    "label",
    "labels",
    "predicate_result",
    "winner",
    "winners",
}
DIGEST_KEYS = (
    "problem_spec_digest",
    "ir_digest",
    "oracle_digest",
    "materialization_digest",
    "canonical_qasm_digest",
    "artifact_digest",
    "recommended_artifact_digest",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_bridge_conformance_v01_sdk065"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected JSON object: {path}")
    return value


def find_forbidden_keys(value: Any, path: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if str(key).lower() in FORBIDDEN_REQUEST_KEYS:
                found.append(child_path)
            found.extend(find_forbidden_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(find_forbidden_keys(child, f"{path}[{index}]"))
    return found


def find_values_by_key(value: Any, key: str) -> list[Any]:
    found: list[Any] = []
    if isinstance(value, Mapping):
        for name, child in value.items():
            if name == key:
                found.append(child)
            found.extend(find_values_by_key(child, key))
    elif isinstance(value, list):
        for child in value:
            found.extend(find_values_by_key(child, key))
    return found


def find_first_mapping_by_key(value: Any, key: str) -> dict[str, Any] | None:
    if isinstance(value, Mapping):
        child = value.get(key)
        if isinstance(child, Mapping):
            return dict(child)
        for nested in value.values():
            found = find_first_mapping_by_key(nested, key)
            if found is not None:
                return found
    elif isinstance(value, list):
        for nested in value:
            found = find_first_mapping_by_key(nested, key)
            if found is not None:
                return found
    return None


def error_code(payload: Any) -> str:
    if isinstance(payload, Mapping):
        for key in ("error_code", "code"):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value
        for child in payload.values():
            found = error_code(child)
            if found:
                return found
    elif isinstance(payload, list):
        for child in payload:
            found = error_code(child)
            if found:
                return found
    return ""


def classify_http_error(exc: QDSVBridgeHTTPError) -> str:
    code = error_code(exc.payload).upper()
    text = json.dumps(exc.payload, sort_keys=True, default=str).upper()
    combined = f"{code} {text}"
    if any(token in combined for token in ("RESOURCE", "SIZE_LIMIT", "MAX_QUBIT", "MAX_DEPTH", "ARTIFACT_SIZE")):
        return "RESOURCE_LIMITED"
    if any(token in combined for token in ("UNSUPPORTED", "NOT_IMPLEMENTED", "MISSING_CAPABILIT")):
        return "UNSUPPORTED"
    if any(token in combined for token in ("INVALID_SPEC", "VALIDATION", "MALFORMED", "UNKNOWN_OPERATION", "OPERATION_COMPILER_REJECTED")):
        return "INVALID_SPEC"
    return "CONTRACT_FAIL"


def build_spec(case: Mapping[str, Any]) -> dict[str, Any]:
    kind = case["kind"]
    common = {
        "rows": case["rows"],
        "artifact_format": "qasm2",
        "shots": 1024,
        "max_qubits": int(case.get("max_qubits", 256)),
        "max_depth": int(case.get("max_depth", 1_000_000)),
        "logical_optimization": True,
    }
    if kind in {"predicate", "invalid_spec", "unsupported", "resource_guardrail"}:
        return build_predicate_spec(predicate=case["predicate"], **common)
    if kind == "score_expression":
        return build_score_expression_spec(
            expression=case["expression"],
            threshold=case["threshold"],
            decision=case.get("decision", "gte"),
            output_scale=int(case.get("output_scale", 1000)),
            max_function_states=int(case.get("max_function_states", 1024)),
            **common,
        )
    if kind == "score_model":
        return build_score_model_spec(
            threshold=case["threshold"],
            decision=case.get("decision", "gte"),
            blocks=case["blocks"],
            output_scale=int(case.get("output_scale", 1000)),
            max_function_states=int(case.get("max_function_states", 1024)),
            **common,
        )
    raise ValueError(f"Unknown case kind: {kind}")


def qreg_map(circuit: QuantumCircuit) -> dict[str, list[int]]:
    return {
        register.name: [circuit.find_bit(qubit).index for qubit in register]
        for register in circuit.qregs
    }


def resolve_layout(circuit: QuantumCircuit) -> dict[str, Any]:
    registers = qreg_map(circuit)
    if {"candidate", "decision"}.issubset(registers):
        input_name, result_name = "candidate", "decision"
    elif {"qdsv_input", "qdsv_result"}.issubset(registers):
        input_name, result_name = "qdsv_input", "qdsv_result"
    else:
        raise AssertionError(f"No public input/result register pair in {sorted(registers)}")
    work_names = [name for name in registers if name not in {input_name, result_name}]
    return {
        "input_register": input_name,
        "result_register": result_name,
        "work_registers": work_names,
        "input_qubits": registers[input_name],
        "result_qubits": registers[result_name],
        "work_qubits": [qubit for name in work_names for qubit in registers[name]],
        "all_registers": registers,
    }


def canonical_oracle_core(circuit: QuantumCircuit, input_qubits: list[int]) -> QuantumCircuit:
    input_set = set(input_qubits)
    removed_preparation: set[int] = set()
    touched: set[int] = set()
    core = QuantumCircuit(circuit.num_qubits)
    for instruction in circuit.data:
        operation = instruction.operation
        if operation.name in {"measure", "barrier"}:
            continue
        indices = [circuit.find_bit(qubit).index for qubit in instruction.qubits]
        is_hadamard = False
        if len(indices) == 1:
            try:
                is_hadamard = Operator(operation).equiv(Operator(HGate()))
            except Exception:
                is_hadamard = operation.name == "h"
        if is_hadamard:
            qubit = indices[0]
            if qubit in input_set and qubit not in touched and qubit not in removed_preparation:
                removed_preparation.add(qubit)
                continue
        touched.update(indices)
        if instruction.clbits:
            raise AssertionError("Classical operation found inside canonical oracle")
        core.append(operation, [core.qubits[index] for index in indices])
    if removed_preparation != input_set:
        raise AssertionError(
            f"Could not identify exact candidate preparation: input={sorted(input_set)}, "
            f"removed={sorted(removed_preparation)}"
        )
    return core


def exact_probabilities(circuit: QuantumCircuit) -> np.ndarray:
    state = Statevector.from_instruction(circuit)
    return np.abs(np.asarray(state.data, dtype=complex)) ** 2


def replay_canonical(
    qasm: str,
    *,
    candidate_count: int,
    expected_decisions: list[int] | None,
) -> dict[str, Any]:
    circuit = qasm2.loads(qasm)
    layout = resolve_layout(circuit)
    input_qubits = layout["input_qubits"]
    result_qubits = layout["result_qubits"]
    work_qubits = layout["work_qubits"]
    if len(result_qubits) != 1:
        raise AssertionError(f"Expected one decision qubit, got {len(result_qubits)}")
    core = canonical_oracle_core(circuit, input_qubits)
    full_domain = 1 << len(input_qubits)
    if candidate_count > full_domain:
        raise AssertionError("Candidate count exceeds encoded input domain")

    rows = []
    for candidate in range(full_domain):
        test = QuantumCircuit(circuit.num_qubits)
        for bit, qubit in enumerate(input_qubits):
            if (candidate >> bit) & 1:
                test.x(qubit)
        test.compose(core, inplace=True)
        probabilities = exact_probabilities(test)
        p_input = 0.0
        p_clean = 0.0
        decision_distribution: dict[int, float] = defaultdict(float)
        for basis, probability in enumerate(probabilities):
            if probability < 1e-14:
                continue
            input_ok = all(
                ((basis >> qubit) & 1) == ((candidate >> bit) & 1)
                for bit, qubit in enumerate(input_qubits)
            )
            work_zero = all(((basis >> qubit) & 1) == 0 for qubit in work_qubits)
            decision = (basis >> result_qubits[0]) & 1
            decision_distribution[decision] += float(probability)
            if input_ok:
                p_input += float(probability)
            if work_zero:
                p_clean += float(probability)
        if abs(p_input - 1.0) >= TOLERANCE:
            raise AssertionError(f"Candidate input not preserved for state {candidate}: {p_input}")
        if abs(p_clean - 1.0) >= TOLERANCE:
            raise AssertionError(f"Work ancillas not clean for state {candidate}: {p_clean}")
        expected = None
        if expected_decisions is not None:
            expected = expected_decisions[candidate] if candidate < candidate_count else 0
            if abs(decision_distribution.get(expected, 0.0) - 1.0) >= TOLERANCE:
                raise AssertionError(
                    f"Decision mismatch for state {candidate}: expected={expected}, "
                    f"observed={dict(decision_distribution)}"
                )
        rows.append(
            {
                "candidate": candidate,
                "valid_candidate": candidate < candidate_count,
                "expected_decision": expected,
                "input_preservation_probability": p_input,
                "clean_ancilla_probability": p_clean,
                "decision_distribution": dict(sorted(decision_distribution.items())),
            }
        )
    return {
        "status": "passed",
        "qubits": circuit.num_qubits,
        "depth": circuit.depth(),
        "operations": sum(circuit.count_ops().values()),
        "layout": layout,
        "basis_states": rows,
    }


def validate_result_contract(result: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
    if result.get("status") != "SUCCESS":
        raise AssertionError(f"Unexpected Bridge status: {result.get('status')}")
    artifact = result.get("artifact")
    if not isinstance(artifact, Mapping) or artifact.get("format") != "qasm2":
        raise AssertionError("Canonical inline qasm2 artifact is required")
    qasm = artifact.get("content")
    if not isinstance(qasm, str) or "OPENQASM" not in qasm:
        raise AssertionError("Canonical OpenQASM content is missing")
    verification = result.get("construction_verification")
    if not isinstance(verification, Mapping) or verification.get("status") != "passed":
        raise AssertionError(f"Construction verification did not pass: {verification}")
    digests = result.get("digests")
    if not isinstance(digests, Mapping):
        raise AssertionError("Digest bundle is missing")
    normalized = {}
    for key in DIGEST_KEYS:
        value = digests.get(key)
        if value is None:
            raise AssertionError(f"Required digest is missing: {key}")
        clean = value[7:] if isinstance(value, str) and value.startswith("sha256:") else value
        if not isinstance(clean, str) or re.fullmatch(r"[0-9a-fA-F]{64}", clean) is None:
            raise AssertionError(f"Invalid SHA-256 digest for {key}: {value}")
        normalized[key] = clean.lower()
    precomputed_values = find_values_by_key(result, "answer_precomputed")
    if any(value is True for value in precomputed_values):
        raise AssertionError("Response declares answer_precomputed=true")
    return qasm, {"digests": normalized, "answer_precomputed_values": precomputed_values}


def contractual_semantic_replay(result: Mapping[str, Any]) -> dict[str, Any]:
    replay = find_first_mapping_by_key(result, "semantic_replay")
    if replay is None:
        raise AssertionError("Bridge semantic_replay bundle is missing")
    canonical = replay.get("canonical")
    if not isinstance(canonical, Mapping):
        raise AssertionError("Canonical semantic replay is missing")
    if canonical.get("status") != "passed" or canonical.get("semantic_equivalence") is not True:
        raise AssertionError(f"Canonical semantic replay failed: {canonical}")
    if canonical.get("mismatch_shots") not in (0, None):
        raise AssertionError(f"Canonical semantic replay has mismatches: {canonical.get('mismatch_shots')}")
    ancilla = canonical.get("ancilla_validation") or {}
    if ancilla.get("status") != "passed":
        raise AssertionError(f"Contractual ancilla validation failed: {ancilla}")
    return replay


def validate_optimized_contract(
    result: Mapping[str, Any],
    *,
    candidate_count: int,
    expected_decisions: list[int],
) -> dict[str, Any]:
    optimized = result.get("optimized_logical_artifact")
    if not isinstance(optimized, Mapping):
        raise AssertionError("Optimized logical artifact is missing")
    if optimized.get("role") != "optimized_logical_artifact" or optimized.get("status") != "accepted":
        raise AssertionError(f"Optimized artifact was not accepted: {optimized.get('status')}")
    content = optimized.get("content")
    if optimized.get("format") != "qasm2" or not isinstance(content, str):
        raise AssertionError("Accepted optimized artifact is not inline qasm2")
    digests = result.get("digests") or {}
    if optimized.get("parent_digest") != digests.get("artifact_digest"):
        raise AssertionError("Optimized parent digest does not link to canonical artifact")
    if result.get("recommended_artifact_role") != "optimized_logical_artifact":
        raise AssertionError("Recommended artifact role is inconsistent with accepted optimization")
    if digests.get("recommended_artifact_digest") != digests.get("optimized_artifact_digest"):
        raise AssertionError("Recommended and optimized artifact digests differ")
    optimization = result.get("logical_optimization")
    if not isinstance(optimization, Mapping) or optimization.get("status") != "accepted":
        raise AssertionError("Logical optimization contract was not accepted")
    if optimization.get("profile") != "qiskit_structural_exact_v1":
        raise AssertionError(f"Unexpected logical optimization profile: {optimization.get('profile')}")
    if optimization.get("acceptance_policy") != "pareto_no_regression_v1":
        raise AssertionError(f"Unexpected acceptance policy: {optimization.get('acceptance_policy')}")
    if optimization.get("approximation") is not False:
        raise AssertionError("Optimized logical artifact used approximation")
    if any(optimization.get(key) not in (None, False) for key in ("backend", "routing", "scheduling")):
        raise AssertionError("Logical optimization unexpectedly used a physical target")
    validation = optimization.get("validation") or {}
    acceptance = optimization.get("acceptance") or {}
    if validation.get("status") != "passed" or validation.get("prepared_state_equivalence") is not True:
        raise AssertionError("Optimized artifact semantic validation did not pass")
    if acceptance.get("status") != "accepted" or acceptance.get("protected_metric_regressions"):
        raise AssertionError("Optimized artifact violated the no-regression contract")
    independent = replay_canonical(
        content,
        candidate_count=candidate_count,
        expected_decisions=expected_decisions,
    )
    return {
        "parent_digest_linked": True,
        "recommended_role_consistent": True,
        "semantic_validation_passed": True,
        "no_regression_policy_passed": True,
        "independent_replay": independent,
    }


def metric_layers(
    *,
    canonical_replay: Mapping[str, Any] | None = None,
    optimized_replay: Mapping[str, Any] | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    logical: dict[str, Any] = {
        "status": "MEASURED" if canonical_replay is not None else "NOT_APPLICABLE",
        "artifact_role": "canonical_ideal_artifact",
    }
    if canonical_replay is not None:
        logical.update(
            {
                "qubits": canonical_replay.get("qubits"),
                "depth": canonical_replay.get("depth"),
                "operations": canonical_replay.get("operations"),
            }
        )
    else:
        logical["reason"] = reason or "no_materialized_artifact"

    optimized: dict[str, Any] = {
        "status": "MEASURED" if optimized_replay is not None else "NOT_APPLICABLE",
        "artifact_role": "optimized_logical_artifact",
    }
    if optimized_replay is not None:
        optimized.update(
            {
                "qubits": optimized_replay.get("qubits"),
                "depth": optimized_replay.get("depth"),
                "operations": optimized_replay.get("operations"),
            }
        )
    else:
        optimized["reason"] = reason or "optimized_profile_not_required_for_case"

    return {
        "semantic": {
            "status": "MEASURED" if canonical_replay is not None else "NOT_APPLICABLE",
            "method": "exact_basis_state_replay" if canonical_replay is not None else None,
            "reason": None if canonical_replay is not None else reason or "no_materialized_artifact",
        },
        "logical": {"canonical": logical, "optimized": optimized},
        "normalized": {
            "status": "NOT_EVALUATED",
            "reason": "common_external_normalization_is_a_separate_benchmark_track",
        },
        "physical": {
            "status": "NOT_APPLICABLE",
            "reason": "bridge_conformance_is_target_independent_and_does_not_submit_hardware",
        },
    }


def case_result(
    case: Mapping[str, Any],
    *,
    status: str,
    outcome: str,
    evidence: str,
    assertions: Mapping[str, Any] | None = None,
    metrics: Mapping[str, Any] | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    value = {
        "case_id": case["case_id"],
        "kind": case["kind"],
        "profiles": list(case.get("profiles", [])),
        "conformance_status": status,
        "outcome": outcome,
        "evidence_level": evidence,
        "assertions": dict(assertions or {}),
        "metrics": dict(metrics or metric_layers(reason="case_did_not_materialize")),
    }
    if error:
        value["error"] = error
    return value


def execute_case(
    client: QDSVBridgeClient,
    case: Mapping[str, Any],
    expected: Mapping[str, Any],
    evidence_dir: Path,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    expected_outcome = expected.get("outcome")
    try:
        spec = build_spec(case)
    except PredicateSpecError as exc:
        outcome = "INVALID_SPEC"
        passed = expected_outcome == outcome
        return (
            case_result(
                case,
                status="PASS" if passed else "FAIL",
                outcome=outcome,
                evidence="CONTRACTUAL",
                assertions={"client_rejected_before_transport": True},
                error=str(exc),
            ),
            None,
        )

    forbidden = find_forbidden_keys(spec)
    if forbidden:
        return (
            case_result(
                case,
                status="FAIL",
                outcome="CONTRACT_FAIL",
                evidence="CONTRACTUAL",
                error=f"Forbidden answer-bearing request keys: {forbidden}",
            ),
            None,
        )
    write_json(evidence_dir / f"{case['case_id']}.request.json", spec)

    try:
        result = client.build(spec)
    except QDSVBridgeHTTPError as exc:
        outcome = classify_http_error(exc)
        write_json(evidence_dir / f"{case['case_id']}.http_error.json", exc.payload)
        passed = expected_outcome == outcome
        return (
            case_result(
                case,
                status="PASS" if passed else "FAIL",
                outcome=outcome,
                evidence="CONTRACTUAL",
                assertions={"http_status": exc.status_code, "error_code": error_code(exc.payload)},
                error=str(exc),
            ),
            None,
        )
    except Exception as exc:
        return (
            case_result(
                case,
                status="NOT_EVALUATED",
                outcome="TRANSPORT_ERROR",
                evidence="CONTRACTUAL",
                error=f"{type(exc).__name__}: {exc}",
            ),
            None,
        )

    write_json(evidence_dir / f"{case['case_id']}.response.json", result)
    if expected_outcome in {"RESOURCE_LIMITED", "UNSUPPORTED", "INVALID_SPEC"}:
        return (
            case_result(
                case,
                status="FAIL",
                outcome="CONTRACT_FAIL",
                evidence="CONTRACTUAL",
                error=f"Expected {expected_outcome}, but the request succeeded",
            ),
            result,
        )

    try:
        qasm, contract = validate_result_contract(result)
        expected_decisions = expected.get("decisions")
        replay = replay_canonical(
            qasm,
            candidate_count=len(case["rows"]),
            expected_decisions=list(expected_decisions) if isinstance(expected_decisions, list) else None,
        )
        contractual = contractual_semantic_replay(result)
        assertions = {
            "request_contains_expected_answers": False,
            "construction_verification": "passed",
            "answer_precomputed_true": False,
            "canonical_replay": replay,
            "contractual_semantic_replay_status": "passed",
            "contract_digest_count": len(contract["digests"]),
        }
        optimized_replay = None
        if "optimized_logical_artifact" in case.get("profiles", []):
            if expected_decisions is None:
                raise AssertionError("Independent expected decisions are required for optimized replay")
            assertions["optimized_logical_artifact"] = validate_optimized_contract(
                result,
                candidate_count=len(case["rows"]),
                expected_decisions=list(expected_decisions),
            )
            optimized_replay = assertions["optimized_logical_artifact"]["independent_replay"]
        evidence_level = "INDEPENDENT_REPLAY" if expected_decisions is not None else "CONTRACTUAL"
        return (
            case_result(
                case,
                status="PASS",
                outcome="SUCCESS",
                evidence=evidence_level,
                assertions=assertions,
                metrics=metric_layers(
                    canonical_replay=replay,
                    optimized_replay=optimized_replay,
                ),
            ),
            result,
        )
    except AssertionError as exc:
        return (
            case_result(
                case,
                status="FAIL",
                outcome="SEMANTIC_FAIL" if "Decision mismatch" in str(exc) else "CONTRACT_FAIL",
                evidence="INDEPENDENT_REPLAY",
                error=str(exc),
            ),
            result,
        )


def determinism_case(
    client: QDSVBridgeClient,
    source_case: Mapping[str, Any],
    evidence_dir: Path,
) -> dict[str, Any]:
    case = {
        "case_id": "deterministic_repeated_build",
        "kind": "determinism",
        "profiles": ["canonical_artifact"],
    }
    try:
        spec = build_spec(source_case)
        builds = [client.build(spec) for _ in range(3)]
        for index, result in enumerate(builds):
            write_json(evidence_dir / f"deterministic_repeated_build.{index + 1}.response.json", result)
        qasms = [validate_result_contract(result)[0] for result in builds]
        digest_sets = [
            {key: result["digests"].get(key) for key in DIGEST_KEYS}
            for result in builds
        ]
        if len(set(qasms)) != 1:
            raise AssertionError("Canonical QASM is not byte-identical across repeated builds")
        if any(value != digest_sets[0] for value in digest_sets[1:]):
            raise AssertionError("Canonical digest bundle changed across repeated builds")
        return case_result(
            case,
            status="PASS",
            outcome="SUCCESS",
            evidence="INDEPENDENT_REPLAY",
            assertions={
                "build_count": 3,
                "byte_identical_qasm": True,
                "stable_digest_bundle": True,
                "canonical_qasm_sha256": sha256_bytes(qasms[0].encode("utf-8")),
            },
            metrics=metric_layers(reason="determinism_case_reuses_source_artifact_metrics"),
        )
    except Exception as exc:
        return case_result(
            case,
            status="FAIL",
            outcome="CONTRACT_FAIL",
            evidence="CONTRACTUAL",
            error=f"{type(exc).__name__}: {exc}",
        )


def package_versions() -> dict[str, str]:
    names = ("qdsv-bridge", "qiskit", "qiskit-aer", "numpy", "requests")
    versions = {}
    for name in names:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "not-installed"
    versions["python"] = sys.version.split()[0]
    return versions


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, default=root / "fixtures" / "public_inputs.json")
    parser.add_argument("--expected", type=Path, default=root / "fixtures" / "expected_outputs.json")
    parser.add_argument("--output", type=Path, default=root / "evidence" / "runs")
    parser.add_argument("--api-url", default=os.environ.get("QDSV_BRIDGE_API_URL"))
    args = parser.parse_args()

    versions = package_versions()
    if versions["qdsv-bridge"] != "0.6.5" or qdsv_bridge.__version__ != "0.6.5":
        raise RuntimeError(
            "The v0.1 contract runner for SDK 0.6.5 requires "
            f"qdsv-bridge 0.6.5, got {versions}"
        )

    inputs = load_json(args.inputs)
    expected_bundle = load_json(args.expected)
    expected_cases = expected_bundle["cases"]
    current_run = run_id()
    output = args.output.resolve() / current_run
    raw_evidence = output / "raw"
    raw_evidence.mkdir(parents=True, exist_ok=True)

    client = QDSVBridgeClient(api_url=args.api_url, timeout=120)
    capabilities = client.capabilities()
    write_json(raw_evidence / "capabilities.json", capabilities)
    preflight_assertions = {
        "status_success": capabilities.get("status") == "SUCCESS",
        "bridge_contract_v2": capabilities.get("contract") == "qdsv_bridge_operation_compiler.v2",
        "compiler_authority_v2": capabilities.get("operation_capabilities", {}).get("version") == "qdsv_operation_compiler.v2",
    }
    if not all(preflight_assertions.values()):
        raise RuntimeError(f"Capability preflight failed: {preflight_assertions}")

    results = []
    source_results: dict[str, dict[str, Any] | None] = {}
    cases = inputs.get("cases", [])
    for case in cases:
        result, raw = execute_case(
            client,
            case,
            expected_cases.get(case["case_id"], {}),
            raw_evidence,
        )
        results.append(result)
        source_results[case["case_id"]] = raw
        print(
            f"{result['conformance_status']:<13} {result['outcome']:<18} "
            f"{result['evidence_level']:<18} {result['case_id']}"
        )

    deterministic_source = next(case for case in cases if case["case_id"] == "compound_predicate_power2")
    deterministic = determinism_case(client, deterministic_source, raw_evidence)
    results.append(deterministic)
    print(
        f"{deterministic['conformance_status']:<13} {deterministic['outcome']:<18} "
        f"{deterministic['evidence_level']:<18} {deterministic['case_id']}"
    )

    counts = Counter(item["conformance_status"] for item in results)
    outcomes = Counter(item["outcome"] for item in results)
    profile_definitions = load_json(root / "spec" / "conformance-profiles-v0.1.json")
    profile_coverage = {}
    for profile in profile_definitions["profiles"]:
        matching = [item for item in results if profile in item.get("profiles", [])]
        if not matching:
            profile_status = "NOT_EVALUATED"
        elif any(item["conformance_status"] == "FAIL" for item in matching):
            profile_status = "FAIL"
        elif any(item["conformance_status"] == "NOT_EVALUATED" for item in matching):
            profile_status = "NOT_EVALUATED"
        else:
            profile_status = "PASS"
        profile_coverage[profile] = {
            "status": profile_status,
            "case_count": len(matching),
            "cases": [item["case_id"] for item in matching],
        }
    omission_reasons = {
        "specialized_runtime": "Bridge logical conformance does not invoke a specialized runtime.",
        "hardware_handoff": "Hardware submission is outside Bridge and requires a separate downstream profile.",
    }
    omissions = [
        {
            "scope": profile,
            "status": coverage["status"],
            "reason": omission_reasons.get(profile, "No applicable frozen case in this suite version."),
        }
        for profile, coverage in profile_coverage.items()
        if coverage["status"] == "NOT_EVALUATED"
    ]
    report = {
        "schema_version": SCHEMA_VERSION,
        "run_id": current_run,
        "created_at_utc": utc_now(),
        "summary": {
            "pass": counts["PASS"],
            "fail": counts["FAIL"],
            "not_evaluated": counts["NOT_EVALUATED"],
            "outcomes": dict(sorted(outcomes.items())),
        },
        "environment": versions,
        "target": {
            "api_url": client.api_url,
            "authentication_present": bool(client.api_key),
            "sdk_name": client.sdk_name,
        },
        "capability_preflight": preflight_assertions,
        "profile_coverage": profile_coverage,
        "metric_layers": {
            "semantic": "Exact independent replay or explicit contractual evidence.",
            "logical": "Target-independent canonical and optimized circuit resources.",
            "normalized": "Common transpilation track; intentionally separate from this suite.",
            "physical": "Backend execution evidence; intentionally separate from Bridge conformance.",
        },
        "omissions": omissions,
        "cases": results,
    }
    write_json(output / "conformance_report.json", report)

    output_hashes = {
        path.relative_to(output).as_posix(): sha256_file(path)
        for path in sorted(output.rglob("*"))
        if path.is_file()
    }
    manifest = {
        "schema_version": MANIFEST_VERSION,
        "run_id": current_run,
        "created_at_utc": report["created_at_utc"],
        "versions": versions,
        "target": report["target"],
        "fixtures": {
            "public_inputs": {"path": str(args.inputs.resolve()), "sha256": sha256_file(args.inputs)},
            "expected_outputs": {"path": str(args.expected.resolve()), "sha256": sha256_file(args.expected)},
            "expected_outputs_sent_to_bridge": False,
        },
        "runner": {
            "path": str(Path(__file__).resolve()),
            "sha256": sha256_file(Path(__file__).resolve()),
            "report_schema_sha256": sha256_file(root / "schema" / "suite-report.schema.json"),
            "manifest_schema_sha256": sha256_file(root / "schema" / "run-manifest.schema.json"),
            "profile_contract_sha256": sha256_file(root / "spec" / "conformance-profiles-v0.1.json"),
            "tolerance": TOLERANCE,
            "random_seed": None,
            "replay_method": "exact_statevector_basis_state_replay",
        },
        "outputs": output_hashes,
        "secrets_recorded": False,
    }
    write_json(output / "run_manifest.json", manifest)

    jsonschema.validate(
        report,
        load_json(root / "schema" / "suite-report.schema.json"),
    )
    jsonschema.validate(
        manifest,
        load_json(root / "schema" / "run-manifest.schema.json"),
    )

    lines = [
        "# QDSV Bridge Conformance Report",
        "",
        f"Run: `{current_run}`",
        f"Target: `{client.api_url}`",
        f"SDK: `{versions['qdsv-bridge']}`",
        "",
        f"- PASS: {counts['PASS']}",
        f"- FAIL: {counts['FAIL']}",
        f"- NOT_EVALUATED: {counts['NOT_EVALUATED']}",
        "",
        "| Case | Conformance | Outcome | Evidence |",
        "|---|---|---|---|",
    ]
    for item in results:
        lines.append(
            f"| {item['case_id']} | {item['conformance_status']} | "
            f"{item['outcome']} | {item['evidence_level']} |"
        )
    lines.extend(["", "## Profile coverage", "", "| Profile | Status | Cases |", "|---|---|---:|"])
    for profile, coverage in profile_coverage.items():
        lines.append(f"| {profile} | {coverage['status']} | {coverage['case_count']} |")
    lines.extend(["", "## Omissions", "", "| Scope | Status | Reason |", "|---|---|---|"])
    for omission in omissions:
        lines.append(f"| {omission['scope']} | {omission['status']} | {omission['reason']} |")
    lines.extend(
        [
            "",
            "Expected outcomes were stored separately and were not sent to Bridge.",
            "Resource and support outcomes are not classified as semantic failures.",
        ]
    )
    (output / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(output)
    return 1 if counts["FAIL"] or counts["NOT_EVALUATED"] else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(2)
