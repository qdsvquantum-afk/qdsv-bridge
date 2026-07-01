# QDSV Bridge for Amazon Braket OpenQASM Workflows

Status: public developer preview.

QDSV Bridge is a problem-first specification layer for quantum-oriented workflows. It helps users declare a controlled semantic problem specification before exporting inspectable OpenQASM artifacts that can be used in Braket-oriented workflows with the Amazon Braket SDK and `LocalSimulator`.

Bridge does not replace Amazon Braket and is not an official Amazon Braket integration. It prepares OpenQASM-oriented artifacts, preservation metadata and reproducibility reports that Braket users can inspect, adapt, simulate locally, or route toward managed Braket workflows when appropriate.

## Current Public Flow

```text
problem intent
-> controlled semantic specification
-> Bridge validation/build
-> OpenQASM 3 artifact
-> Braket-compatible OpenQASM view
-> Amazon Braket LocalSimulator
-> Bridge Report
```

## Quick Start

Install the public SDK and Braket SDK:

```bash
pip install qdsv-bridge amazon-braket-sdk
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
        "backend_family": "braket",
    },
    "limits": {
        "max_qubits": 5,
        "max_depth": 160,
    },
}

artifact_package = client.build(spec)
qasm3_source = artifact_package["artifact"]["content"]
```

Amazon Braket documents OpenQASM examples with the `OPENQASM 3;` header and without `stdgates.inc`. Bridge's current public artifact is intentionally OpenQASM/Qiskit-oriented, so the Braket demo creates a small compatibility view before submitting it to Braket:

```python
def to_braket_openqasm(source: str) -> str:
    lines = []
    for line in source.splitlines():
        stripped = line.strip()
        if stripped == "OPENQASM 3.0;":
            lines.append("OPENQASM 3;")
        elif stripped == 'include "stdgates.inc";':
            continue
        else:
            lines.append(line)
    return "\n".join(lines) + "\n"

braket_qasm = to_braket_openqasm(qasm3_source)
```

Run locally with Braket:

```python
from braket.devices import LocalSimulator
from braket.ir.openqasm import Program

program = Program(source=braket_qasm)
result = LocalSimulator().run(program, shots=1024).result()
print(dict(result.measurement_counts))
```

Generate a shareable report:

```python
report = client.report(spec, mode="build", format="markdown")
print(report["content"])
```

## Colab Demo

Use the AWS Braket demo notebook for a complete public walkthrough:

[Open 05 AWS Braket OpenQASM Demo](https://colab.research.google.com/github/qdsvquantum-afk/qdsv-bridge/blob/main/notebooks/05_aws_braket_openqasm_demo.ipynb)

The notebook demonstrates:

- installing `qdsv-bridge` from PyPI;
- installing the Amazon Braket Python SDK as an optional demo dependency;
- connecting to the public Bridge API;
- declaring a bounded semantic problem specification;
- building an OpenQASM 3 artifact for a Braket-oriented target;
- preparing a small Braket-compatible OpenQASM view;
- simulating locally with `LocalSimulator`;
- generating a Bridge Report.

## Tested Environment

This demo was tested with:

- Python 3.11;
- `qdsv-bridge` 0.1.5;
- Amazon Braket SDK;
- Amazon Braket `LocalSimulator`.

Python 3.14 is not recommended for this demo yet due to dependency compatibility issues observed in the Braket SDK / Pydantic stack.

## Boundaries

Bridge is not an AWS hardware execution SDK. It does not manage AWS accounts, Amazon S3 task locations, Braket QPU access, billing, backend selection, production adapters or private lowering internals.

The current public role of Bridge is upstream of managed execution:

```text
preserve problem intent
-> derive an auditable OpenQASM artifact
-> provide metadata and warnings
-> let the Braket user inspect and control the execution workflow
```

## Why This Helps Braket Users

Amazon Braket supports OpenQASM 3.0 programs for gate-based devices and simulators. Bridge adds an upstream problem-first layer before the OpenQASM program enters the Braket workflow.

For Braket users, the practical benefit is traceability before simulation or task submission:

- what problem was declared;
- what state-space role was used;
- what OpenQASM artifact was generated;
- what semantic preservation evidence was reported;
- what compatibility adjustments were made for Braket;
- what warnings or limits should be inspected before execution.

## Public Links

- QDSV Bridge PyPI: <https://pypi.org/project/qdsv-bridge/>
- QDSV Bridge GitHub: <https://github.com/qdsvquantum-afk/qdsv-bridge>
- QDSV project overview: <https://qdsv.cloud/>
- Amazon Braket OpenQASM documentation: <https://docs.aws.amazon.com/braket/latest/developerguide/braket-openqasm.html>
- Amazon Braket OpenQASM task example: <https://docs.aws.amazon.com/braket/latest/developerguide/braket-openqasm-create-submit-task.html>
