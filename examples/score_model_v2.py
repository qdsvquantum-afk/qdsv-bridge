"""Request a bounded ScoreModel v2 circuit from the canonical QDSV path."""

from qdsv_bridge import QDSVBridgeClient


def field(name: str) -> dict:
    return {
        "op": "field",
        "dataset": "input_0",
        "row": {"var": "x"},
        "column": name,
    }


value = field("value")
problem_spec = {
    "target": "quantum_hardware",
    "domain": {"variable": "x", "type": "int_range", "start": 0, "end": 1},
    "data_binding": {
        "kind": "data_binding.v1",
        "datasets": [
            {
                "id": "input_0",
                "row_variable": "x",
                "index_field": "candidate_index",
                "rows": [
                    {"candidate_index": 0, "value": 0},
                    {"candidate_index": 1, "value": 1},
                ],
            }
        ],
    },
    "model": {
        "kind": "score_model",
        "version": "2.0",
        "numeric_contract": {
            "output_scale": 2,
            "max_function_states": 8,
            "max_input_qubits": 2,
        },
        "score": {
            "terms": [
                {
                    "name": "bounded_value",
                    "value": {"op": "squared_diff", "left": value, "right": 0},
                    "importance": 1,
                    "priority": 1,
                    "adjustments": [
                        {"name": "context", "lambda": 0.5, "value": value}
                    ],
                }
            ],
            "penalty": 0,
            "epsilon": 0.001,
            "decision": "gte",
            "threshold": 1,
            "execution_strategy": "semantic_auto",
        },
    },
    "query": {"kind": "find_any"},
    "evidence": {"shots": 1024},
}

spec = {
    "problem_spec": problem_spec,
    "target": {"format": "qasm2", "backend_family": "qiskit"},
    "limits": {"max_qubits": 256, "max_depth": 1_000_000},
    "materialization_policy": {"mode": "superposition_oracle", "shots": 1024},
}

result = QDSVBridgeClient().build(spec)
evidence = result["materialization_evidence"]

print(result["artifact"]["format"])
print(result["circuit"]["status"])
print(evidence["materializer"])
print(evidence["formula_variant"])
print(evidence["actual_qubits"], evidence["actual_depth"])
print(evidence["candidate_precomputed"])
