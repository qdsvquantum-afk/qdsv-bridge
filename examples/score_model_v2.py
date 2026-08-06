"""Generate a small multi-criteria ScoreModel circuit with Bridge."""

from __future__ import annotations

from qdsv_bridge import QDSVBridgeClient


def build_spec() -> dict:
    """Return a public ScoreModel specification without compiler internals."""

    return {
        "state_space": {
            "kind": "finite_candidates",
            "candidate_count": 2,
            "candidate_id": "application",
        },
        "signals": ["readiness", "reliability"],
        # These are prepared input metrics, not decisions or expected answers.
        "prepared_candidates": [
            {"readiness": 800, "reliability": 900},
            {"readiness": 400, "reliability": 500},
        ],
        "goal": {
            "kind": "marking",
            # Prepared metrics and the cutoff use the same declared 0..1000 scale.
            "threshold": 700,
            "criteria": [
                {"signal": "readiness", "importance": 2, "priority": 1},
                {"signal": "reliability", "importance": 1, "priority": 1},
            ],
        },
        "target": {"format": "qasm3", "backend_family": "qiskit"},
        "limits": {"max_qubits": 16, "max_depth": 1_000},
    }


def main() -> None:
    client = QDSVBridgeClient()
    result = client.generate(build_spec())
    package = result["circuit_realization_package"]

    print("status:", result["status"])
    print("artifact format:", result["artifact"]["format"])
    print("canonical identity:", package["canonical_identity"])
    print("result contract:", package["contracts"]["result"])
    print("measurement contract:", package["contracts"]["measurement"])
    print("target handoff:", result["target_handoff"])
    print(result["artifact"]["content"])


if __name__ == "__main__":
    main()
