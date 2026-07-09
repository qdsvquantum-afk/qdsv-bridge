# QDSV Bridge Developer Preview

[![PyPI](https://img.shields.io/pypi/v/qdsv-bridge.svg)](https://pypi.org/project/qdsv-bridge/)
[![Python](https://img.shields.io/pypi/pyversions/qdsv-bridge.svg)](https://pypi.org/project/qdsv-bridge/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-developer%20preview-0ea5e9.svg)](#resource-and-multi-user-limits)
[![Qiskit Ecosystem](https://qisk.it/e-e8734f93)](https://www.ibm.com/quantum/ecosystem)

Current package version: `0.1.5`.

QDSV Bridge is a lightweight Python client SDK for a controlled semantic-to-circuit bridge built on **QDSV - Quantum Declarative Semantic Value**.

It turns supported problem-family specifications into problem-derived circuit materializations, QDSV IR, oracle specs, QASM/Qiskit artifacts or expert construction inputs.

The public developer preview is available without an API key:

```python
from qdsv_bridge import QDSVBridgeClient

client = QDSVBridgeClient()  # Uses https://api.qdsv.cloud/api
```

Use a private/local Docker node only when you are running QDSV privately:

```python
client = QDSVBridgeClient.local()  # Uses http://localhost:18080/api
```

QDSV Bridge is not a template selector and not a free arbitrary circuit generator. Its core rule is:

```text
do not force the problem into a prefabricated circuit;
derive the circuit or construction inputs from the semantic problem specification.
```

## Choose A Mode

Bridge has one SDK with different output depths:

| If you are... | Use | Python helper | Main output |
|---|---|---|---|
| A basic user who wants a ready artifact | Bridge Use | `client.generate(spec)` | Simple generated artifact, guidance and ready-to-run example |
| A Qiskit/QASM/OpenQASM user | Bridge Build | `client.build(spec)` | QASM/Qiskit-oriented artifact, oracle spec, IR summary, digests and preservation report |
| An expert circuit constructor | Bridge Expert Prepare | `client.prepare(spec)` | Semantic construction inputs without forcing a final circuit |
| An expert evaluating materializations | Bridge Expert Evaluate | `client.evaluate(spec)` | Suggested materialization variants and comparison evidence |

If you are not sure where to start, use:

```python
result = client.generate(spec)  # basic
```

If you want to inspect or route the artifact into Qiskit, Braket or another OpenQASM-oriented workflow, use:

```python
result = client.build(spec)  # intermediate/developer
```

## 5 Minute Quickstart

Install the SDK:

```bash
pip install qdsv-bridge
```

Build a QASM3 artifact from a compact semantic spec. No key is required in the public preview:

```python
from qdsv_bridge import QDSVBridgeClient

client = QDSVBridgeClient()

spec = {
    "family": "bounded_semantic_marking",
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

result = client.generate(spec)  # basic-user mode

print(result["status"])
print(result["bridge_mode"])
print(result["circuit_origin"])
print(result["artifact"]["format"])
```

For a developer-oriented package with oracle spec, IR summary, digests and preservation evidence:

```python
result = client.build(spec)

print(result["editable_artifacts"]["oracle_spec"])
print(result["editable_artifacts"]["ir_summary"])
print(result["digests"])
```

## Colab Notebooks

Use these notebooks when you want to try Bridge without setting up a local project:

| Notebook | Flow |
|---|---|
| [Open 01 Semantic Candidate Marking](https://colab.research.google.com/github/qdsvquantum-afk/qdsv-bridge/blob/main/notebooks/01_semantic_candidate_marking.ipynb) | `bounded_semantic_marking` -> QASM3 artifact -> Bridge Report |
| [Open 02 Predicate Oracle Marking](https://colab.research.google.com/github/qdsvquantum-afk/qdsv-bridge/blob/main/notebooks/02_predicate_oracle_marking.ipynb) | `predicate_marking` -> Qiskit blueprint -> Bridge Report |
| [Open 03 Semantic Signal Classification](https://colab.research.google.com/github/qdsvquantum-afk/qdsv-bridge/blob/main/notebooks/03_semantic_signal_classification.ipynb) | `semantic_signal_classification` -> QASM3 artifact -> Bridge Report |
| [Open 04 IBM/Qiskit Artifact Demo](https://colab.research.google.com/github/qdsvquantum-afk/qdsv-bridge/blob/main/notebooks/04_ibm_qiskit_bridge_demo.ipynb) | Problem-first spec -> QASM3 artifact -> Qiskit inspection/simulation -> Bridge Report |
| [Open 05 AWS Braket OpenQASM Demo](https://colab.research.google.com/github/qdsvquantum-afk/qdsv-bridge/blob/main/notebooks/05_aws_braket_openqasm_demo.ipynb) | Problem-first spec -> OpenQASM artifact -> Braket LocalSimulator -> Bridge Report |

Each notebook follows the same route:

```text
problem spec -> Bridge artifact -> shareable report
```

## IBM/Qiskit Workflow

For Qiskit-oriented users, see the public integration guide:

- [QDSV Bridge for IBM/Qiskit Workflows](docs/integrations/ibm_quantum.md)
- [Open 04 IBM/Qiskit Artifact Demo](https://colab.research.google.com/github/qdsvquantum-afk/qdsv-bridge/blob/main/notebooks/04_ibm_qiskit_bridge_demo.ipynb)

## Amazon Braket OpenQASM Workflow

For Braket-oriented users, see the public OpenQASM integration guide:

- [QDSV Bridge for Amazon Braket OpenQASM Workflows](docs/integrations/aws_braket.md)
- [Amazon Braket Community Submission Path](docs/integrations/aws_braket_community_path.md)
- [Open 05 AWS Braket OpenQASM Demo](https://colab.research.google.com/github/qdsvquantum-afk/qdsv-bridge/blob/main/notebooks/05_aws_braket_openqasm_demo.ipynb)

QDSV Bridge exports OpenQASM artifacts that can be inspected and executed in Braket-oriented workflows using the Amazon Braket SDK and `LocalSimulator`. This is not an official Amazon Braket integration and does not include managed AWS hardware execution.

## OpenQASM-First Interoperability

For a provider-neutral view of the Bridge artifact handoff, see:

- [QDSV Bridge OpenQASM-First Interoperability](docs/integrations/openqasm.md)

Bridge uses OpenQASM as a public artifact boundary between controlled semantic problem specifications and framework-specific workflows such as Qiskit or Amazon Braket.

Default cloud endpoint:

```text
https://api.qdsv.cloud/api
```

Private/local Docker endpoint:

```python
client = QDSVBridgeClient.local()
```

## What This Is

- A client SDK for QDSV Bridge.
- A controlled semantic-to-circuit export interface.
- A way to request QDSV IR, oracle specs, QASM/Qiskit artifacts or expert construction inputs.
- A way to generate shareable Bridge Reports in JSON, Markdown or HTML.
- A bridge for users who need circuit ecosystems but do not want to start from prebuilt templates.

## What This Is Not

- It is not the private QDSV Runtime.
- It is not a bulk data processing SDK.
- It is not a hardware execution SDK.
- It is not an arbitrary circuit generator.
- It is not a selector of prefabricated circuit templates.
- It does not expose CAP, backend selection heuristics, private lowering internals, QuEST/Aer/IBM adapters, secrets or production configuration.

## Why This Exists

Traditional quantum workflows often start by asking users to choose a circuit, encoding, ansatz or measurement pattern. That can force the data to adapt to a circuit.

QDSV Bridge starts from a controlled semantic family. The family defines what kind of problem is allowed, what concepts belong to it, what patterns are excluded and what evidence must be produced.

```text
problem family spec
-> family ontology validation
-> semantic ProblemSpec / IR
-> oracle specification
-> materialization policy
-> generated circuit artifact or expert construction inputs
```

For users who need circuit ecosystems, Bridge derives a new circuit artifact from that semantic specification instead of asking the user to adapt the problem to a ready-made template.

For expert constructors, Bridge can also return the key semantic inputs needed to design a custom circuit without forcing a final circuit.

## Bridge Modes

QDSV Bridge is one SDK with multiple output depths. The modes do not change the core principle: the circuit, when delivered, is derived from the semantic problem specification.

| API | Commercial name | Intended user | What Bridge returns |
|---|---|---|---|
| `generate()` / `use` | Bridge Use | Basic user who wants to solve without designing circuits. | A new problem-derived circuit artifact, simple explanation, information-loss risk, usage recommendation and ready-to-run example. |
| `build()` / `build` | Bridge Build | Intermediate user who understands Qiskit, QASM or quantum workflows. | A new problem-derived circuit artifact plus QASM/Qiskit, oracle spec, IR summary, preservation report, estimated qubits/depth and digests. |
| `prepare()` / `expert_prepare` | Bridge Expert Prepare | Expert constructor who wants to design a custom circuit. | Validated family, ProblemSpec/IR, oracle spec, predicates, target state/goal, constraints, variables, information-loss risk, encoding/measurement suggestions, estimated limits and evidence. It does not force a final circuit. |
| `evaluate()` / `expert_evaluate` | Bridge Expert Evaluate | Expert evaluator who wants to compare QDSV materializations. | Suggested QDSV circuit artifact, materialization variants, comparison and preservation report. |

Python helpers:

```python
client.generate(spec)  # mode="use"
client.build(spec)     # mode="build"
client.prepare(spec)   # mode="expert_prepare"
client.evaluate(spec)  # mode="expert_evaluate"
```

Explicit mode:

```python
client.export(spec, mode="build")
client.explain(spec, mode="expert_prepare")
```

CLI:

```bash
qdsv-bridge export spec.json --mode use
qdsv-bridge export spec.json --mode build
qdsv-bridge export spec.json --mode expert_prepare
qdsv-bridge export spec.json --mode expert_evaluate
qdsv-bridge report spec.json --mode build --format markdown --output bridge_report.md
```

Every export response should include traceability metadata:

```json
{
  "mode": "use | build | expert_prepare | expert_evaluate",
  "artifact_type": "qasm3",
  "circuit_origin": "qdsv_derived",
  "semantic_preservation": {"status": "accepted", "score": 1.0},
  "warnings": [],
  "digests": {}
}
```

## Examples By User Type

Basic user:

```python
result = client.generate(spec)
print(result["circuit_origin"])          # qdsv_derived
print(result["circuit"]["status"])       # generated_from_semantic_spec
print(result["ready_to_run_example"])
```

Intermediate developer:

```python
result = client.build(spec)
print(result["artifact"]["format"])
print(result["editable_artifacts"]["oracle_spec"])
print(result["editable_artifacts"]["ir_summary"])
print(result["digests"])
```

Expert constructor:

```python
inputs = client.prepare(spec)
print(inputs["expert_inputs"]["encoding_suggestions"])
print(inputs["expert_inputs"]["measurement_suggestions"])
```

Expert evaluator:

```python
comparison = client.evaluate(spec)
print(comparison["materialization_variants"])
print(comparison["comparison"])
```

## Supported Families

Developer Preview families:

| Family | Status | Use it for |
|---|---|---|
| `bounded_semantic_marking` | Generic fallback, developer preview | Finite, bounded semantic marking/ranking/constraint problems that do not yet fit a specialized family. This is the safest generic starting point. |
| `semantic_signal_classification` | Developer preview | Classification, marking or ranking from prepared numeric signals such as scores, risk indicators, eligibility signals or scientific features. |
| `predicate_marking` | Developer preview | Marking finite candidates that satisfy a bounded predicate such as threshold, range or set membership. |
| `state_similarity` | Developer preview | Similarity, overlap or fidelity-style relations over prepared numeric states or vectors. |
| `combinatorial_relation` | Developer preview | Bounded relations over finite domains, assignments or constraint-satisfaction structures. |
| `distribution_sampling` | Specified experimental | Distribution inspection or sampling over finite state spaces. Do not use it for production randomness or cryptographic claims. |

`bounded_semantic_marking` is the controlled fallback family. Use it when the problem is finite, bounded and semantic, but no specialized Bridge family exists yet.

It is not a universal free-form mode: it still requires a bounded state space, declared goal, limits, excluded patterns and preservation reporting.

Each family has:

- ontology boundary;
- allowed state-space kinds;
- allowed goal kinds;
- allowed semantic operations;
- excluded patterns;
- public limits;
- export targets;
- evidence / digest contract.

Fallback example:

```python
spec = {
    "family": "bounded_semantic_marking",
    "state_space": {
        "kind": "finite_candidates",
        "candidate_count": 128,
        "candidate_id": "candidate",
    },
    "signals": ["risk_score", "value_score", "eligibility_score"],
    "goal": {
        "kind": "marking",
        "predicate": "eligible_candidate",
    },
    "target": {
        "format": "qasm3",
        "backend_family": "qiskit",
    },
    "limits": {
        "max_qubits": 8,
        "max_depth": 250,
    },
}

result = client.build(spec)
print(result["family"])
print(result["circuit_origin"])
print(result["warnings"])
```

## What It Exports

Depending on `target.format`, QDSV Bridge can export:

- `problem_spec`
- `ir`
- `oracle_spec`
- `qasm2`
- `qasm3`
- `qiskit_blueprint`

## Bridge Report

Bridge Report turns the same auditable export package into a document users can share, attach to technical notes or keep as reproducibility evidence.

Supported report formats:

- `json`
- `markdown`
- `html`

Python:

```python
report = client.report(spec, mode="build", format="markdown")
print(report["content"])
```

CLI:

```bash
qdsv-bridge report spec.json --mode build --format markdown --output bridge_report.md
qdsv-bridge report spec.json --mode build --format html --output bridge_report.html
qdsv-bridge report spec.json --mode build --format json --output bridge_report.json
```

Each Bridge Report includes:

1. Problem and deliverable contract.
2. Family and mode used.
3. Validations and semantic preservation evidence.
4. Generated artifact summary and QASM/Qiskit blueprint content when requested.
5. Circuit policy and template-use status.
6. Digests.
7. Resource limits and warnings.
8. Reproducibility metadata.

Bridge Report is the public trust document for Bridge: it makes clear what was derived, what was preserved, what was warned about and which digests identify the exported artifacts.

For `use` and `build`, circuit-oriented targets return a circuit artifact derived from the semantic spec, with explicit QDSV oracle/digest information and preservation metadata.

In Developer Preview, some targets are returned as integration blueprints with semantic oracle insertion points so external platforms can inspect, execute, optimize or complete the materialization safely.

For `expert_prepare`, Bridge may intentionally return construction inputs instead of forcing a final circuit. This is useful when an expert wants to design a custom circuit with the correct semantic ingredients.

## Public Endpoints

The SDK calls the QDSV API:

- `GET /api/bridge/families`
- `POST /api/bridge/validate`
- `POST /api/bridge/compile`
- `POST /api/bridge/explain`
- `POST /api/bridge/export`
- `POST /api/bridge/report`

Default cloud endpoint:

```python
client = QDSVBridgeClient(api_url="https://api.qdsv.cloud/api")
```

Local/private Docker endpoint:

```python
client = QDSVBridgeClient.local()
```

Public informational endpoints such as `families()` are open. Developer Preview value-producing operations can be used without an API key and are limited by rate limits, payload limits and a demo quota per caller bucket. Deployments can optionally enable API-key-only access for partners, pilots or private environments.

## Resource And Multi-User Limits

QDSV Bridge accepts compact semantic problem specifications, not raw datasets.

Do not send:

- full CSV files;
- raw datasets;
- thousands of rows;
- sensitive records;
- training data;
- hardware execution requests.

Send:

- problem family;
- finite state-space size;
- prepared signal or variable names;
- goal / predicate / ranking intent;
- target format;
- qubit/depth limits;
- materialization policy.

Public API minimum limits:

| Limit | Default |
|---|---:|
| Max spec payload | 64 KB |
| Max QASM / circuit artifact payload | 256 KB |
| Max compile time | 5 seconds |
| Max export time | 10 seconds |
| API key required for | Not required by default in Developer Preview |
| Monthly demo quota | 100 compilations/exports/reports per caller bucket |
| Raw data payloads | Not allowed |
| Hardware execution | Not available from Bridge SDK |
| `bounded_semantic_marking` | 1024 candidates / 24 signals |
| `semantic_signal_classification` | 1024 candidates / 32 signals |
| `predicate_marking` | 2048 candidates / 8 signals |
| `state_similarity` | 1024 candidates / 64 signals |
| `combinatorial_relation` | 4096 candidates / 16 signals |
| `distribution_sampling` | 2048 candidates / 16 signals |

Default API rate limits may be configured by the QDSV deployment:

- `families`: 60/minute
- `validate`: 30/minute
- `compile`: 20/minute
- `explain`: 20/minute
- `export`: 10/minute
- `report`: 10/minute

Rate limits use `Authorization`, `x-api-key` or `x-license-key` when present. Otherwise they fall back to IP plus SDK name.

API keys are optional for the open Developer Preview path. They become useful for higher quotas, partner access, private pilots, usage attribution or deployments configured with `QDSV_BRIDGE_API_KEY_REQUIRED=true`.

In the current public deployment, rate limiting is in-memory per API instance. If Cloud Run scales to multiple instances, the effective limit may multiply until a distributed rate-limit store is enabled.

The SDK itself is stateless and does not block multiple users. Multi-user control, quotas, optional API keys, license checks and history belong to the QDSV/Qruba API deployment, not to the local Python package.

Raw dataset payloads are rejected:

```json
{
  "detail": {
    "error_code": "E_BRIDGE_RAW_DATA_NOT_ALLOWED",
    "message": "Raw datasets are not allowed in Bridge specs. Provide semantic signals, predicates, candidates, or summarized problem structure instead.",
    "detail": {
      "forbidden_fields": ["rows"]
    }
  }
}
```

## Examples And Roadmap

- [Examples](examples/)
- [Roadmap](ROADMAP.md)
- [QDSV model site](https://qdsv.cloud/)
- [Qruba Cloud](https://cloud.qruba.site/)
- [PyPI](https://pypi.org/project/qdsv-bridge/)

Current public artifact targets are `problem_spec`, `ir`, `oracle_spec`, `qasm2`, `qasm3` and `qiskit_blueprint`.

PennyLane, Azure Quantum/Q#, Cirq, VS Code, TypeScript clients, Amazon Braket managed hardware execution and packaged NISQ recipes such as QUBO/QAOA/VQE/Grover are planned integrations or higher-level examples. They should not be described as current public Bridge capabilities.

## Important Boundaries

QDSV Bridge does not expose:

- QDSV Runtime internals;
- CAP internals;
- backend selection heuristics;
- private QuEST/Aer/IBM adapters;
- native lowering internals;
- unrestricted circuit generation;
- arbitrary Python execution;
- prefabricated circuit selection as the main product;
- user-supplied free circuits as family contracts.

Product principle:

```text
controlled semantic family
-> problem-derived circuit materialization or expert inputs
-> auditable export
```

Not:

```text
any input -> arbitrary circuit
```

## Open SDK, Private Runtime

This repository is open-core:

- Open under MIT: Python client SDK, examples, docs and tests.
- Not included: QDSV Runtime, ontology compiler internals, CAP, lowering, advanced materialization, backend adapters, private endpoints, secrets or production configuration.

QDSV, QIntent and Qruba names and marks are project marks of their respective owners. The MIT License for this repository does not grant trademark rights.
