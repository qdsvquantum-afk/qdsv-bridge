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

Bridge emits complete OpenQASM 3 artifacts converted from the canonical QDSV QASM2 materialization. A coherent score circuit includes candidate, signal, score, comparator and predicate registers, for example:

```text
OPENQASM 3.0;
include "stdgates.inc";
bit[2] c_result;
qubit[1] candidate;
qubit[1] signal_0;
qubit[1] score_sum;
qubit[1] score_accept;
qubit[1] candidate_valid;
qubit[1] selected;
h candidate[0];
cx candidate[0], signal_0[0];
// reversible score, threshold, phase marking, uncompute and diffusion gates
c_result[0] = measure candidate[0];
c_result[1] = measure selected[0];
```

The complete artifact is inspectable and executable. Bridge no longer emits an empty semantic-oracle insertion point as a completed circuit. If canonical materialization is not possible, circuit export fails explicitly and the user can request expert semantic inputs instead.

## Framework Handoff Pattern

Bridge should be understood as upstream of the execution framework:

```text
Bridge
  declares and validates the problem-level structure
  materializes through canonical ProblemSpec/IR
  exports executable OpenQASM and reproducibility metadata

Framework
  imports or adapts the OpenQASM artifact
  handles inspection, transpilation, simulation or execution
```

This keeps the roles separated:

- Bridge records problem intent and generates auditable artifacts through the canonical QDSV materializer.
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

The Braket demo creates an executable compatibility view by defining the lowered gate set and mapping Qiskit's `cx` spelling to Braket's `cnot` spelling:

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
- canonical materialization evidence, including formula location and precomputation flags;
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
-> canonical QDSV ProblemSpec / IR
-> executable auditable OpenQASM artifact
-> framework-specific workflow
-> reproducibility report
```

Managed hardware execution, provider-specific backend routing and production lowering remain outside the public Bridge SDK.

## Public Links

- QDSV Bridge PyPI: <https://pypi.org/project/qdsv-bridge/>
- QDSV Bridge GitHub: <https://github.com/qdsvquantum-afk/qdsv-bridge>
- QDSV project overview: <https://qdsv.cloud/>
- OpenQASM specification: <https://openqasm.com/>
