"""Black-box QDSV Bridge 0.7.0 conformance runner.

This runner intentionally depends only on the published HTTP contract, the
public fixtures in this directory and Qiskit/Aer.  It does not import QDSV
modules, inspect a deployment, or require a compiler implementation checkout.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import qiskit
from qiskit import QuantumCircuit, qasm2, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
import qiskit_aer
import requests


REPORT_SCHEMA = "qdsv_bridge_conformance_report.v0.7"
DIGEST_PREFIX = "sha256:"
SHA256_LENGTH = 64
TOLERANCE = 1e-9
FORBIDDEN_RESPONSE_KEYS = frozenset(
    {
        "problem_spec",
        "oracle_spec",
        "materialization_plan",
        "semantic_preservation_report",
        "operation_compiler",
        "selected_lowering_rule",
        "rejected_lowering_rules",
        "candidate_constructions",
        "optimization_search_path",
        "internal_cost_function",
        "rule_identifier",
        "compiler_stack_trace",
        "canonical_materializer",
        "reversible_plan_optimizer",
        "qintent_capability_registry",
        "specialized_operation_program",
    }
)
FORBIDDEN_ERROR_TERMS = (
    "lowering",
    "materialization",
    "optimizer",
    "compiler stack",
    "internal module",
    "semantic ir",
)
COMPILE_FIELDS = {
    "status",
    "product",
    "contract",
    "request_digest",
    "readiness",
    "resources",
    "digests",
    "warnings",
    "limits",
}
EXPORT_FIELDS = {
    "status",
    "contract",
    "artifact",
    "verification",
    "resources",
    "digests",
    "warnings",
    "limits",
}
REPORT_FIELDS = {
    "status",
    "contract_version",
    "sdk_version",
    "request_digest",
    "artifact_digest",
    "compiler_build_digest",
    "verification",
    "resources",
    "warnings",
    "limits",
}
RESOURCE_FIELDS = {
    "logical_qubits",
    "logical_depth",
    "logical_size",
    "one_qubit_operations",
    "two_qubit_operations",
    "multi_qubit_operations",
    "qasm_bytes",
    "qasm3_bytes",
    "qpy_bytes",
}


class ConformanceError(AssertionError):
    """A public contract or observable behaviour did not conform."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError("Expected a JSON object in {}".format(path))
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_bytes(value: bytes) -> str:
    return DIGEST_PREFIX + hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ConformanceError(message)


def require_exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        raise ConformanceError(
            "{} keys differ; missing={}, unexpected={}".format(
                label,
                sorted(expected - actual),
                sorted(actual - expected),
            )
        )


def assert_no_private_keys(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            name = str(key)
            if name in FORBIDDEN_RESPONSE_KEYS:
                raise ConformanceError("private response key at {}.{}".format(path, name))
            assert_no_private_keys(child, "{}.{}".format(path, name))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_no_private_keys(child, "{}[{}]".format(path, index))


def assert_digest(value: Any, label: str) -> str:
    require(isinstance(value, str), "{} is not a string".format(label))
    require(value.startswith(DIGEST_PREFIX), "{} has no sha256 prefix".format(label))
    raw = value[len(DIGEST_PREFIX) :]
    require(len(raw) == SHA256_LENGTH and all(char in "0123456789abcdef" for char in raw), "{} is not a lowercase SHA-256 digest".format(label))
    return value


def public_projection(value: Any) -> Any:
    """Keep evidence compact without storing public circuit source unnecessarily."""

    if isinstance(value, Mapping):
        projected: dict[str, Any] = {}
        for key, child in value.items():
            if key == "content" and isinstance(child, str):
                projected[key] = {"sha256": sha256_bytes(child.encode("utf-8")), "bytes": len(child.encode("utf-8"))}
            else:
                projected[str(key)] = public_projection(child)
        return projected
    if isinstance(value, list):
        return [public_projection(item) for item in value]
    return value


class PublicBridgeApi:
    """Deliberately minimal HTTP client; it has no dependency on qdsv_bridge."""

    def __init__(self, base_url: str, timeout: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def post(self, path: str, body: Mapping[str, Any]) -> tuple[int, Any]:
        response = requests.post(
            self.base_url + path,
            json=dict(body),
            headers={"Content-Type": "application/json"},
            timeout=self.timeout,
        )
        try:
            payload: Any = response.json()
        except ValueError as exc:
            raise ConformanceError("{} returned non-JSON content".format(path)) from exc
        return response.status_code, payload


def artifact_layout(circuit: QuantumCircuit) -> tuple[list[int], list[int], list[int]]:
    registers = {
        register.name: [circuit.find_bit(qubit).index for qubit in register]
        for register in circuit.qregs
    }
    input_name = "qdsv_input" if "qdsv_input" in registers else "candidate"
    result_name = "qdsv_result" if "qdsv_result" in registers else "decision"
    require(input_name in registers, "QASM artifact has no public input register")
    require(result_name in registers, "QASM artifact has no public result register")
    input_qubits = registers[input_name]
    result_qubits = registers[result_name]
    require(len(result_qubits) == 1, "QASM artifact must have exactly one public decision qubit")
    work_qubits = [
        index
        for name, indices in registers.items()
        if name not in {input_name, result_name}
        for index in indices
    ]
    return input_qubits, result_qubits, work_qubits


def observable_core(circuit: QuantumCircuit, input_qubits: list[int]) -> QuantumCircuit:
    """Remove public preparation/measurement to test the observable Boolean map."""

    core = QuantumCircuit(circuit.num_qubits)
    prepared: set[int] = set()
    touched: set[int] = set()
    input_set = set(input_qubits)
    for instruction in circuit.data:
        operation = instruction.operation
        indices = [circuit.find_bit(qubit).index for qubit in instruction.qubits]
        if operation.name in {"measure", "barrier"}:
            continue
        if (
            operation.name == "h"
            and len(indices) == 1
            and indices[0] in input_set
            and indices[0] not in touched
        ):
            prepared.add(indices[0])
            continue
        touched.update(indices)
        core.append(operation, [core.qubits[index] for index in indices])
    require(prepared == input_set, "QASM artifact does not expose standard input superposition preparation")
    return core


def bit(value: int, index: int) -> int:
    return (value >> index) & 1


def exercise_qiskit_artifact(qasm: str, expected: Mapping[str, Any]) -> dict[str, Any]:
    circuit = qasm2.loads(qasm)
    backend = AerSimulator()
    transpiled = transpile(circuit, backend)
    input_qubits, result_qubits, work_qubits = artifact_layout(circuit)
    core = observable_core(circuit, input_qubits)
    expected_decisions = expected["decisions"]
    candidate_count = len(expected_decisions)
    full_domain = 1 << len(input_qubits)
    require(candidate_count <= full_domain, "fixture exceeds representable input domain")

    observed: list[int] = []
    for candidate in range(full_domain):
        pure = QuantumCircuit(circuit.num_qubits)
        measured = QuantumCircuit(circuit.num_qubits, 1)
        for input_bit, qubit in enumerate(input_qubits):
            if bit(candidate, input_bit):
                pure.x(qubit)
                measured.x(qubit)
        pure.compose(core, inplace=True)
        measured.compose(core, inplace=True)
        measured.measure(result_qubits[0], 0)

        state = Statevector.from_instruction(pure)
        input_probability = 0.0
        clean_work_probability = 0.0
        decision_probability = [0.0, 0.0]
        for basis, amplitude in enumerate(state.data):
            probability = float(abs(amplitude) ** 2)
            if probability < TOLERANCE:
                continue
            input_matches = all(bit(basis, qubit) == bit(candidate, input_bit) for input_bit, qubit in enumerate(input_qubits))
            work_is_clean = all(bit(basis, qubit) == 0 for qubit in work_qubits)
            if input_matches:
                input_probability += probability
            if work_is_clean:
                clean_work_probability += probability
            decision_probability[bit(basis, result_qubits[0])] += probability
        require(abs(input_probability - 1.0) < TOLERANCE, "input register changed for candidate {}".format(candidate))
        require(abs(clean_work_probability - 1.0) < TOLERANCE, "work register not clean for candidate {}".format(candidate))

        expected_bit = expected_decisions[candidate] if candidate < candidate_count else expected["inactive_state_decision"]
        require(abs(decision_probability[expected_bit] - 1.0) < TOLERANCE, "statevector function mismatch for candidate {}".format(candidate))
        counts = backend.run(transpile(measured, backend), shots=128).result().get_counts()
        observed_bit = 1 if counts.get("1", 0) == 128 else 0 if counts.get("0", 0) == 128 else -1
        require(observed_bit == expected_bit, "Aer function mismatch for candidate {}: {}".format(candidate, counts))
        observed.append(observed_bit)
    return {
        "qiskit_version": qiskit.__version__,
        "qiskit_aer_version": qiskit_aer.__version__,
        "qasm_qubits": circuit.num_qubits,
        "qasm_depth": circuit.depth(),
        "transpiled_depth": transpiled.depth(),
        "observed_decisions_including_inactive_states": observed,
    }


def assert_public_error(payload: Any, label: str) -> None:
    require(isinstance(payload, Mapping), "{} error is not a JSON object".format(label))
    require_exact_keys(payload, {"detail"}, label)
    detail = payload["detail"]
    require(isinstance(detail, Mapping), "{} detail is not an object".format(label))
    require_exact_keys(detail, {"error_code", "message", "detail"}, label + ".detail")
    require(str(detail["error_code"]).startswith("E_BRIDGE_"), "{} error code is not public Bridge code".format(label))
    require(isinstance(detail["detail"], Mapping), "{} nested detail is not an object".format(label))
    message = str(detail["message"]).lower()
    require(not any(term in message for term in FORBIDDEN_ERROR_TERMS), "{} error message reveals implementation detail".format(label))
    assert_no_private_keys(payload)


def evaluate_positive_case(api: PublicBridgeApi, case: Mapping[str, Any], expected: Mapping[str, Any]) -> dict[str, Any]:
    spec = case["spec"]
    status, compiled = api.post("/bridge/compile", {"spec": spec})
    require(status == 200 and isinstance(compiled, Mapping), "compile did not return 200")
    require_exact_keys(compiled, COMPILE_FIELDS, "compile")
    require(compiled["contract"] == "qdsv_bridge_public.v1", "compile response contract differs")
    require(compiled["status"] == "COMPILED", "compile status differs")
    require_exact_keys(compiled["digests"], {"request_digest", "compiler_build_digest"}, "compile.digests")
    assert_no_private_keys(compiled)

    status, exported = api.post("/bridge/export", {"spec": spec})
    require(status == 200 and isinstance(exported, Mapping), "export did not return 200")
    require_exact_keys(exported, EXPORT_FIELDS, "export")
    require(exported["contract"] == "qdsv_bridge_public.v1", "export response contract differs")
    require(exported["status"] == "SUCCESS", "export status differs")
    require_exact_keys(exported["digests"], {"request_digest", "artifact_digest", "compiler_build_digest"}, "export.digests")
    require_exact_keys(exported["artifact"], {"format", "language", "content", "materialization_status"}, "export.artifact")
    require(exported["artifact"]["format"] == "qasm2", "fixture did not receive qasm2")
    qasm = exported["artifact"]["content"]
    require(isinstance(qasm, str) and qasm.startswith("OPENQASM 2.0"), "export did not include OpenQASM 2")
    require_exact_keys(exported["verification"], {"status", "circuit_materialized", "artifact_verified"}, "export.verification")
    require(exported["verification"]["status"] == "passed", "artifact verification did not pass")
    require(exported["verification"]["artifact_verified"] is True, "artifact verification is not true")
    require(set(exported["resources"]).issubset(RESOURCE_FIELDS), "export resources contain a non-public field")
    assert_no_private_keys(exported)

    request_digest = assert_digest(exported["digests"]["request_digest"], "request_digest")
    artifact_digest = assert_digest(exported["digests"]["artifact_digest"], "artifact_digest")
    compiler_build_digest = assert_digest(exported["digests"]["compiler_build_digest"], "compiler_build_digest")
    require(request_digest == compiled["request_digest"] == compiled["digests"]["request_digest"], "compile/export request digest mismatch")
    require(compiler_build_digest == compiled["digests"]["compiler_build_digest"], "compile/export build digest mismatch")
    require(artifact_digest == sha256_bytes(qasm.encode("utf-8")), "artifact digest does not bind delivered QASM")

    status, repeat = api.post("/bridge/export", {"spec": spec})
    require(status == 200 and isinstance(repeat, Mapping), "repeat export did not return 200")
    for key in ("request_digest", "artifact_digest", "compiler_build_digest"):
        require(repeat["digests"][key] == exported["digests"][key], "repeat export changed {}".format(key))
    require(repeat["artifact"]["content"] == qasm, "repeat export changed QASM content")

    status, report = api.post("/bridge/report", {"spec": spec, "format": "json"})
    require(status == 200 and isinstance(report, Mapping), "report did not return 200")
    require_exact_keys(report, REPORT_FIELDS | {"format", "content_type", "content", "report"}, "report")
    require_exact_keys(report["report"], REPORT_FIELDS, "report.document")
    require(report["content"] == report["report"], "JSON report content differs from report document")
    require(report["sdk_version"] == "0.7.0", "report SDK version differs")
    require("artifact" not in report["report"] and "trace" not in report["report"], "report exposes an artifact or trace")
    assert_no_private_keys(report)

    qiskit_result = exercise_qiskit_artifact(qasm, expected)
    return {
        "case_id": case["case_id"],
        "request_digest": request_digest,
        "artifact_digest": artifact_digest,
        "compiler_build_digest": compiler_build_digest,
        "compile": public_projection(compiled),
        "export": public_projection(exported),
        "report": public_projection(report),
        "qiskit": qiskit_result,
    }


def negative_specs(public_cases: list[Mapping[str, Any]]) -> list[tuple[str, dict[str, Any]]]:
    base = json.loads(json.dumps(public_cases[0]["spec"]))
    malformed = json.loads(json.dumps(base))
    malformed["problem"]["candidates"] = []
    unsupported = json.loads(json.dumps(base))
    unsupported["problem"]["rule"] = {"op": "unregistered_public_operation", "args": [{"op": "field", "name": "value"}]}
    resource = json.loads(json.dumps(base))
    resource["guardrails"] = {"max_qubits": 1}
    return [("malformed_request", malformed), ("unsupported_input", unsupported), ("resource_exceeded", resource)]


def evaluate_negative_cases(api: PublicBridgeApi, public_cases: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for case_id, spec in negative_specs(public_cases):
        status, payload = api.post("/bridge/export", {"spec": spec})
        require(status == 400, "{} expected HTTP 400, got {}".format(case_id, status))
        assert_public_error(payload, case_id)
        results.append({"case_id": case_id, "http_status": status, "response": public_projection(payload)})
    return results


def make_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# QDSV Bridge 0.7.0 Conformance",
        "",
        "Run: `{}`".format(report["run_id"]),
        "Target: `{}`".format(report["target"]["api_url"]),
        "",
        "| Category | Result |",
        "| --- | --- |",
    ]
    for key, value in report["summary"].items():
        lines.append("| {} | {} |".format(key, value))
    lines.extend(["", "| Check | Status |", "| --- | --- |"])
    for check in report["checks"]:
        lines.append("| {} | {} |".format(check["check_id"], check["status"]))
    lines.extend(
        [
            "",
            "The runner used only public HTTP responses, public fixtures and Qiskit/Aer. "
            "It did not import, inspect or distribute private compiler implementation material.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", required=True, help="Public API base URL ending in /api")
    parser.add_argument("--output", type=Path, required=True, help="Directory for generated public evidence")
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()

    boundary = load_json(root / "spec" / "public-boundary.json")
    inputs = load_json(root / "fixtures" / "public_inputs.json")
    expected = load_json(root / "fixtures" / "expected_outputs.json")
    public_cases = inputs.get("cases")
    require(isinstance(public_cases, list) and public_cases, "public fixtures are missing cases")
    expected_cases = expected.get("cases")
    require(isinstance(expected_cases, Mapping), "expected fixtures are missing cases")

    api = PublicBridgeApi(args.api_url, args.timeout)
    checks: list[dict[str, Any]] = []
    for case in public_cases:
        case_id = str(case["case_id"])
        try:
            detail = evaluate_positive_case(api, case, expected_cases[case_id])
            checks.append({"check_id": case_id, "category": "positive_public_qiskit", "status": "PASS", "detail": detail})
        except Exception as exc:  # report all failed cases, then return non-zero
            checks.append({"check_id": case_id, "category": "positive_public_qiskit", "status": "FAIL", "error": str(exc)})

    try:
        negatives = evaluate_negative_cases(api, public_cases)
        checks.append({"check_id": "negative_public_errors", "category": "negative", "status": "PASS", "detail": negatives})
    except Exception as exc:
        checks.append({"check_id": "negative_public_errors", "category": "negative", "status": "FAIL", "error": str(exc)})

    checks.extend(
        [
            {
                "check_id": "production_timeout_path",
                "category": "negative",
                "status": "NOT_EVALUATED",
                "reason": "The frozen public API has no deterministic public switch for inducing a real service timeout.",
            },
            {
                "check_id": "production_service_failure_path",
                "category": "negative",
                "status": "NOT_EVALUATED",
                "reason": "The frozen public API has no deterministic public switch for inducing an internal 5xx response.",
            },
        ]
    )

    positive_details = [check["detail"] for check in checks if check["status"] == "PASS" and check["category"] == "positive_public_qiskit"]
    try:
        build_digests = {detail["compiler_build_digest"] for detail in positive_details}
        request_digests = {detail["request_digest"] for detail in positive_details}
        require(len(build_digests) == 1, "compiler build digest changed across nearby public requests")
        require(len(request_digests) == len(positive_details), "distinct public requests share request digests")
        checks.append({"check_id": "cross_case_reproducibility", "category": "integrity", "status": "PASS", "detail": {"compiler_build_digest": next(iter(build_digests)), "cases": len(positive_details)}})
    except Exception as exc:
        checks.append({"check_id": "cross_case_reproducibility", "category": "integrity", "status": "FAIL", "error": str(exc)})

    pass_count = sum(check["status"] == "PASS" for check in checks)
    fail_count = sum(check["status"] == "FAIL" for check in checks)
    not_evaluated_count = sum(check["status"] == "NOT_EVALUATED" for check in checks)
    report = {
        "schema_version": REPORT_SCHEMA,
        "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_bridge_070",
        "created_at_utc": utc_now(),
        "target": {"api_url": api.base_url, "authentication_present": False, "private_compiler_access": False},
        "boundary": boundary,
        "runner": {"python": sys.version.split()[0], "qiskit": qiskit.__version__, "qiskit_aer": qiskit_aer.__version__},
        "summary": {"pass": pass_count, "fail": fail_count, "not_evaluated": not_evaluated_count},
        "checks": checks,
        "limitations": [
            "The API has no public deterministic switch for inducing a real service timeout or an internal 5xx response; those two production-fault conditions are intentionally not claimed as evaluated.",
            "This validates bounded fixture behaviour and portable QASM interoperability. It does not claim hardware execution, scalability beyond fixture limits, or independent third-party validation.",
        ],
    }
    output = args.output.resolve()
    write_json(output / "conformance_report.json", report)
    (output / "REPORT.md").write_text(make_markdown(report), encoding="utf-8")
    manifest = {
        "schema_version": "qdsv_bridge_conformance_manifest.v0.7",
        "created_at_utc": report["created_at_utc"],
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "boundary_sha256": sha256_file(root / "spec" / "public-boundary.json"),
        "public_inputs_sha256": sha256_file(root / "fixtures" / "public_inputs.json"),
        "expected_outputs_sha256": sha256_file(root / "fixtures" / "expected_outputs.json"),
        "report_sha256": sha256_file(output / "conformance_report.json"),
        "private_compiler_access": False,
        "expected_answers_sent_to_bridge": False,
    }
    write_json(output / "run_manifest.json", manifest)
    print(output)
    return 1 if fail_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
