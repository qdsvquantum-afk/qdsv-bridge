# QDSV Bridge Developer Preview

Current package version: `0.1.3`.

Lightweight Python SDK for **QDSV Bridge**, a controlled semantic compiler built on **QDSV (Quantum Declarative Semantic Value)** that turns supported problem-family specifications into problem-derived circuit materializations, QDSV IR, oracle specs, QASM/Qiskit artifacts, or expert construction inputs.

QDSV Bridge is not a template selector and not a free arbitrary circuit generator. It is a restricted semantic-to-circuit bridge for supported problem families. Its core rule is simple: **do not force the problem into a prefabricated circuit; derive the circuit or construction inputs from the semantic problem specification.**

QDSV Bridge does not force a problem into a prebuilt circuit template. It derives circuital artifacts from the semantic structure of the problem.

```text
problem family spec
-> family ontology validation
-> semantic ProblemSpec / IR
-> oracle specification
-> materialization policy
-> generated circuit artifact or expert construction inputs
```

The SDK is a client only. It does not include the private QDSV Runtime, CAP, backend selector, lowering internals, QuEST/Aer/IBM adapters, or advanced orchestration.

```bash
pip install qdsv-bridge
```

## Why This Exists

Traditional quantum workflows often start by asking users to choose a circuit, encoding, ansatz, or measurement pattern. That can force the data to adapt to a circuit.

QDSV Bridge starts from a controlled semantic family. The family defines what kind of problem is allowed, what concepts belong to it, what patterns are excluded, and what evidence must be produced. For users who need circuit ecosystems, Bridge derives a new circuit artifact from that semantic specification instead of asking the user to adapt the problem to a ready-made template. For expert constructors, Bridge can also return the key semantic inputs needed to design a custom circuit without forcing a final circuit.

For example, in signal classification:

```text
prepared signals
-> semantic_signal_classification
-> preserve signal geometry
-> oracle / IR / QASM blueprint
```

This is designed to avoid a fixed pattern such as:

```text
forced reduction -> angle encoding -> fixed ansatz -> fixed measurement
```


## Bridge Modes

QDSV Bridge is one SDK with multiple output depths. The modes do not change the core principle: the circuit, when delivered, is derived from the semantic problem specification.

| API | Commercial name | Intended user | What Bridge returns | Message |
| --- | --- | --- | --- | --- |
| `generate()` / `use` | Bridge Use | Basic user who wants to solve without designing circuits | A new problem-derived circuit artifact, simple explanation, information-loss risk, usage recommendation and ready-to-run example | No need to design the circuit; Bridge generates it from your problem. |
| `build()` / `build` | Bridge Build | Intermediate user who understands Qiskit, QASM or quantum workflows | A new problem-derived circuit artifact plus QASM/Qiskit, oracle spec, IR summary, preservation report, estimated qubits/depth and digests | Take this circuit generated from semantics and adjust or integrate it into your stack. |
| `prepare()` / `expert_prepare` | Bridge Expert Prepare | Expert constructor who wants to design a custom circuit | Validated family, ProblemSpec/IR, oracle spec, predicates, target state/goal, constraints, relevant variables, information-loss risk, encoding/measurement suggestions, estimated limits and evidence. It does not force a final circuit. | We give you the right inputs to design a circuit faithful to the problem. |
| `evaluate()` / `expert_evaluate` | Bridge Expert Evaluate | Expert evaluator who wants to compare QDSV materializations | Suggested QDSV circuit artifact, materialization variants, comparison and preservation report | Compare QDSV materializations and decide which one preserves the problem best. |

Python helpers:

```python
client.generate(spec)  # mode="use"
client.build(spec)     # mode="build"
client.prepare(spec)   # mode="expert_prepare"
client.evaluate(spec)  # mode="expert_evaluate"
```

Or pass the mode explicitly:

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
```

## Quick Start

```python
from qdsv_bridge import QDSVBridgeClient

client = QDSVBridgeClient()

spec = {
    "family": "semantic_signal_classification",
    "state_space": {
        "kind": "finite_candidates",
        "candidate_count": 300,
        "candidate_id": "eeg_window",
    },
    "signals": [
        "dwt_cD3_std_score",
        "std_score",
        "activity_score",
        "energy_score",
        "dwt_cD2_std_score",
        "complexity_score",
    ],
    "goal": {
        "kind": "binary_marking",
        "positive_state": "ictal",
    },
    "materialization_policy": {
        "preserve_signal_geometry": True,
        "avoid_fixed_ansatz": True,
        "avoid_forced_dimensionality_reduction": True,
        "report_information_loss": True,
    },
    "target": {
        "format": "qasm3",
        "backend_family": "qiskit",
    },
    "limits": {
        "max_qubits": 10,
        "max_depth": 300,
    },
}

result = client.build(spec)

print(result["status"])
print(result["bridge_mode"])
print(result["circuit"])
print(result["semantic_preservation_report"])
print(result["artifact"]["content"])
```

By default, `QDSVBridgeClient()` points to the public cloud API:

```text
https://api.qdsv.cloud/api
```

For the local/private Docker demo, use:

```python
client = QDSVBridgeClient.local()
```


## Examples by User Type

### Bridge Use: problem to generated circuit

```python
result = client.generate(spec)

print(result["circuit_origin"])      # qdsv_derived
print(result["circuit"]["status"])   # generated_from_semantic_spec
print(result["ready_to_run_example"]["kind"])
```

### Bridge Build: problem to QASM/Qiskit/oracle/IR

```python
result = client.build(spec)

print(result["artifact"]["format"])
print(result["editable_artifacts"]["oracle_spec"])
print(result["editable_artifacts"]["ir_summary"])
print(result["digests"])
```

### Bridge Expert: construction inputs and materialization comparison

```python
inputs = client.prepare(spec)
print(inputs["expert_inputs"]["encoding_suggestions"])
print(inputs["expert_inputs"]["measurement_suggestions"])

comparison = client.evaluate(spec)
print(comparison["materialization_variants"])
print(comparison["comparison"])
```

Every export response includes minimum traceability metadata:

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

## Public Endpoints

The SDK calls the QDSV API:

- `GET /api/bridge/families`
- `POST /api/bridge/validate`
- `POST /api/bridge/compile`
- `POST /api/bridge/explain`
- `POST /api/bridge/export`

Default cloud endpoint:

```python
client = QDSVBridgeClient(api_url="https://api.qdsv.cloud/api")
```

Local/private Docker endpoint:

```python
client = QDSVBridgeClient.local()
```

## Resource and Multi-User Limits

QDSV Bridge accepts compact semantic problem specifications, not raw datasets.

QDSV Bridge is not a bulk data processing SDK. It is designed to receive a bounded semantic specification of the problem and return circuit-oriented artifacts or expert construction inputs.

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
| --- | --- |
| Max spec payload | 64 KB |
| Max QASM / circuit artifact payload | 256 KB |
| Max compile time | 5 seconds |
| Max export time | 10 seconds |
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

Rate limits use `Authorization`, `x-api-key` or `x-license-key` when present; otherwise they fall back to IP plus SDK name. In the current public deployment, rate limiting is in-memory per API instance. If Cloud Run scales to multiple instances, the effective limit may multiply until a distributed rate-limit store is enabled.

The SDK itself is stateless and does not block multiple users. Multi-user control, quotas, API keys, license checks and history belong to the QDSV/Qruba API deployment, not to the local Python package.

Raw dataset payloads are rejected. Example:

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

## Supported Families

Developer Preview families:

- `bounded_semantic_marking`
- `semantic_signal_classification`
- `predicate_marking`
- `state_similarity`
- `combinatorial_relation`
- `distribution_sampling`

`bounded_semantic_marking` is the controlled fallback family. Use it when the problem is finite, bounded and semantic, but no specialized Bridge family exists yet. It is not a universal free-form mode: it still requires a bounded state space, declared goal, limits, excluded patterns and preservation reporting.

Each family has:

- ontology boundary;
- allowed state-space kinds;
- allowed goal kinds;
- allowed semantic operations;
- excluded patterns;
- public limits;
- export targets;
- evidence / digest contract.

### Fallback family example

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

print(result["family"])          # bounded_semantic_marking
print(result["circuit_origin"])  # qdsv_derived
print(result["warnings"])        # includes fallback-family guidance
```

## What It Exports

Depending on `target.format`, QDSV Bridge can export:

- `problem_spec`
- `ir`
- `oracle_spec`
- `qasm2`
- `qasm3`
- `qiskit_blueprint`

For `use` and `build`, circuit-oriented targets return a circuit artifact derived from the semantic spec, with explicit QDSV oracle/digest information and preservation metadata. In Developer Preview, some targets are returned as integration blueprints with semantic oracle insertion points so external platforms can inspect, execute, optimize or complete the materialization safely.

For `expert_prepare`, Bridge may intentionally return construction inputs instead of forcing a final circuit. This is useful when an expert wants to design a custom circuit with the correct semantic ingredients.

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

The product principle is:

```text
controlled semantic family
-> problem-derived circuit materialization or expert inputs
-> auditable export
```

Not:

```text
any input
-> arbitrary circuit
```

## Open SDK, Private Runtime

This repository is open-core:

- **Open under MIT:** Python client SDK, examples, docs and tests.
- **Not included:** QDSV Runtime, ontology compiler internals, CAP, lowering, advanced materialization, backend adapters, private endpoints, secrets or production configuration.

QDSV, QIntent and Qruba names and marks are project marks of their respective owners. The MIT License for this repository does not grant trademark rights.
