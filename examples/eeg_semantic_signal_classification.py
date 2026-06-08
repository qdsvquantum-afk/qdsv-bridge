import os

from qdsv_bridge import QDSVBridgeClient


spec = {
    "family": "semantic_signal_classification",
    "state_space": {"kind": "finite_candidates", "candidate_count": 300, "candidate_id": "eeg_window"},
    "signals": [
        "dwt_cD3_std_score",
        "std_score",
        "activity_score",
        "energy_score",
        "dwt_cD2_std_score",
        "complexity_score",
    ],
    "goal": {"kind": "binary_marking", "positive_state": "ictal"},
    "materialization_policy": {
        "preserve_signal_geometry": True,
        "avoid_fixed_ansatz": True,
        "avoid_forced_dimensionality_reduction": True,
        "report_information_loss": True,
    },
    "target": {"format": "qasm3", "backend_family": "qiskit"},
    "limits": {"max_qubits": 10, "max_depth": 300},
}


client = QDSVBridgeClient(api_key=os.getenv("QDSV_BRIDGE_API_KEY") or "YOUR_QDSV_API_KEY")
result = client.build(spec)

print(result["status"])
print(result["bridge_mode"])
print(result["circuit"])
print(result["semantic_preservation_report"])
print(result["artifact"]["content"])
