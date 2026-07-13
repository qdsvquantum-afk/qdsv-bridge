# QDSV Bridge Developer Preview

[![PyPI](https://img.shields.io/pypi/v/qdsv-bridge.svg)](https://pypi.org/project/qdsv-bridge/)
[![Python](https://img.shields.io/pypi/pyversions/qdsv-bridge.svg)](https://pypi.org/project/qdsv-bridge/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-developer%20preview-0ea5e9.svg)](#resource-and-multi-user-limits)
[![Qiskit Ecosystem](https://qisk.it/e-e8734f93)](https://www.ibm.com/quantum/ecosystem)

Current package version: `0.4.2`.

Documentation site: https://qdsvquantum-afk.github.io/qdsv-bridge/

QDSV Bridge converts supported semantic problem specifications into executable quantum circuit artifacts or expert construction packages. It is a lightweight Python client SDK built on **QDSV - Quantum Declarative Semantic Value**.

Bridge never labels an incomplete artifact as a completed circuit. If the accepted problem can be constructed with the currently supported capabilities and resource limits, Bridge returns the circuit. Otherwise it returns a bounded expert construction package or an explicit capability error; it does not invent a circuit or embed a precomputed answer.

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

## Choose A Delivery Mode

Bridge has one SDK with four delivery modes. Choose the mode by the output you need, not by creating a different kind of project.

Choose how much control you want over the returned artifact. A legacy `family` value may be retained as a descriptive label, but operation capabilities determine whether a circuit can be generated:

| If you need... | Use | Python helper | Main output |
|---|---|---|---|
| A simpler starting point without designing circuits | Bridge Use | `client.generate(spec)` | Canonically materialized circuit, evidence, guidance and ready-to-run example |
| An inspectable OpenQASM/Qiskit artifact | Bridge Build | `client.build(spec)` | Executable QASM/Qiskit artifact, public oracle contract, stable public IR summary, actual metrics and digests |
| Expert construction inputs before final circuit materialization | Bridge Expert Prepare | `client.prepare(spec)` | Semantic construction inputs without forcing a final circuit |
| Expert evaluation of a materialized artifact | Bridge Expert Evaluate | `client.evaluate(spec)` | The actual materialization, construction evidence and clearly labeled non-materialized alternatives |

If you are not sure where to start, use:

```python
result = client.generate(spec)  # basic
```

If you want to inspect or route the artifact into Qiskit, Braket or another OpenQASM-oriented workflow, use:

```python
result = client.build(spec)  # intermediate/developer
```

Expert users have two separate routes: `prepare` for semantic construction ingredients, and `evaluate` for the actual materialization evidence plus clearly labeled conceptual alternatives.

## 5 Minute Quickstart

Install the SDK:

```bash
pip install qdsv-bridge
```

For the optional Qiskit artifact inspection path:

```bash
pip install "qdsv-bridge[qiskit]"
```

The Qiskit extra is intentionally version-capped to the current supported major series (`qiskit>=2,<3`) to follow Qiskit Ecosystem compatibility guidance.

Build a QASM3 artifact from a compact semantic spec. No key is required in the public preview:

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
    "target": {
        "format": "qasm3",
        "backend_family": "qiskit",
    },
    "limits": {
        "max_qubits": 8,
        "max_depth": 160,
    },
}

result = client.generate(spec)  # basic-user mode

print(result["status"])
print(result["bridge_mode"])
print(result["circuit_origin"])
print(result["artifact"]["format"])
print(result["materialization_evidence"]["formula_materialized_in"])
print(result["materialization_evidence"]["candidate_precomputed"])
print(result["construction_verification"])
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
| [Open 02 Predicate Construction Inputs](https://colab.research.google.com/github/qdsvquantum-afk/qdsv-bridge/blob/main/notebooks/02_predicate_oracle_marking.ipynb) | `predicate_marking` -> expert construction inputs -> Bridge Report |
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

For users of the tested Amazon Braket `LocalSimulator` conversion workflow, see:

- [QDSV Bridge for Amazon Braket OpenQASM Workflows](docs/integrations/aws_braket.md)
- [Amazon Braket Community Submission Path](docs/integrations/aws_braket_community_path.md)
- [Open 05 AWS Braket OpenQASM Demo](https://colab.research.google.com/github/qdsvquantum-afk/qdsv-bridge/blob/main/notebooks/05_aws_braket_openqasm_demo.ipynb)

QDSV Bridge exports an OpenQASM artifact compatible with the tested Amazon Braket `LocalSimulator` conversion workflow and includes `to_braket_openqasm()` for its bounded gate-name/definition conversion. This is not an official Amazon Braket integration and does not include managed AWS hardware execution.

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
- A controlled interface for requesting problem-derived quantum circuit artifacts.
- A way to request QASM/Qiskit artifacts, public construction contracts or expert construction inputs.
- A way to generate shareable Bridge Reports in JSON, Markdown or HTML.
- A bridge for users who need circuit ecosystems but do not want to start from prebuilt templates.

## What This Is Not

- It is not the private QDSV Runtime.
- It is not a bulk data processing SDK.
- It is not a hardware execution SDK.
- It is not an arbitrary circuit generator.
- It is not a selector of prefabricated circuit templates.
- It does not expose the private runtime, internal compilation or optimization rules, private backend adapters, secrets or production configuration.

## Why This Exists

Traditional quantum workflows often start by asking users to choose a circuit, encoding, ansatz or measurement pattern. That can force the data to adapt to a circuit.

QDSV Bridge starts from a bounded semantic problem and checks that every required capability and resource is available before a circuit is claimed.

```text
semantic problem spec
-> capability and resource validation
-> executable circuit or expert construction package
-> auditable report
```

For users who want a simpler starting point, Bridge can generate executable problem-derived circuits when the specification compiles completely to a reversible semantic formula. It refuses to present incomplete blueprints or classically enumerated answer oracles as completed circuits.

For expert constructors, Bridge can also return the key semantic inputs needed to design a custom circuit without forcing a final circuit.

## Bridge Modes

QDSV Bridge is one SDK with multiple output depths. The modes do not change the core principle: a circuit is delivered only after the complete supported construction path succeeds.

| API | Commercial name | Intended user | What Bridge returns |
|---|---|---|---|
| `generate()` / `use` | Bridge Use | Basic user who needs a circuit without designing its quantum core. | Ready-to-use canonical circuit, dependencies, expected inputs, measurement meaning, actual resources and a minimal loading example. Execution and integration remain with the user. |
| `build()` / `build` | Bridge Build | Intermediate user who understands Qiskit, QASM or quantum workflows. | Canonical materialized circuit plus executable QASM/Qiskit, oracle spec, IR summary, actual qubits/depth and digests. |
| `prepare()` / `expert_prepare` | Bridge Expert Prepare | Expert constructor who wants to design a custom circuit. | Validated semantic specification, ProblemSpec/IR, oracle contract, predicates, variables, constraints, capability gaps, encoding/measurement guidance, limits and digests. It does not force a final circuit. |
| `evaluate()` / `expert_evaluate` | Bridge Expert Evaluate | Expert evaluator who wants the full construction evidence. | The actual canonical materialization and resources. Any other design is labeled conceptual until it is independently materialized; Bridge does not claim an execution comparison. |

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
  "circuit_origin": "qdsv_canonical_problem_ir_materializer",
  "materialization_evidence": {
    "formula_materialized_in": "quantum_circuit",
    "execution_performed": false,
    "classical_scan": false,
    "candidate_precomputed": false,
    "answer_leakage": false,
    "precomputed_result_table": false
  },
  "construction_verification": {
    "status": "passed",
    "scope": "semantic_specification_to_circuit_construction",
    "execution_performed": false
  },
  "warnings": [],
  "digests": {}
}
```

## Examples By User Type

Basic user:

```python
result = client.generate(spec)
print(result["circuit_origin"])          # qdsv_canonical_problem_ir_materializer
print(result["circuit"]["status"])       # materialized_from_canonical_problem_ir
print(result["ready_to_run_example"]["dependencies"])
print(result["ready_to_run_example"]["measurement_contract"])
print(result["ready_to_run_example"]["resources"])
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
print(inputs["expert_inputs"]["construction_status"])
print(inputs["expert_inputs"]["missing_capabilities"])
print(inputs["expert_inputs"]["encoding_suggestions"])
print(inputs["expert_inputs"]["measurement_suggestions"])
```

Expert evaluator:

```python
comparison = client.evaluate(spec)
print(comparison["materialization_variants"])
print(comparison["construction_alternatives"])
print(comparison["comparison"])
```

## How Bridge Checks The Circuit Construction

Bridge verifies the construction path before returning a completed circuit:

1. It validates and normalizes the semantic specification.
2. It builds one canonical public problem representation and operation plan.
3. It rejects the circuit request if any required operation lacks a certified implementation.
4. It checks the reversible compute/decision/uncompute contract and rejects
   embedded answer tables or precomputed winning candidates.
5. It materializes the concrete circuit, measures its actual qubits, depth and
   operation counts, and enforces the requested/public resource limits.
6. It links the specification, IR, formula/oracle and artifact with digests.

The response exposes these checks in `construction_verification`. This verifies
that the delivered artifact was constructed from the accepted semantic
specification through the supported QDSV path. It does **not** prove that the
user modeled the real-world problem correctly, that the supplied data is true,
or that a simulator/QPU produced a correct business result. Bridge does not run
the circuit; execution, provider selection, credentials, shots, cost and result
validation remain with the user.

### Advanced Technical Boundary

Internally, the supported path uses a typed operation graph and a reversible
intermediate representation before concrete circuit generation. These stages
are mentioned here only to define the verification boundary: the public SDK
does not expose the private reversible IR, lowering implementation, optimization
rules or backend adapters. Public responses contain only stable summaries,
capability identifiers, resource evidence and digests.

## Operation Capabilities

Circuit construction is selected from the required operations and available capabilities, not from a problem-family name. Query the current catalog with:

```python
catalog = client.capabilities()
print(catalog["operation_capabilities"])
```

Each physical/composite operation reports whether it is semantically supported,
graph-composable, verified for circuit generation and QASM loading, and whether
a resource profile is available. Verification is profile-specific; it is not a
claim that the same operation is materializable in every possible context.

`client.capabilities()` uses `/api/bridge/capabilities`. The previous
`client.families()` helper remains only as a compatibility alias; family labels
do not select a compiler, set physical capacity or promise circuit delivery.

The compiler v1 executable slice supports bounded prepared numeric data and predicates composed from:

- fields and constants;
- addition and subtraction;
- multiplication and division within the certified bounded profile;
- absolute and squared differences plus bounded similarity expressions;
- `eq`, `ne`, `lt`, `lte`, `gt` and `gte` decisions;
- ScoreModel v2 flat and hierarchical importance-priority aggregation;
- signed contextual adjustments, normalization and penalties;
- reversible formula and decision operators with explicit uncompute evidence.

## ScoreModel v2 Decision Capability

ScoreModel v2 is the broadest decision-oriented circuit path currently exposed
through Bridge. It is not tied to one industry or to similarity alone. It
materializes bounded multi-criteria decision predicates over finite candidates
through the canonical QDSV operation compiler.

ScoreModel v2 accepts two complementary value routes:

| Value route | What the user provides | Typical sources |
|---|---|---|
| Prepared numeric metric | Any finite numeric value that fits the declared numeric contract, together with optional provenance | Probability, normalized distance, risk metric, correlation, externally calculated similarity, model output or domain measurement |
| QDSV numeric expression | Prepared numeric fields plus a bounded operation graph supported by the ScoreModel v2 physical profile | Direct values, bounded arithmetic, absolute or squared difference and scalar numeric similarity |

An externally produced metric remains an input: Bridge does not claim to have
computed it. This lets users bring a value from another model or domain process
while QDSV materializes the bounded decision operation. QDSV can also compute
scalar numeric similarity inside the circuit profile. Arbitrary vector or cosine
similarity is not currently computed by this physical profile, but a separately
computed finite similarity value can be supplied as a prepared numeric metric.

The implemented ScoreModel v2 capability includes:

- flat multi-term decisions;
- hierarchical decisions with independent importance and priority at each block;
- non-negative term and block importance and priority values;
- signed contextual adjustments over bounded adjustment values;
- term aggregation, normalization and zero-mass protection;
- flat/global and hierarchical block/global penalty handling;
- exact rational semantic evaluation followed by declared fixed-point output,
  deterministic rounding and overflow rejection;
- `eq`, `ne`, `lt`, `lte`, `gt` and `gte` threshold decisions;
- bounded value expressions using fields, constants, addition, subtraction,
  multiplication, division, safe division, modulo, absolute value, absolute
  difference, squared difference and scalar numeric similarity when accepted by
  the current capability assessment;
- candidate-independent reversible formula synthesis, decision marking,
  measurement and explicit uncompute evidence;
- optional bounded Grover amplification inside the certified ScoreModel v2
  materialization, without inferring winning candidates through a classical
  answer scan. This is not a general Grover recipe for arbitrary problems.

Public ScoreModel specifications use user-oriented decision names:

```python
term = {
    "value": prepared_metric,
    "importance": 2,
    "priority": 3,
}
```

`importance` expresses the relative contribution of a factor. `priority`
expresses its declared urgency or severity. The compiler uses their product as
the factor applied in both the weighted numerator and normalization mass. A zero
value removes that term or block from the aggregate; `priority` is not circuit
execution order or precedence. The legacy
names `weight` and `criticality` remain accepted for compatibility, but new SDK
code and public Bridge responses use `importance` and `priority`. QDSV keeps any
canonical mathematical naming internal to the operation compiler.

This supports practical finite-candidate workflows such as:

- eligibility, approval and compliance screening;
- multi-criteria candidate selection by threshold;
- risk-benefit and cost-value assessment;
- project, supplier, customer, hypothesis or alternative evaluation;
- contextual decisions where the same observed value must be adjusted by
  declared circumstances;
- hierarchical decisions that combine local block assessments into one global
  acceptance predicate.

These are threshold-based decision and selection workflows. The current physical
profile does **not** claim complete ranking, Top-K, argmax/argmin, unrestricted
optimization, arbitrary vector similarity or automatic model calibration.

ScoreModel v2 is available through a canonical `problem_spec`. Bridge returns the
materialized circuit and a public evidence passport. It does not expose private
compiler implementation, internal optimization rules, intermediate candidate
scores or precomputed answers. The public profile is only a capability identifier;
the evidence also reports actual qubit and depth metrics.

The current physical synthesis is bounded by the declared `max_input_qubits` and
`max_function_states`, as well as Bridge payload, QASM, qubit and depth limits.
Resource cost can grow rapidly with the number and precision of prepared fields.
Bridge stops after delivering the circuit artifact or expert construction inputs.
It does not execute the circuit or validate the problem result; hardware
validation is not part of the Bridge delivery contract. The user chooses the
simulator or provider, supplies the execution resources and validates the resulting behavior. See
[`examples/score_model_v2.py`](examples/score_model_v2.py) for a bounded circuit-delivery example.

Other operations can still be represented semantically. If any required operation lacks a certified implementation, Bridge returns exact `missing_capabilities` for expert construction instead of claiming a circuit.

Legacy family values such as `bounded_semantic_marking` remain accepted as compatibility labels. They do not choose the compiler, alter the generated circuit or promise support.

Legacy family labels remain accepted only as optional metadata:

```python
legacy_labeled_spec = {**spec, "family": "bounded_semantic_marking"}
```

The label does not select the compiler, alter the circuit or promise support.

## What It Exports

What is exposed depends on the delivery mode:

| Mode | Public artifact boundary |
|---|---|
| `generate()` | Circuit, loading guidance, measurement meaning, actual resources and construction evidence. No public IR or lowering details. |
| `build()` | Editable QASM/Qiskit artifact, public oracle contract, stable public IR summary, resources and digests. No reversible IR. |
| `prepare()` | Public construction contract, semantic requirements, capability gaps and design guidance. No private compiler plan. |
| `evaluate()` | Actual materialization evidence and conceptual alternatives. No private selection heuristics. |

The public `oracle_spec` never contains answer tables, private function rows or
winning candidates. A public profile value is an identifier and version only,
not an implementation disclosure.

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
2. Delivery mode and the legacy family label, only when supplied.
3. Construction verification and canonical materialization evidence.
4. Generated executable QASM/Qiskit content when requested.
5. Circuit policy and template-use status.
6. Digests.
7. Resource limits and warnings.
8. Reproducibility metadata.

Bridge Report is the public trust document for Bridge: it makes clear what was derived, what was preserved, what was warned about and which digests identify the exported artifacts.

For `use` and `build`, circuit-oriented targets return a circuit only when canonical QDSV materialization succeeds, together with formula/oracle digests and actual circuit metrics.

Bridge does not insert placeholder oracle comments and call them completed circuits. Incomplete specifications must use `expert_prepare` or add computable semantic inputs.

For `expert_prepare`, Bridge may intentionally return construction inputs instead of forcing a final circuit. This is useful when an expert wants to design a custom circuit with the correct semantic ingredients.

## Public Endpoints

The SDK calls the QDSV API:

- `GET /api/bridge/capabilities`
- `GET /api/bridge/families` (compatibility alias)
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

`client.capabilities()` is the recommended name for the informational catalog. `families()` and `/bridge/families` remain compatibility aliases. Developer Preview value-producing operations can be used without an API key and are limited by rate limits, payload limits and a demo quota per caller bucket.

## Resource And Multi-User Limits

QDSV Bridge accepts compact semantic problem specifications and small prepared numeric signal tables, not raw datasets.

Do not send:

- full CSV files;
- raw datasets;
- thousands of rows;
- sensitive records;
- training data;
- hardware execution requests.

Send:

- semantic `problem_spec` or bounded state space;
- finite state-space size;
- prepared signal or variable names;
- threshold decision goal or predicate supported by the current compiler;
- target format;
- qubit/depth limits;
- compact `prepared_candidates` containing only the bounded numeric signals required by the formula, when requesting a coherent circuit;
- or a canonical `problem_spec` containing the supported operations needed to construct the circuit.
- unsupported predicates may be sent to `expert_prepare`; they are not converted into circuits from precomputed satisfying states.

Public API minimum limits:

| Limit | Default |
|---|---:|
| Max spec payload | 64 KB |
| Max QASM / circuit artifact payload | 256 KB |
| Max compile time | 5 seconds |
| Max export time | 10 seconds |
| API key required for | Not required by default in Developer Preview |
| Monthly demo quota | 100 compilations/exports/reports per caller bucket |
| Raw data payloads | Not allowed; compact prepared numeric signals are allowed |
| Hardware execution | Not available from Bridge SDK |
| Semantic service boundary | 4096 finite candidates / 64 named signals |
| Compiler v1 coherent boundary | 16 candidates / 20 prepared-signal qubits |
| Default requested circuit ceiling | 256 qubits / depth 1,000,000 |

The semantic service boundary is not a circuit-size promise. Actual circuit resources depend on the complete operation graph, precision, registers, reversible arithmetic, ancillas and uncompute.

Default API rate limits may be configured by the QDSV deployment:

- `capabilities`: 60/minute (`families` uses the same limit as a compatibility alias)
- `validate`: 30/minute
- `compile`: 20/minute
- `explain`: 20/minute
- `export`: 10/minute
- `report`: 10/minute

Quotas, authentication requirements and rate limits are configurable by each
deployment. The public preview may apply different limits from a private or
partner deployment.

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

QDSV Bridge does not expose the private runtime, internal compilation or
optimization rules, private backend adapters, secrets or production
configuration. It also does not provide unrestricted circuit generation or
arbitrary Python execution.

Product principle:

```text
semantic problem specification
-> capability and resource validation
-> executable circuit materialization or expert inputs
-> auditable export
```

Not:

```text
any input -> arbitrary circuit
```

## Open SDK, Private Runtime

This repository contains the MIT-licensed Python client SDK, examples,
documentation and tests. It does not contain the private runtime, internal
compilation rules, private backend adapters, secrets or production configuration.

QDSV, QIntent and Qruba names and marks are project marks of their respective owners. The MIT License for this repository does not grant trademark rights.
