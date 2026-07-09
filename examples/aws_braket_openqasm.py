"""QDSV Bridge -> OpenQASM -> Amazon Braket LocalSimulator demo.

This example keeps Braket optional. Install it with:

    pip install amazon-braket-sdk

The demo does not require AWS credentials because it uses the local simulator.
"""

from __future__ import annotations

import os
from pathlib import Path

from qdsv_bridge import QDSVBridgeClient


API_URL = os.getenv("QDSV_BRIDGE_API_URL") or None
API_KEY = os.getenv("QDSV_BRIDGE_API_KEY") or None


def to_braket_openqasm(source: str) -> str:
    """Create a small Braket-compatible OpenQASM view of the Bridge artifact."""

    lines: list[str] = []
    for line in source.splitlines():
        stripped = line.strip()
        if stripped == "OPENQASM 3.0;":
            lines.append("OPENQASM 3;")
        elif stripped == 'include "stdgates.inc";':
            continue
        else:
            lines.append(line)
    return "\n".join(lines) + "\n"


def main() -> None:
    client = QDSVBridgeClient(api_url=API_URL, api_key=API_KEY, timeout=60)

    spec = {
        "family": "bounded_semantic_marking",
        "bridge_mode": "build",
        "state_space": {
            "kind": "finite_candidates",
            "candidate_count": 8,
            "candidate_id": "candidate",
        },
        "signals": ["eligibility_score", "risk_score"],
        "goal": {
            "kind": "marking",
            "predicate": "eligible_candidate",
        },
        "target": {
            "format": "qasm3",
            "backend_family": "braket",
        },
        "limits": {
            "max_qubits": 5,
            "max_depth": 160,
        },
    }

    artifact_package = client.build(spec)
    qasm3_source = artifact_package["artifact"]["content"]
    braket_qasm = to_braket_openqasm(qasm3_source)

    Path("bridge_aws_braket_artifact.qasm").write_text(qasm3_source, encoding="utf-8")
    Path("bridge_aws_braket_compatible.qasm").write_text(braket_qasm, encoding="utf-8")

    try:
        from braket.devices import LocalSimulator
        from braket.ir.openqasm import Program
    except Exception as exc:  # pragma: no cover - optional dependency path
        raise SystemExit(
            "Amazon Braket SDK is required for simulation. Install it with "
            "`pip install amazon-braket-sdk` and use a supported Python version."
        ) from exc

    program = Program(source=braket_qasm)
    result = LocalSimulator().run(program, shots=1024).result()
    print("Counts:")
    print(dict(result.measurement_counts))

    report = client.report(spec, mode="build", format="markdown")
    Path("bridge_report_aws_braket_demo.md").write_text(report["content"], encoding="utf-8")
    print("Saved: bridge_aws_braket_artifact.qasm")
    print("Saved: bridge_aws_braket_compatible.qasm")
    print("Saved: bridge_report_aws_braket_demo.md")


if __name__ == "__main__":
    main()
