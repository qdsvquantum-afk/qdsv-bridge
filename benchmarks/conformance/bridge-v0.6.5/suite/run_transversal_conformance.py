from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Callable, Mapping

import jsonschema
import requests


SCHEMA_VERSION = "qdsv_transversal_conformance_report.v0.1"
COMPILER_V2 = "qdsv_operation_compiler.v2"
OPERATION_PROGRAM_V2 = "qdsv_operation_program_public.v2"
CAPABILITY_STATES = {
    "compiler_v2_ready",
    "compile_only",
    "specialized_runtime",
    "not_materialized",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def check(
    check_id: str,
    surface: str,
    evidence_level: str,
    assertions: Mapping[str, Any],
    *,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    passed = all(value is True for value in assertions.values())
    return {
        "check_id": check_id,
        "surface": surface,
        "conformance_status": "PASS" if passed else "FAIL",
        "evidence_level": evidence_level,
        "assertions": dict(assertions),
        "notes": list(notes or []),
    }


def not_evaluated(check_id: str, surface: str, reason: str) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "surface": surface,
        "conformance_status": "NOT_EVALUATED",
        "evidence_level": "CONTRACTUAL",
        "assertions": {},
        "reason": reason,
    }


def is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"(?:sha256:)?[0-9a-fA-F]{64}", value) is not None


def operation_program_assertions(program: Any) -> dict[str, bool]:
    if not isinstance(program, Mapping):
        return {
            "operation_program_present": False,
            "compiler_authority_v2": False,
            "answer_precomputed_false": False,
            "program_digest_present": False,
            "no_classical_answer_substitution": False,
            "quantum_program_ready": False,
        }
    contracts = program.get("contracts") if isinstance(program.get("contracts"), Mapping) else {}
    return {
        "operation_program_present": program.get("contract") == OPERATION_PROGRAM_V2,
        "compiler_authority_v2": program.get("compiler_version") == COMPILER_V2,
        "answer_precomputed_false": program.get("answer_precomputed") is False,
        "program_digest_present": is_sha256(program.get("program_digest")),
        "no_classical_answer_substitution": contracts.get("no_classical_answer_substitution") is True,
        "quantum_program_ready": program.get("quantum_program_ready") is True,
    }


class PublicApi:
    def __init__(self, base_url: str, raw_dir: Path, timeout: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.raw_dir = raw_dir
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "qdsv-conformance-transversal/0.1"})

    def call(
        self,
        name: str,
        method: str,
        path: str,
        payload: Mapping[str, Any] | None = None,
        expected_status: int = 200,
    ) -> tuple[int, Any]:
        response = self.session.request(
            method,
            f"{self.base_url}{path}",
            json=payload,
            timeout=self.timeout,
        )
        try:
            data = response.json()
        except ValueError:
            data = {"text": response.text[:2000]}
        write_json(
            self.raw_dir / f"{name}.json",
            {
                "request": {
                    "method": method,
                    "path": path,
                    "authentication_present": False,
                    "payload_sha256": sha256_bytes(
                        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
                    )
                    if payload is not None
                    else None,
                },
                "response": {"status_code": response.status_code, "body": data},
            },
        )
        if response.status_code != expected_status:
            raise AssertionError(
                f"{method} {path}: expected HTTP {expected_status}, got {response.status_code}: {data}"
            )
        return response.status_code, data


def selected_indices(payload: Mapping[str, Any]) -> list[int]:
    result = payload.get("result") if isinstance(payload.get("result"), Mapping) else {}
    direct = result.get("selected_indices")
    if isinstance(direct, list):
        return sorted(int(value) for value in direct)
    rows = result.get("selected_rows")
    if isinstance(rows, list):
        values = []
        for row in rows:
            if isinstance(row, Mapping) and isinstance(row.get("candidate_index"), int):
                values.append(int(row["candidate_index"]))
        return sorted(values)
    enriched = result.get("rows_enriched")
    if isinstance(enriched, list):
        return sorted(
            int(row["candidate_index"])
            for row in enriched
            if isinstance(row, Mapping)
            and row.get("_qdsv_selected") is True
            and isinstance(row.get("candidate_index"), int)
        )
    return []


def source_assertions(platform_root: Path) -> tuple[list[dict[str, Any]], dict[str, str]]:
    files = {
        "qintent_client": platform_root / "sdk" / "python" / "qdsv-qintent" / "src" / "qintent" / "client.py",
        "runtime_client": platform_root / "sdk" / "python" / "qdsv-runtime" / "src" / "qdsv_runtime" / "runtime.py",
        "qruba_api_client": platform_root / "qdsv" / "frontend" / "src" / "api" / "client.ts",
        "qruba_executor": platform_root / "qdsv" / "frontend" / "src" / "runtime" / "productWorkflowExecutor.ts",
        "qruba_console": platform_root / "qdsv" / "frontend" / "src" / "components" / "terminal" / "ProductTerminal.tsx",
        "specialized_program": platform_root / "qdsv" / "runtime" / "specialized_operation_program.py",
        "physical_runtime": platform_root / "qdsv" / "runtime" / "physical_property_runtime.py",
        "api_product": platform_root / "qdsv" / "api" / "product.py",
    }
    missing = [name for name, path in files.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing transversal source files: {missing}")
    text = {name: path.read_text(encoding="utf-8") for name, path in files.items()}
    hashes = {name: sha256_file(path) for name, path in files.items()}
    checks = [
        check(
            "qintent_sdk_fail_closed",
            "QIntent SDK",
            "STATIC_SOURCE",
            {
                "checks_answer_precomputed": 'program.get("answer_precomputed") is True' in text["qintent_client"],
                "uses_compile_endpoint": "/qintent/compile" in text["qintent_client"],
                "uses_execute_endpoint": "/qintent/execute" in text["qintent_client"],
            },
        ),
        check(
            "runtime_sdk_uses_canonical_endpoints",
            "QDSV Runtime SDK",
            "STATIC_SOURCE",
            {
                "uses_runtime_compile": "/runtime/compile" in text["runtime_client"],
                "uses_runtime_compile_intent": "/runtime/compile-intent" in text["runtime_client"],
                "does_not_use_deprecated_hardware_submit": "/product/hardware/submit" not in text["runtime_client"],
            },
        ),
        check(
            "qruba_canonical_problem_routes",
            "Qruba frontend",
            "STATIC_SOURCE",
            {
                "problem_compile_route": "/product/problem/compile" in text["qruba_api_client"],
                "problem_execute_route": "/product/problem/execute" in text["qruba_api_client"],
                "qintent_compile_route": "/qintent/compile" in text["qruba_api_client"],
                "qintent_execute_route": "/qintent/execute" in text["qruba_api_client"],
                "deprecated_direct_hardware_submit_absent": "/product/hardware/submit" not in text["qruba_api_client"],
            },
        ),
        check(
            "qruba_decision_model_v2",
            "Qruba Decision Model node",
            "STATIC_SOURCE",
            {
                "builds_score_model_problem": 'kind: "score_model"' in text["qruba_executor"],
                "declares_score_model_v2": 'version: "2.0"' in text["qruba_executor"],
                "calls_problem_compile": "productAPI.problemCompile" in text["qruba_executor"],
                "calls_problem_execute": "productAPI.problemExecute" in text["qruba_executor"],
                "local_score_labeled_boundary_review": "computeLocalBoundaryReviewScore" in text["qruba_executor"]
                and "authoritative ScoreModel decision exposed by Qruba" in text["qruba_executor"],
            },
            notes=[
                "The local score helper is limited to boundary-review UX; canonical execution is sent as ProblemSpec."
            ],
        ),
        check(
            "qruba_console_canonical_execution",
            "Qruba Console",
            "STATIC_SOURCE",
            {
                "documents_canonical_problem_surface": "/api/product/problem/execute" in text["qruba_console"],
                "deprecated_direct_hardware_submit_absent": "/product/hardware/submit" not in text["qruba_console"],
            },
        ),
        check(
            "specialized_runtime_wrapped_by_operation_program_v2",
            "Specialized physical runtime",
            "STATIC_SOURCE",
            {
                "specialized_builder_present": "build_specialized_operation_program" in text["physical_runtime"],
                "specialized_verifier_present": "verify_specialized_operation_program" in text["physical_runtime"],
                "compiler_v2_contract_present": COMPILER_V2 in text["specialized_program"],
                "answer_precomputed_false": '"answer_precomputed": False' in text["specialized_program"],
                "classical_materialization_labeled": "classical_scientific_materialization" in text["physical_runtime"],
            },
        ),
        check(
            "api_canonical_and_specialized_entrypoints",
            "QDSV API",
            "STATIC_SOURCE",
            {
                "product_problem_compile": '@router.post("/product/problem/compile"' in text["api_product"],
                "product_problem_execute": '@router.post("/product/problem/execute"' in text["api_product"],
                "runtime_compile": '@router.post("/runtime/compile"' in text["api_product"],
                "runtime_compile_intent": '@router.post("/runtime/compile-intent"' in text["api_product"],
                "qintent_compile": '@router.post("/qintent/compile"' in text["api_product"],
                "qintent_execute": '@router.post("/qintent/execute"' in text["api_product"],
            },
        ),
    ]
    return checks, hashes


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", default="https://api.qdsv.cloud/api")
    parser.add_argument("--platform-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=root / "evidence" / "transversal-runs")
    parser.add_argument("--timeout", type=float, default=120.0)
    args = parser.parse_args()

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_transversal_v01"
    output = args.output.resolve() / run_id
    raw_dir = output / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    api = PublicApi(args.api_url, raw_dir, args.timeout)
    checks: list[dict[str, Any]] = []

    _, product_capabilities = api.call("product_capabilities", "GET", "/product/capabilities")
    _, bridge_capabilities = api.call("bridge_capabilities", "GET", "/bridge/capabilities")
    _, qintent_spec = api.call("qintent_spec", "GET", "/qintent/spec")
    _, qintent_capabilities = api.call("qintent_capabilities", "GET", "/qintent/capabilities")

    family = qintent_capabilities.get("family_materialization", {})
    family_states = family.get("families", {}) if isinstance(family, Mapping) else {}
    checks.append(
        check(
            "public_capability_contracts",
            "Public APIs",
            "DYNAMIC_CONTRACT",
            {
                "product_compiler_v2": product_capabilities.get("compiler") == COMPILER_V2,
                "bridge_compiler_v2": bridge_capabilities.get("operation_capabilities", {}).get("version") == COMPILER_V2,
                "bridge_contract_v2": bridge_capabilities.get("contract") == "qdsv_bridge_operation_compiler.v2",
                "qintent_compiler_v2": qintent_capabilities.get("compiler") == COMPILER_V2,
                "family_states_complete": set(family_states.values()).issubset(CAPABILITY_STATES)
                and set(family_states.values()) == CAPABILITY_STATES,
                "qintent_fail_closed": family.get("fallback_policy") == "fail_closed_without_classical_substitution",
            },
        )
    )

    rows = [
        {"candidate_index": 0, "score": 900},
        {"candidate_index": 1, "score": 650},
        {"candidate_index": 2, "score": 800},
        {"candidate_index": 3, "score": 400},
    ]
    source = 'find_rows("candidate_index").where("score", ">=", 700)'
    qintent_request = {
        "source": source,
        "rows": rows,
        "target": "simulator",
        "backend": "quest",
        "shots": 256,
    }
    _, qintent_compile = api.call("qintent_compile", "POST", "/qintent/compile", qintent_request)
    runtime_request = {key: value for key, value in qintent_request.items() if key != "target"}
    _, runtime_compile = api.call(
        "runtime_compile_intent",
        "POST",
        "/runtime/compile-intent",
        runtime_request,
    )
    _, qintent_execute = api.call("qintent_execute", "POST", "/qintent/execute", qintent_request)

    q_program = qintent_compile.get("operation_program")
    runtime_program = runtime_compile.get("operation_program")
    execute_program = qintent_execute.get("operation_program")
    assertions = operation_program_assertions(q_program)
    assertions.update(
        {
            "qintent_family_compiler_v2_ready": qintent_compile.get("family_capability", {}).get("state")
            == "compiler_v2_ready",
            "runtime_same_program_digest": isinstance(q_program, Mapping)
            and isinstance(runtime_program, Mapping)
            and q_program.get("program_digest") == runtime_program.get("program_digest"),
            "execution_same_program_digest": isinstance(q_program, Mapping)
            and isinstance(execute_program, Mapping)
            and q_program.get("program_digest") == execute_program.get("program_digest"),
            "backend_explicit_quest": qintent_execute.get("backend") == "quest",
            "execution_class_quantum": qintent_execute.get("execution_class") == "quantum_simulation",
            "quantum_execution_true": qintent_execute.get("quantum_execution") is True,
            "not_classical_reference_path": "reference" not in str(qintent_execute.get("execution_path") or "").lower(),
            "independent_business_result": selected_indices(qintent_execute) == [0, 2],
        }
    )
    checks.append(
        check(
            "qintent_runtime_execution_identity",
            "QIntent + Runtime + QuEST",
            "DYNAMIC_SIMULATION",
            assertions,
            notes=["Expected indices were computed locally and were not sent to QDSV."],
        )
    )

    # Qruba/product endpoints are intentionally private. Anonymous access must fail closed.
    product_probe = {
        "target": "simulator",
        "backend": "quest",
        "domain": {"variable": "x", "type": "int_range", "start": 0, "end": 3},
        "model": {"kind": "score_model", "version": "2.0"},
        "query": {"kind": "find_all"},
    }
    status, _ = api.call(
        "product_problem_compile_anonymous_boundary",
        "POST",
        "/product/problem/compile",
        product_probe,
        expected_status=401,
    )
    checks.append(
        check(
            "qruba_private_route_auth_boundary",
            "Qruba private API",
            "DYNAMIC_CONTRACT",
            {
                "anonymous_request_rejected": status == 401,
                "no_anonymous_fallback": status != 200,
            },
            notes=["A licensed interactive Qruba session is required for end-to-end private-node execution."],
        )
    )

    static_checks, source_hashes = source_assertions(args.platform_root.resolve())
    checks.extend(static_checks)

    capability_matrix = [
        {"surface": "Bridge SDK/API", "state": "compiler_v2_ready", "execution_policy": "materialize_only", "evidence": "dynamic_exact_conformance"},
        {"surface": "QIntent with bound rows", "state": "compiler_v2_ready", "execution_policy": "verified_program_and_realizer", "evidence": "dynamic_compile_and_quest_execution"},
        {"surface": "QIntent without bound rows", "state": "compile_only", "execution_policy": "execution_blocked", "evidence": "public_capability_contract"},
        {"surface": "Qruba Decision Model", "state": "compiler_v2_ready", "execution_policy": "private_authenticated_problem_spec", "evidence": "static_source_plus_fail_closed_boundary"},
        {"surface": "QDSV Runtime SDK", "state": "compiler_v2_ready", "execution_policy": "canonical_runtime_endpoints", "evidence": "static_source_and_dynamic_runtime_compile"},
        {"surface": "Physical properties", "state": "specialized_runtime", "execution_policy": "registered_specialized_realizer", "evidence": "static_source_plus_public_capability_contract"},
        {"surface": "AI semantic operation", "state": "compile_only", "execution_policy": "execution_blocked_without_realizer", "evidence": "public_capability_contract"},
        {"surface": "Unknown family", "state": "not_materialized", "execution_policy": "fail_closed", "evidence": "public_capability_contract"},
    ]

    counts = Counter(item["conformance_status"] for item in checks)
    omissions = [
        {
            "scope": "Qruba licensed interactive execution",
            "status": "NOT_EVALUATED",
            "reason": "The clean-room runner has no user license or session token; anonymous access was correctly rejected.",
        },
        {
            "scope": "IBM hardware handoff",
            "status": "NOT_EVALUATED",
            "reason": "No hardware job is submitted by transversal conformance; historical hardware evidence remains a separate track.",
        },
        {
            "scope": "Independent external organization",
            "status": "NOT_EVALUATED",
            "reason": "This run is an owner-side clean-room reproduction, not third-party validation.",
        },
    ]
    report = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_at_utc": utc_now(),
        "target": {
            "api_url": api.base_url,
            "authentication_present": False,
            "platform_root_recorded": str(args.platform_root.resolve()),
        },
        "summary": {
            "pass": counts["PASS"],
            "fail": counts["FAIL"],
            "not_evaluated": counts["NOT_EVALUATED"],
        },
        "contract_identity": {
            "compiler": COMPILER_V2,
            "bridge_contract": bridge_capabilities.get("contract"),
            "contract_bundle_digest": bridge_capabilities.get("operation_capabilities", {}).get("contract_bundle_digest"),
            "qintent_contract": qintent_spec.get("contract"),
        },
        "source_hashes": source_hashes,
        "capability_matrix": capability_matrix,
        "checks": checks,
        "omissions": omissions,
    }
    schema = json.loads((root / "schema" / "transversal-report.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(report, schema)
    write_json(output / "transversal_report.json", report)

    lines = [
        "# QDSV Transversal Conformance Report",
        "",
        f"Run: `{run_id}`",
        f"Target: `{api.base_url}`",
        "",
        f"- PASS: {counts['PASS']}",
        f"- FAIL: {counts['FAIL']}",
        f"- NOT_EVALUATED checks: {counts['NOT_EVALUATED']}",
        "",
        "| Surface | State | Execution policy | Evidence |",
        "|---|---|---|---|",
    ]
    for item in capability_matrix:
        lines.append(
            f"| {item['surface']} | {item['state']} | {item['execution_policy']} | {item['evidence']} |"
        )
    lines.extend(["", "## Checks", "", "| Check | Surface | Status | Evidence |", "|---|---|---|---|"])
    for item in checks:
        lines.append(
            f"| {item['check_id']} | {item['surface']} | {item['conformance_status']} | {item['evidence_level']} |"
        )
    lines.extend(["", "## Explicit omissions", "", "| Scope | Status | Reason |", "|---|---|---|"])
    for item in omissions:
        lines.append(f"| {item['scope']} | {item['status']} | {item['reason']} |")
    (output / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    output_hashes = {
        path.relative_to(output).as_posix(): sha256_file(path)
        for path in sorted(output.rglob("*"))
        if path.is_file()
    }
    manifest = {
        "schema_version": "qdsv_transversal_run_manifest.v0.1",
        "run_id": run_id,
        "created_at_utc": report["created_at_utc"],
        "target": report["target"],
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "schema_sha256": sha256_file(root / "schema" / "transversal-report.schema.json"),
        "outputs": output_hashes,
        "secrets_recorded": False,
        "expected_answers_sent_to_qdsv": False,
    }
    write_json(output / "run_manifest.json", manifest)
    print(output)
    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
