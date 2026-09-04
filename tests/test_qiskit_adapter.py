from __future__ import annotations

from hashlib import sha256
from io import BytesIO

import pytest

from qdsv_bridge import QDSVBridgeArtifact


qiskit = pytest.importorskip("qiskit")


def _response(source: str, artifact_format: str) -> dict:
    return {
        "contract": "qdsv_bridge_public.v1",
        "status": "SUCCESS",
        "artifact": {
            "format": artifact_format,
            "language": f"open{artifact_format}",
            "content": source,
            "materialization_status": "complete",
        },
        "digests": {
            "request_digest": "sha256:" + "a" * 64,
            "artifact_digest": "sha256:" + sha256(source.encode("utf-8")).hexdigest(),
            "compiler_build_digest": "sha256:" + "b" * 64,
        },
        "verification": {"status": "passed", "circuit_materialized": None, "artifact_verified": True},
        "resources": {"logical_qubits": 1},
        "warnings": [],
    }


def test_verified_qasm2_artifact_loads_transpiles_executes_and_round_trips_qpy() -> None:
    from qiskit import qpy, transpile
    from qiskit_aer import AerSimulator

    source = '''OPENQASM 2.0;
include "qelib1.inc";
qreg q[1];
creg c[1];
x q[0];
measure q[0] -> c[0];
'''
    circuit = QDSVBridgeArtifact.from_public_response(_response(source, "qasm2")).to_quantum_circuit()
    backend = AerSimulator()
    transpiled = transpile(circuit, backend)
    counts = backend.run(transpiled, shots=32).result().get_counts()
    buffer = BytesIO()
    qpy.dump(circuit, buffer)
    buffer.seek(0)
    restored = qpy.load(buffer)[0]

    assert counts == {"1": 32}
    assert restored == circuit


def test_verified_qasm3_artifact_loads_into_quantum_circuit() -> None:
    source = '''OPENQASM 3.0;
include "stdgates.inc";
bit[1] c;
qubit[1] q;
x q[0];
c[0] = measure q[0];
'''
    circuit = QDSVBridgeArtifact.from_public_response(_response(source, "qasm3")).to_quantum_circuit()

    assert circuit.num_qubits == 1
    assert circuit.num_clbits == 1
    assert circuit.data[0].operation.name == "x"
