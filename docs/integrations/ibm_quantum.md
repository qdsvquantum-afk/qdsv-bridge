# QDSV Bridge for IBM/Qiskit Workflows

Status: public developer preview.

QDSV Bridge is a problem-first specification layer for quantum-oriented workflows. It helps users declare a controlled semantic problem specification before exporting inspectable artifacts for circuit ecosystems such as Qiskit.

Bridge does not replace Qiskit. It uses canonical QDSV ProblemSpec/IR materialization to prepare executable QASM/Qiskit artifacts, materialization evidence and reproducibility reports.

## Current Public Flow

```text
problem intent
-> controlled semantic specification
-> Bridge validation and canonical QDSV materialization
-> QASM3 or Qiskit-oriented artifact
-> Qiskit inspection or local simulation
-> Bridge Report
```

## Quick Start

Install the public SDK:

```bash
pip install "qdsv-bridge[qiskit]"
```

The optional Qiskit extra is version-capped to the current supported major series
(`qiskit>=2,<3`) to follow Qiskit Ecosystem compatibility guidance.

Minimal build flow:

```python
from qdsv_bridge import QDSVBridgeClient

client = QDSVBridgeClient()

spec = {
    "bridge_mode": "build",
    "state_space": {
        "kind": "finite_candidates",
        "candidate_count": 2,
        "candidate_id": "candidate",
    },
    "signals": ["eligibility_score"],
    "prepared_candidates": [
        {"eligibility_score": 0},
        {"eligibility_score": 1},
    ],
    "goal": {
        "kind": "marking",
        "threshold": 1,
        "criteria": [
            {"signal": "eligibility_score", "importance": 1, "priority": 1}
        ],
    },
    "target": {
        "format": "qasm3",
        "backend_family": "qiskit",
    },
    "limits": {
        "max_qubits": 8,
        "max_depth": 160,
    },
}

artifact_package = client.build(spec)
qasm3_source = artifact_package["artifact"]["content"]

print(qasm3_source)
print(artifact_package["materialization_evidence"])
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

Bridge is not an IBM Quantum hardware execution SDK. It does not expose the private runtime, internal compilation or optimization rules, or private backend adapters.

The current public role of Bridge is upstream of execution:

```text
preserve problem intent
-> construct the formula/oracle through the supported QDSV path
-> derive an executable auditable artifact
-> provide metadata and warnings
-> let the Qiskit user inspect and control the circuit workflow
```

## Why This Helps Qiskit Users

Many quantum workflows start directly from gates, encodings, ansatz choices or backend details. Bridge starts from a controlled semantic specification and then exports artifacts for circuit ecosystems.

For Qiskit users, the practical benefit is not loss of control. The benefit is traceability before circuit construction:

- what problem was declared;
- what state-space role was used;
- what artifact was generated;
- whether the formula was constructed in the circuit;
- whether candidates or result tables were precomputed;
- what warnings or limits should be inspected before execution.

## Public Links

- QDSV Bridge PyPI: <https://pypi.org/project/qdsv-bridge/>
- QDSV Bridge GitHub: <https://github.com/qdsvquantum-afk/qdsv-bridge>
- QDSV project overview: <https://qdsv.cloud/>
