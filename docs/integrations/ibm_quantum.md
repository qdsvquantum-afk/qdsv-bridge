# QDSV Bridge for IBM/Qiskit Workflows

Status: public developer preview.

QDSV Bridge is a problem-first specification layer for quantum-oriented workflows. It helps users declare a controlled semantic problem specification before exporting inspectable artifacts for circuit ecosystems such as Qiskit.

Bridge does not replace Qiskit. It prepares QASM/Qiskit-oriented artifacts, preservation metadata and reproducibility reports that Qiskit users can inspect, modify, simulate or route toward IBM Quantum workflows when appropriate.

## Current Public Flow

```text
problem intent
-> controlled semantic specification
-> Bridge validation/build
-> QASM3 or Qiskit-oriented artifact
-> Qiskit inspection or local simulation
-> Bridge Report
```

## Quick Start

Install the public SDK:

```bash
pip install qdsv-bridge
```

Minimal build flow:

```python
from qdsv_bridge import QDSVBridgeClient

client = QDSVBridgeClient()

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
        "backend_family": "qiskit",
    },
    "limits": {
        "max_qubits": 5,
        "max_depth": 160,
    },
}

artifact_package = client.build(spec)
qasm3_source = artifact_package["artifact"]["content"]

print(qasm3_source)
print(artifact_package["semantic_preservation"])
print(artifact_package["digests"])
```

Load the artifact into Qiskit when the current Qiskit environment supports the generated OpenQASM 3 features:

```python
from qiskit import qasm3

circuit = qasm3.loads(qasm3_source)
print(circuit)
```

Generate a shareable report:

```python
report = client.report(spec, mode="build", format="markdown")
print(report["content"])
```

## Colab Demo

Use the IBM/Qiskit demo notebook for a complete public walkthrough:

[Open 04 IBM/Qiskit Artifact Demo](https://colab.research.google.com/github/qdsvquantum-afk/qdsv-bridge/blob/main/notebooks/04_ibm_qiskit_bridge_demo.ipynb)

The notebook demonstrates:

- installing `qdsv-bridge` from PyPI;
- connecting to the public Bridge API;
- declaring a bounded semantic problem specification;
- building a QASM3 artifact for a Qiskit-oriented target;
- loading the artifact with Qiskit when supported;
- simulating locally with Qiskit Aer;
- generating a Bridge Report.

## Boundaries

Bridge is not an IBM Quantum hardware execution SDK. It does not expose the private QDSV Runtime, backend-routing heuristics, production adapters or private lowering internals.

The current public role of Bridge is upstream of execution:

```text
preserve problem intent
-> derive an auditable artifact
-> provide metadata and warnings
-> let the Qiskit user inspect and control the circuit workflow
```

## Why This Helps Qiskit Users

Many quantum workflows start directly from gates, encodings, ansatz choices or backend details. Bridge starts from a controlled semantic specification and then exports artifacts for circuit ecosystems.

For Qiskit users, the practical benefit is not loss of control. The benefit is traceability before circuit construction:

- what problem was declared;
- what state-space role was used;
- what artifact was generated;
- what semantic preservation evidence was reported;
- what warnings or limits should be inspected before execution.

## Public Links

- QDSV Bridge PyPI: <https://pypi.org/project/qdsv-bridge/>
- QDSV Bridge GitHub: <https://github.com/qdsvquantum-afk/qdsv-bridge>
- QDSV project overview: <https://qdsv.cloud/>
