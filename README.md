# QDSV Bridge Developer Preview

Lightweight Python SDK for **QDSV Bridge**, a controlled semantic compiler that turns supported problem-family specifications into QDSV IR, oracle specs, QASM blueprints, or integration-ready circuit scaffolds.

QDSV Bridge is not a free circuit generator. It is a restricted semantic-to-circuit bridge for supported problem families.

```text
problem family spec
-> family ontology validation
-> semantic ProblemSpec / IR
-> oracle specification
-> materialization policy
-> QASM / Qiskit blueprint when the target requires circuits
```

The SDK is a client only. It does not include the private QDSV Runtime, CAP, backend selector, lowering internals, QuEST/Aer/IBM adapters, or advanced orchestration.

```bash
pip install qdsv-bridge
```

## Why This Exists

Traditional quantum workflows often start by asking users to choose a circuit, encoding, ansatz, or measurement pattern. That can force the data to adapt to a circuit.

QDSV Bridge starts from a controlled semantic family. The family defines what kind of problem is allowed, what concepts belong to it, what patterns are excluded, and what evidence must be produced. Circuit materialization is only one possible export when another platform requires it.

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

result = client.export(spec)

print(result["status"])
print(result["semantic_preservation_report"])
print(result["artifact"]["content"])
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

## Supported Families

Developer Preview families:

- `semantic_signal_classification`
- `predicate_marking`
- `state_similarity`
- `combinatorial_relation`
- `distribution_sampling`

Each family has:

- ontology boundary;
- allowed state-space kinds;
- allowed goal kinds;
- allowed semantic operations;
- excluded patterns;
- public limits;
- export targets;
- evidence / digest contract.

## What It Exports

Depending on `target.format`, QDSV Bridge can export:

- `problem_spec`
- `ir`
- `oracle_spec`
- `qasm2`
- `qasm3`
- `qiskit_blueprint`

QASM outputs are bridge blueprints with explicit semantic oracle insertion points and QDSV digests. External platforms should inspect the returned preservation report, qubit/depth limits and oracle digest before executing or optimizing the generated artifact.

## Important Boundaries

QDSV Bridge does not expose:

- QDSV Runtime internals;
- CAP internals;
- backend selection heuristics;
- private QuEST/Aer/IBM adapters;
- native lowering internals;
- unrestricted circuit generation;
- arbitrary Python execution;
- user-supplied free circuits as family contracts.

The product principle is:

```text
controlled semantic family
-> flexible materialization
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
