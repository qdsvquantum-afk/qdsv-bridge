from __future__ import annotations

import os

import pytest

from qdsv_bridge import QDSVBridge, QDSVBridgeClient, const, field, predicate_request


pytestmark = pytest.mark.live_bridge
qiskit = pytest.importorskip("qiskit")


@pytest.mark.parametrize("artifact_format", ["qasm2", "qasm3"])
def test_live_service_artifact_is_verified_then_loads_in_qiskit(artifact_format: str) -> None:
    api_url = os.getenv("QDSV_BRIDGE_INTEGRATION_URL")
    if not api_url:
        pytest.skip("Set QDSV_BRIDGE_INTEGRATION_URL to run the live public-adapter check.")

    request = predicate_request(
        candidates=[{"candidate_id": "eligible", "value": 4}, {"candidate_id": "ineligible", "value": 3}],
        rule={"op": "eq", "left": field("value"), "right": const(4)},
        format=artifact_format,
    )
    bridge = QDSVBridge(QDSVBridgeClient(api_url=api_url, max_retries=0))
    artifact = bridge.export(request)
    circuit = artifact.to_quantum_circuit()

    assert artifact.format == artifact_format
    assert circuit.num_qubits >= 1
    assert artifact.artifact_digest.startswith("sha256:")
