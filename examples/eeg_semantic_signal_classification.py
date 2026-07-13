from qdsv_bridge import QDSVBridgeClient


spec = {
    "family": "semantic_signal_classification",
    "state_space": {"kind": "finite_candidates", "candidate_count": 2, "candidate_id": "eeg_window"},
    "signals": ["ictal_score"],
    "prepared_candidates": [{"ictal_score": 0}, {"ictal_score": 1}],
    "goal": {
        "kind": "binary_marking",
        "positive_state": "ictal",
        "threshold": 1,
        "criteria": [{"signal": "ictal_score", "importance": 1, "priority": 1}],
    },
    "materialization_policy": {
        "preserve_signal_geometry": True,
        "avoid_fixed_ansatz": True,
        "avoid_forced_dimensionality_reduction": True,
        "report_information_loss": True,
    },
    "target": {"format": "qasm3", "backend_family": "qiskit"},
    "limits": {"max_qubits": 8, "max_depth": 160},
}


client = QDSVBridgeClient()
result = client.build(spec)

print(result["status"])
print(result["bridge_mode"])
print(result["circuit"])
print(result["materialization_evidence"])
print(result["artifact"]["content"])
