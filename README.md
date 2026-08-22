# QDSV Bridge

[![PyPI](https://img.shields.io/pypi/v/qdsv-bridge.svg)](https://pypi.org/project/qdsv-bridge/)
[![Python](https://img.shields.io/pypi/pyversions/qdsv-bridge.svg)](https://pypi.org/project/qdsv-bridge/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/qdsvquantum-afk/qdsv-bridge/blob/main/LICENSE)
[![Status](https://img.shields.io/badge/status-public%20preview-0ea5e9.svg)](#current-availability-and-operational-boundaries)
[![Qiskit Ecosystem](https://qisk.it/e-e8734f93)](https://www.ibm.com/quantum/ecosystem)

Source/package version: `0.6.5`. See the PyPI badge for publication status.

## From Business Meaning To Quantum Artifacts

QDSV Bridge transforms bounded business rules, prepared data and functional
objectives into semantically validated and optimized logical quantum artifacts.
It is QDSV's interoperability layer for today's circuit-based quantum
ecosystem: the semantic problem remains primary, and logical circuits are
derived when the destination requires a circuit artifact.

QDSV Bridge is domain-agnostic within its certified semantic operation set. It
does not choose a circuit from a fixed catalog of industry templates. It
compiles bounded semantic programs assembled from composable numeric and
logical operations, including general predicates and ScoreModel v2. Users do
not need to design gates, quantum registers, ancillas, reversible cleanup or a
framework-specific quantum model. The user describes what the problem means;
Bridge derives and verifies its quantum realization.

> **The circuit is a delivery format, not the source of truth.**

The semantic problem specification remains canonical while Bridge derives,
validates and documents:

- the supported reversible construction, registers, controls and cleanup;
- an immutable canonical logical circuit;
- an optional exact logical optimization linked to its parent by digest;
- semantic-equivalence and no-regression validation;
- inspectable OpenQASM/Qiskit artifacts, resources and construction evidence;
- a traceable handoff for downstream simulator or hardware execution.

The user provides bounded candidates, prepared numeric inputs, functional
rules, thresholds, priorities and objectives. Bridge derives the supported
quantum construction without requiring the user to design it. It never
fabricates an unsupported construction or embeds precomputed answers when a
request cannot be materialized.

- [Documentation](https://qdsvquantum-afk.github.io/qdsv-bridge/)
- [PyPI](https://pypi.org/project/qdsv-bridge/)
- [Source](https://github.com/qdsvquantum-afk/qdsv-bridge)
- [Conformance evidence](benchmarks/conformance/bridge-v0.6.5)

## Business-First Quickstart

Start with the candidates and the rule they must satisfy. This example asks
Bridge to mark suppliers whose quality is at least `700` and whose compliance
flag is `1`:

```python
from qdsv_bridge import (
    QDSVBridgeClient,
    build_predicate_spec,
    select_recommended_artifact,
)

suppliers = [
    {"candidate_index": 0, "supplier_id": 101, "quality": 820, "compliance": 1},
    {"candidate_index": 1, "supplier_id": 102, "quality": 680, "compliance": 1},
    {"candidate_index": 2, "supplier_id": 103, "quality": 760, "compliance": 0},
]

business_rule = {
    "op": "and",
    "args": [
        {
            "op": "gte",
            "left": {"op": "field", "name": "quality"},
            "right": {"op": "const", "value": 700},
        },
        {
            "op": "eq",
            "left": {"op": "field", "name": "compliance"},
            "right": {"op": "const", "value": 1},
        },
    ],
}

spec = build_predicate_spec(rows=suppliers, predicate=business_rule)
result = QDSVBridgeClient().generate(spec)
recommended = select_recommended_artifact(result)

print(result["status"])
print(result["recommended_artifact_role"])
print(recommended["format"])
print(result["construction_verification"])
```

The user does not provide gates, registers, ancillas, reversible cleanup or
expected answers. `candidate_index` is the stable circuit-domain identity;
`supplier_id` remains the organization's business reference.
`build_predicate_spec()` preserves both, normalizes the declared rule without
evaluating it, and applies portable defaults for the logical artifact. Advanced
users can override those defaults through its typed parameters.

The successful response can contain:

- an immutable canonical logical artifact;
- an accepted optimized child artifact when exact validation and no-regression
  checks pass;
- the recommended artifact role and inspectable OpenQASM/Qiskit content;
- construction verification, resource metrics, digests and traceability;
- a handoff contract for downstream simulation or hardware execution.

The complete runnable version is
[`examples/compound_business_predicate.py`](examples/compound_business_predicate.py).

## Conformance And Evidence

Bridge `0.6.5` includes a public conformance evidence package under
[`benchmarks/conformance/bridge-v0.6.5`](benchmarks/conformance/bridge-v0.6.5).
It publishes the reduced review layer for QDSV Bridge Conformance v0.1:
normative contract, profiles, schemas, public fixtures, runner scripts,
summarized evidence and benchmark manifests.

The public package reports:

- Bridge conformance: `10/10 PASS`;
- general semantic kernel benchmark: `36/36 PASS`;
- ScoreModel benchmark: `16/16 PASS`;
- SDK unit tests: `41/41 PASS`;
- clean wheel installation and Quickstart verification: `PASS`.

The package does not include private compiler internals, formulas, production
configuration, credentials, raw logs, notebooks or hardware evidence. Hardware
execution and third-party attestation are separate downstream validation
tracks.

## How Bridge Differs From Quantum Synthesis Platforms

Most quantum-development platforms reduce the work required to construct a
circuit but still expect the user to define or review a quantum program.
Bridge starts one layer earlier: with the bounded problem and its functional
meaning.

The distinction is not merely fewer lines of code. It is a different user
responsibility:

| Dimension | Classiq | QDSV Bridge |
|---|---|---|
| Starting point | An explicit Qmod quantum model, written manually or with AI assistance | Prepared business data and a supported semantic rule |
| User thinks about | Quantum functions, variables, model behavior and synthesis | Candidates, values, criteria, thresholds, priorities and outcomes |
| Canonical source | The explicit quantum model | The semantic problem specification |
| Quantum-specific user work | Define or review the quantum model | No quantum program design for bounded programs expressible through the certified semantic operation set |
| Reversible realization | Synthesized from the Qmod model | Derived from the semantic rule and linked to semantic digests |
| Optimization | Broad synthesis, including hardware-aware options | Exact target-independent logical optimization with replay and no-regression acceptance |
| Execution | Integrated simulator and provider workflows | Deliberately separated through Qiskit, Qruba or QDSV Runtime/HSP |
| Primary strength | Broad quantum-engineering and execution platform | Higher problem-level abstraction and less explicit quantum engineering |

Classiq provides a high-level environment for designing and synthesizing
quantum programs. For bounded semantic programs expressible through Bridge's
certified composable operation graph, QDSV Bridge removes quantum-program
design from the end-user workflow.

Classiq provides a broader integrated quantum-development environment. Bridge
provides an earlier entry point for organizations that want to begin with the
problem rather than with a quantum program. The comparison above describes the
public workflows and architectural responsibility boundary; it is not a claim
of universal circuit-performance superiority. See the
[Classiq documentation](https://docs.classiq.io/) for its current public
workflow.

## Installation

Install the client:

```bash
pip install qdsv-bridge
```

Install the optional Qiskit inspection dependencies:

```bash
pip install "qdsv-bridge[qiskit]"
```

The Qiskit extra is capped at `qiskit>=2,<3` to preserve compatibility with the
currently tested Qiskit major version. The Public Preview does not require an
API key.

## Current Availability And Operational Boundaries

QDSV Bridge is publicly available through PyPI and the Qiskit Ecosystem for
bounded real-world validation. Its certified semantic operations and deployment
options continue to expand under the Public Preview contract.

- Bridge supports bounded compositions of certified semantic operations, not a
  fixed catalog of industries or use cases. Public paths include general
  predicates and ScoreModel v2.
- Practical limits are determined by certified reversible lowering and
  materialized resource limits, not by a fixed catalog of industries or use
  cases. Relevant resources include candidate count, numeric precision,
  expression complexity, qubits, ancillas, circuit depth and artifact size.
  Bridge does not accept every arbitrary business or quantum program.
- The public service is provided without an SLA and may change or be
  temporarily unavailable before `1.0`.
- Bridge does not execute on a simulator or QPU, select a provider, manage
  credentials, route to hardware, mitigate noise or interpret experiments.
- Do not send confidential, regulated or secret data to the public service.

Bridge validates the semantic-to-circuit construction path and reports the
resources required by the generated artifact. It can derive an exact,
target-independent logical optimization and recommend it only when contractual
replay passes and protected logical metrics do not regress. The canonical
artifact is never replaced silently.

The public SDK supports Python `3.9` and later. Before `1.0`, minor releases may
introduce contract changes; deprecations and migration notes are recorded in
the [changelog](https://github.com/qdsvquantum-afk/qdsv-bridge/blob/main/CHANGELOG.md).

## Technical Workflows

Use `build_predicate_spec()` for explicit public predicates with nested boolean
composition and field-to-field comparisons. Use
`build_score_expression_spec()` when a numeric expression must be compared
with a declared threshold, and `build_score_model_spec()` for flat or
hierarchical ScoreModel v2 decisions. These helpers normalize public semantic
inputs without calculating scores, decisions or expected answers.

| Public input | SDK constructor | Examples |
|---|---|---|
| Boolean rule | `build_predicate_spec()` | comparisons, `and`, `or`, `xor`, `not`, null checks |
| Numeric expression plus cutoff | `build_score_expression_spec()` | rounding, sums, means, weighted sums |
| Multi-criteria decision | `build_score_model_spec()` | flat terms or hierarchical blocks |

`weighted_sum` accepts explicit `values` and same-length `weights`. Unary
operations accept `arg`, `value`, `operand` or a one-item `args` list and are
canonicalized to one stable operand form. Every request remains bounded and
resource checked; a valid semantic program can still be rejected if its
materialized artifact exceeds the active limits.

Use the lower-level specification contract only when you need to freeze
artifact format, backend family, evidence or resource limits. In every path,
do not include labels, expected decisions or precomputed predicate results in
the input rows.

When materialization succeeds, `generate()` returns the canonical circuit and
loading guidance. Bridge attempts the public `qiskit_structural_exact_v1`
logical optimization by default. `select_recommended_artifact()` returns the
accepted optimized artifact when available and otherwise returns the canonical
artifact.

The optimization is exact and target-independent. It does not perform layout,
routing, scheduling, calibration-aware selection, noise suppression,
mitigation or hardware execution. Those operations remain downstream in
Qiskit, Qruba or QDSV Runtime/HSP.

For a minimal multi-criteria ScoreModel example, run
[`examples/score_model_v2.py`](examples/score_model_v2.py). Prepared metrics and
the cutoff use one declared scale, and `priority` represents a domain priority,
not the position of a criterion. The SDK example does not reproduce private
ScoreModel aggregation or compiler rules.

## Technical Reference

The detailed contracts remain versioned in the documentation:

- [Public SDK contract](https://qdsvquantum-afk.github.io/qdsv-bridge/reference/public_contract.html): delivery modes, outputs, errors, limits, privacy, reports and compatibility.
- [Conformance and release identity](https://qdsvquantum-afk.github.io/qdsv-bridge/reference/conformance.html): normative outcomes, validated runtime identities, suite evidence and reproducibility boundaries.
- [Migration to 0.6.5](https://qdsvquantum-afk.github.io/qdsv-bridge/migration_0_6_5.html): compatibility, contract and evidence changes from 0.6.4.
- [Problem-first and similarity boundaries](https://qdsvquantum-afk.github.io/qdsv-bridge/explanations/index.html): prepared metrics, declared operations and construction guarantees.
- [Canonical and optimized artifacts](https://qdsvquantum-afk.github.io/qdsv-bridge/how_to/logical_artifacts.html): profiles, lineage, validation and recommendation.
- [IBM/Qiskit handoff](https://qdsvquantum-afk.github.io/qdsv-bridge/integrations/ibm_quantum.html): the boundary between logical artifacts and physical execution.
- [Examples and tutorials](https://qdsvquantum-afk.github.io/qdsv-bridge/tutorials/index.html): first workflow, ScoreModel and inspectable artifacts.

Installed clients can inspect the exact public release identity without
contacting the service:

```python
from qdsv_bridge import get_release_manifest

manifest = get_release_manifest()
print(manifest["contracts"])
print(manifest["conformance"])
```

The manifest identifies the contract and the runtime builds used for release
validation. It is evidence about those frozen builds, not a claim that a
mutable public endpoint will always serve the same deployment.

## Support And Security

- General questions and defects: [GitHub Issues](https://github.com/qdsvquantum-afk/qdsv-bridge/issues)
- Sensitive security reports: follow [SECURITY.md](https://github.com/qdsvquantum-afk/qdsv-bridge/blob/main/SECURITY.md); do not open a public issue
- Release history: [CHANGELOG.md](https://github.com/qdsvquantum-afk/qdsv-bridge/blob/main/CHANGELOG.md)
- Roadmap: [ROADMAP.md](https://github.com/qdsvquantum-afk/qdsv-bridge/blob/main/ROADMAP.md)

## License

The client SDK, examples, documentation and tests in this repository are licensed under the [MIT License](https://github.com/qdsvquantum-afk/qdsv-bridge/blob/main/LICENSE).

QDSV, QIntent and Qruba names and marks belong to their respective owners. The MIT License does not grant trademark rights.
