# QDSV Bridge

[![PyPI](https://img.shields.io/pypi/v/qdsv-bridge.svg)](https://pypi.org/project/qdsv-bridge/)
[![Python](https://img.shields.io/pypi/pyversions/qdsv-bridge.svg)](https://pypi.org/project/qdsv-bridge/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/qdsvquantum-afk/qdsv-bridge/blob/main/LICENSE)
[![Status](https://img.shields.io/badge/status-developer%20preview-0ea5e9.svg)](#status-and-scope)
[![Qiskit Ecosystem](https://qisk.it/e-e8734f93)](https://www.ibm.com/quantum/ecosystem)

Source/package version: `0.5.1`. See the PyPI badge for publication status.

QDSV Bridge is a lightweight Python client SDK that converts supported semantic problem specifications into executable OpenQASM/Qiskit-compatible circuit artifacts or validated expert construction packages.

Circuit delivery is conditional on capability and resource validation. Bridge does not execute circuits, generate arbitrary circuits or embed precomputed answers.

- [Documentation](https://qdsvquantum-afk.github.io/qdsv-bridge/)
- [PyPI](https://pypi.org/project/qdsv-bridge/)
- [Source](https://github.com/qdsvquantum-afk/qdsv-bridge)

## Status And Scope

QDSV Bridge is a Developer Preview for bounded, problem-first circuit construction. The public service is provided without an SLA and may change or be temporarily unavailable.

Bridge validates the semantic-to-circuit construction path and reports the resources required by the generated artifact. It does not validate the user's domain assumptions, execute on a simulator or QPU, choose a provider, manage credentials or interpret experimental results.

The public SDK supports Python `3.9` and later. Before `1.0`, minor releases may introduce contract changes; deprecations and migration notes are recorded in the [changelog](https://github.com/qdsvquantum-afk/qdsv-bridge/blob/main/CHANGELOG.md).

## Installation

Install the client:

```bash
pip install qdsv-bridge
```

Install the optional Qiskit inspection dependencies:

```bash
pip install "qdsv-bridge[qiskit]"
```

The Qiskit extra is capped at `qiskit>=2,<3` to preserve compatibility with the currently tested Qiskit major version.

## Quickstart

The public Developer Preview does not require an API key:

```python
from qdsv_bridge import QDSVBridgeClient

client = QDSVBridgeClient()

spec = {
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
    "target": {"format": "qasm3", "backend_family": "qiskit"},
    "limits": {"max_qubits": 8, "max_depth": 160},
}

result = client.generate(spec)

print(result["status"])
print(result["artifact"]["format"])
print(result["artifact"]["content"])
print(result["construction_verification"])
```

When materialization succeeds within the supported capability and resource limits, `generate()` returns the completed circuit and loading guidance. Otherwise the SDK raises an explicit HTTP error; it does not return a substitute circuit.

## Delivery Modes

Bridge uses one specification and offers four output depths:

| Method | Intended user | Result |
|---|---|---|
| `generate()` | A user who needs the quantum core without designing it | Completed circuit, loading guidance, measurement meaning, resources and construction evidence, when materialization succeeds |
| `build()` | A developer integrating QASM or Qiskit | Editable circuit artifact, public construction summaries, resources and digests, when materialization succeeds |
| `prepare()` | An expert designing a custom circuit | Validated construction requirements and capability gaps without forcing a final circuit |
| `evaluate()` | An expert reviewing a construction | Materialization evidence and clearly labeled construction alternatives |

`evaluate()` evaluates construction evidence. It does not execute the circuit on a simulator or QPU and does not compare runtime results.

### Start By User Type

All four modes reuse the `spec` from the Quickstart. Users can begin with one call and move to a deeper delivery mode without redefining the problem.

Basic user - receive the completed quantum core and loading guidance:

```python
result = client.generate(spec)
print(result["artifact"]["content"])
print(result["ready_to_run_example"])
```

Intermediate developer - receive editable QASM/Qiskit artifacts and digests:

```python
package = client.build(spec)
print(package["editable_artifacts"]["artifact_content"])
print(package["editable_artifacts"]["oracle_spec"])
print(package["digests"])
```

Expert constructor - receive the validated construction package without forcing a circuit:

```python
prepared = client.prepare(spec)
inputs = prepared["expert_inputs"]
print(inputs["construction_status"])
print(inputs["relevant_variables"])
print(inputs["missing_capabilities"])
print(inputs["encoding_suggestions"])
```

Expert evaluator - review construction evidence and labeled alternatives without executing the circuit:

```python
review = client.evaluate(spec)
print(review["construction_verification"])
print(review["materialization_evidence"])
print(review["construction_alternatives"])
print(review["comparison"]["comparative_execution_performed"])
```

## Outputs And Outcomes

Supported public artifact targets are:

| Target | Output |
|---|---|
| `qasm2` | Completed OpenQASM 2 circuit |
| `qasm3` | Completed OpenQASM 3 circuit |
| `qiskit_blueprint` | Python loader generated from the completed canonical QASM circuit; it is not a partial circuit blueprint |
| `oracle_spec` | Public expert construction contract |
| `problem_spec` | Normalized public problem specification |
| `ir` | Stable public summary, not the private compiler representation |

Circuit-oriented targets are returned only when the full supported construction succeeds. Typical outcomes are:

| Outcome | SDK behavior |
|---|---|
| Materialized circuit | Successful `generate()` or `build()` response with artifact, resources and evidence |
| Expert construction package | Successful `prepare()` response without a forced circuit |
| Unsupported capability | `QDSVBridgeHTTPError` with the API error payload |
| Resource limit exceeded | `QDSVBridgeHTTPError` with the required resource details |
| Invalid specification | `QDSVBridgeHTTPError` with validation details |
| Transport or service failure | `QDSVBridgeAPIError` |

Handle API rejections explicitly:

```python
from qdsv_bridge import QDSVBridgeAPIError, QDSVBridgeHTTPError

try:
    result = client.generate(spec)
except QDSVBridgeHTTPError as error:
    print(error.status_code)
    print(error.payload)
except QDSVBridgeAPIError as error:
    print(f"Bridge service unavailable: {error}")
```

The current operation catalog and service limits are available from:

```python
catalog = client.capabilities()
```

For the detailed operation contract and ScoreModel v2 capabilities, see the [technical documentation](https://qdsvquantum-afk.github.io/qdsv-bridge/explanations/index.html) and [ScoreModel tutorial](https://qdsvquantum-afk.github.io/qdsv-bridge/tutorials/score_model_v2.html).

## Limits And Privacy

Bridge accepts compact semantic specifications and bounded prepared numeric inputs. It is not a bulk-data service and does not accept raw datasets or hardware-execution requests.

Public Preview limits are configurable and include payload, compilation time, artifact size, qubit and depth ceilings. A semantically valid problem may still be rejected when its materialized circuit exceeds the active resource limits. Query `client.capabilities()` for the current deployment contract.

Do not submit personal, confidential, regulated or security-sensitive data to the public preview. The public preview provides no contractual retention guarantee. Use a private deployment for sensitive workloads and review the [security policy](https://github.com/qdsvquantum-afk/qdsv-bridge/blob/main/SECURITY.md) before reporting a vulnerability.

Default public endpoint:

```python
client = QDSVBridgeClient()  # https://api.qdsv.cloud/api
```

Private/local endpoint for an existing QDSV Docker deployment:

```python
client = QDSVBridgeClient.local()  # http://localhost:18080/api
```

## Tested Compatibility

| Component | Tested/supported boundary |
|---|---|
| Python | `>=3.9` |
| Qiskit SDK | `>=2,<3` |
| Qiskit Aer | `>=0.17,<0.18` |
| Qiskit QASM 3 importer | `>=0.5,<0.7` |
| OpenQASM | QASM 2 and QASM 3 artifacts generated by Bridge |
| Amazon Braket SDK | Optional OpenQASM conversion tested with `LocalSimulator`; not version-pinned and not an official Amazon Braket integration |

Bridge does not provide managed IBM Quantum or Amazon Braket hardware execution.

## Integrations And Examples

- [First Bridge workflow](https://qdsvquantum-afk.github.io/qdsv-bridge/tutorials/first_bridge_workflow.html)
- [ScoreModel v2 circuit delivery](https://qdsvquantum-afk.github.io/qdsv-bridge/tutorials/score_model_v2.html)
- [IBM/Qiskit artifact workflow](https://github.com/qdsvquantum-afk/qdsv-bridge/blob/main/docs/integrations/ibm_quantum.md)
- [OpenQASM-first interoperability](https://github.com/qdsvquantum-afk/qdsv-bridge/blob/main/docs/integrations/openqasm.md)
- [Amazon Braket LocalSimulator conversion](https://github.com/qdsvquantum-afk/qdsv-bridge/blob/main/docs/integrations/aws_braket.md)
- [Python examples](https://github.com/qdsvquantum-afk/qdsv-bridge/tree/main/examples)
- [Colab notebooks](https://github.com/qdsvquantum-afk/qdsv-bridge/tree/main/notebooks)

The notebooks cover problem-first circuit delivery, expert construction inputs, Qiskit inspection and the tested Braket `LocalSimulator` conversion flow.

## Reports

Bridge can render the same public construction evidence as JSON, Markdown or HTML:

```python
report = client.report(spec, mode="build", format="markdown")
print(report["content"])
```

Reports identify the accepted specification, delivered artifact, warnings, resource evidence and digests. They do not claim simulator or hardware execution.

## Support And Security

- General questions and defects: [GitHub Issues](https://github.com/qdsvquantum-afk/qdsv-bridge/issues)
- Sensitive security reports: follow [SECURITY.md](https://github.com/qdsvquantum-afk/qdsv-bridge/blob/main/SECURITY.md); do not open a public issue
- Release history: [CHANGELOG.md](https://github.com/qdsvquantum-afk/qdsv-bridge/blob/main/CHANGELOG.md)
- Roadmap: [ROADMAP.md](https://github.com/qdsvquantum-afk/qdsv-bridge/blob/main/ROADMAP.md)

## License

The client SDK, examples, documentation and tests in this repository are licensed under the [MIT License](https://github.com/qdsvquantum-afk/qdsv-bridge/blob/main/LICENSE).

QDSV, QIntent and Qruba names and marks belong to their respective owners. The MIT License does not grant trademark rights.
