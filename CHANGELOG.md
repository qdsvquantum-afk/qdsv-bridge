# Changelog

Notable public changes to QDSV Bridge are documented here. The project is a Developer Preview and has not reached a stable `1.0` contract.

## 0.5.3

- Adds a minimal public ScoreModel example using prepared metrics, a shared declared scale and the high-level `generate()` contract.
- Clarifies that `priority` is a domain parameter rather than criterion order or execution precedence.
- Keeps private ScoreModel aggregation and compiler rules outside the public SDK documentation and adds regression coverage for that boundary.

## 0.5.2

- Adds a stable backend-neutral circuit realization package linked to the canonical semantic, quantum and reversible-plan identities.
- Separates ideal circuit construction evidence from target-specific readiness, optimization, mitigation and provider execution.
- Adds an explicit hardware handoff contract: Bridge delivers the canonical ideal logical circuit, while managed IBM execution belongs to Runtime/HSP or an equivalent user-controlled physical workflow.
- Keeps unavailable ideal replay evidence explicit and removes private artifact locations from public target summaries.

## 0.5.1

- Reorganizes the package README around installation, delivery modes, outputs, limits and support.
- Clarifies conditional circuit delivery, `evaluate()` behavior and the `qiskit_blueprint` artifact.
- Adds tested compatibility, privacy, versioning, error-handling and support guidance.
- Moves detailed compiler and ScoreModel discussion out of the package landing page.

## 0.5.0

- Routes the public bounded expression catalog through the shared canonical QDSV operation compiler.
- Adds a general bounded reversible circuit realization path with resource-aware optimizations derived from the same canonical program.
- Adds exact finite-domain preparation and explicit compute-mark-uncompute evidence.
- Publishes circuit-generation and QASM-load evidence while preserving explicit resource rejection.

## 0.4.4

- Narrows Bridge to circuit delivery and expert construction artifacts.
- Rejects unsupported goals instead of silently substituting another intent.
- Corrects `prepare()` so it requests expert construction evidence rather than a final circuit.

## 0.4.0

- Adds canonical ScoreModel v2 delivery for bounded flat and hierarchical decisions.
- Adds public `importance` and `priority` terminology, contextual adjustments, bounded score handling, penalties and comparison decisions while keeping aggregation internals private.
- Separates semantic admission limits from the resources of the materialized circuit.

## Earlier Releases

See the complete [release notes](docs/release_notes.rst) for versions `0.1.5` through `0.4.3`.
