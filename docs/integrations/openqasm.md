# QDSV Bridge OpenQASM-First Interoperability

Status: public developer preview.

QDSV Bridge is a problem-first specification layer that exports auditable OpenQASM artifacts from controlled semantic problem specifications.

The goal is not to replace circuit frameworks. The goal is to preserve problem intent before the artifact enters a framework-specific workflow such as Qiskit, Amazon Braket, or another OpenQASM-aware toolchain.

## Why OpenQASM

OpenQASM provides a portable circuit representation that can be inspected, adapted and routed into multiple quantum software ecosystems.

Bridge uses OpenQASM as a public artifact boundary:

```text
problem intent
-> controlled semantic specification
-> Bridge validation/build
-> OpenQASM artifact
-> framework-specific inspection or execution workflow
-> Bridge Report
```

This makes the handoff explicit. The user can see what Bridge generated, which semantic family was used, what warnings were reported and which digests identify the artifact.

## Current Public Artifact

Bridge currently emits OpenQASM 3-oriented artifacts for circuit targets:

```openqasm
OPENQASM 3.0;
include "stdgates.inc";
// QDSV Bridge family: bounded_semantic_marking
// QDSV oracle_digest: sha256:...
// Blueprint: semantic oracle materialization point is intentionally explicit.
qubit[3] q;
bit[3] c;
h q[0];
h q[1];
h q[2];
// qdsv_semantic_oracle(q) would be inserted here by the target integration.
// Optional amplitude amplification can be inserted here when supported.
c = measure q;
```

The artifact is intentionally inspectable. In Developer Preview, some semantic oracle materialization points remain explicit so downstream users can inspect, complete, replace or adapt the target-specific realization.

## Framework Handoff Pattern

Bridge should be understood as upstream of the execution framework:

```text
Bridge
  declares and validates the problem-level structure
  exports OpenQASM and reproducibility metadata

Framework
  imports or adapts the OpenQASM artifact
  handles inspection, transpilation, simulation or execution
```

This keeps the roles separated:

- Bridge preserves problem intent and generates auditable artifacts.
- Qiskit, Braket or another framework controls framework-specific simulation, transpilation and execution.

## Qiskit Path

Qiskit can load the Bridge OpenQASM artifact when the current environment supports the generated OpenQASM 3 features:

```python
from qiskit import qasm3

circuit = qasm3.loads(qasm3_source)
print(circuit)
```

See:

- [QDSV Bridge for IBM/Qiskit Workflows](ibm_quantum.md)
- [Open 04 IBM/Qiskit Artifact Demo](https://colab.research.google.com/github/qdsvquantum-afk/qdsv-bridge/blob/main/notebooks/04_ibm_qiskit_bridge_demo.ipynb)

## Amazon Braket Path

Amazon Braket documents OpenQASM examples with the `OPENQASM 3;` header and without `stdgates.inc`. The Braket demo therefore creates a small compatibility view before passing the source to the Amazon Braket SDK:

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
```

The resulting source can be used with `braket.ir.openqasm.Program` and `LocalSimulator`:

```python
from braket.devices import LocalSimulator
from braket.ir.openqasm import Program

program = Program(source=braket_qasm)
result = LocalSimulator().run(program, shots=1024).result()
print(dict(result.measurement_counts))
```

See:

- [QDSV Bridge for Amazon Braket OpenQASM Workflows](aws_braket.md)
- [Open 05 AWS Braket OpenQASM Demo](https://colab.research.google.com/github/qdsvquantum-afk/qdsv-bridge/blob/main/notebooks/05_aws_braket_openqasm_demo.ipynb)

## Reproducibility Layer

Every Bridge Report records:

- the problem and deliverable contract;
- family and mode used;
- semantic preservation evidence;
- generated artifact content;
- warnings and limits;
- artifact, IR, oracle, materialization and problem-spec digests.

This means the OpenQASM artifact is not just a circuit text file. It is attached to a traceable semantic export package.

## Boundaries

Bridge is not an official integration for Qiskit, Amazon Braket or any other provider.

Bridge is not a hardware execution SDK, backend scheduler, transpiler replacement or universal quantum compiler.

The current public role of Bridge is:

```text
controlled semantic spec
-> auditable OpenQASM artifact
-> framework-specific workflow
-> reproducibility report
```

Managed hardware execution, provider-specific backend routing and production lowering remain outside the public Bridge SDK.

## Public Links

- QDSV Bridge PyPI: <https://pypi.org/project/qdsv-bridge/>
- QDSV Bridge GitHub: <https://github.com/qdsvquantum-afk/qdsv-bridge>
- QDSV project overview: <https://qdsv.cloud/>
- OpenQASM specification: <https://openqasm.com/>
