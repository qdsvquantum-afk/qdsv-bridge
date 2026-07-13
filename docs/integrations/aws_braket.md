# QDSV Bridge for Amazon Braket OpenQASM Workflows

Status: public developer preview.

QDSV Bridge is a problem-first specification layer for quantum-oriented workflows. It helps users declare a controlled semantic problem specification before exporting an OpenQASM artifact compatible with the tested Amazon Braket `LocalSimulator` conversion workflow.

Bridge does not replace Amazon Braket and is not an official Amazon Braket integration. It prepares problem-derived OpenQASM artifacts, construction evidence and reproducibility reports for the tested local conversion workflow.

## Current Public Flow

```text
problem intent
-> controlled semantic specification
-> Bridge validation and canonical QDSV materialization
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
        "backend_family": "braket",
    },
    "limits": {
        "max_qubits": 8,
        "max_depth": 160,
    },
}

artifact_package = client.build(spec)
qasm3_source = artifact_package["artifact"]["content"]
```

Bridge's canonical artifact uses Qiskit's OpenQASM 3 standard-gate include. The Braket demo therefore creates an explicit compatibility view: it removes that include, defines the four gates used by the lowered circuit, and renames Qiskit's `cx` instruction to Braket's `cnot` spelling.

```python
def to_braket_openqasm(source: str) -> str:
    lines = []
    gate_definitions = [
        "gate x a { U(pi, 0, pi) a; }",
        "gate h a { U(pi/2, 0, pi) a; }",
        "gate rz(lambda) a { gphase(-lambda/2); U(0, 0, lambda) a; }",
        "gate cnot a, b { ctrl @ x a, b; }",
    ]
    for line in source.splitlines():
        stripped = line.strip()
        if stripped == "OPENQASM 3.0;":
            lines.append("OPENQASM 3;")
            lines.extend(gate_definitions)
        elif stripped == 'include "stdgates.inc";':
            continue
        elif stripped.startswith("cx "):
            lines.append(line.replace("cx ", "cnot ", 1))
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
- building an OpenQASM 3 artifact for the tested Braket LocalSimulator conversion;
- preparing a small Braket-compatible OpenQASM view;
- simulating locally with `LocalSimulator`;
- generating a Bridge Report.

## Tested Environment

This demo was tested with:

- Python 3.11;
- `qdsv-bridge` 0.4.3;
- Amazon Braket SDK;
- Amazon Braket `LocalSimulator`.

Python 3.14 is not recommended for this demo yet due to dependency compatibility issues observed in the Braket SDK / Pydantic stack.

## Boundaries

Bridge is not an AWS hardware execution SDK. It does not manage AWS accounts, Amazon S3 task locations, Braket QPU access, billing or managed execution. It also does not expose private backend adapters or internal compilation rules.

The current public role of Bridge is upstream of managed execution:

```text
preserve problem intent
-> construct an executable circuit through the supported QDSV path
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
- what canonical materialization evidence was reported;
- what compatibility adjustments were made for Braket;
- what warnings or limits should be inspected before execution.

## Public Links

- QDSV Bridge PyPI: <https://pypi.org/project/qdsv-bridge/>
- QDSV Bridge GitHub: <https://github.com/qdsvquantum-afk/qdsv-bridge>
- QDSV project overview: <https://qdsv.cloud/>
- Amazon Braket OpenQASM documentation: <https://docs.aws.amazon.com/braket/latest/developerguide/braket-openqasm.html>
- Amazon Braket OpenQASM task example: <https://docs.aws.amazon.com/braket/latest/developerguide/braket-openqasm-create-submit-task.html>
