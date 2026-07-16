# Changelog

Notable public changes to QDSV Bridge are documented here. The project is a Developer Preview and has not reached a stable `1.0` contract.

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
- Adds public `importance` and `priority` terminology, contextual adjustments, normalization, penalties and comparison decisions.
- Separates semantic admission limits from the resources of the materialized circuit.

## Earlier Releases

See the complete [release notes](docs/release_notes.rst) for versions `0.1.5` through `0.4.3`.
