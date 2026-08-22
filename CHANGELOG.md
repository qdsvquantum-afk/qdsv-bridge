# Changelog

Notable public changes to QDSV Bridge are documented here. The project is a conformance-tested Public Preview and has not reached a stable `1.0` contract or an SLA.

## Unreleased

## 0.6.5

- Freezes the public Bridge and operation-compiler v2 contract identities used by the post-0.6.4 logical materializer.
- Packages a machine-readable release manifest with validated Docker and Cloud Run identities, protected runtime-file hashes and explicit product boundaries.
- Publishes the matching conformance contract and evidence identity without placing the external test suite or private compiler in the SDK repository.
- Records bounded regression evidence for 36 general-kernel configurations and 16 ScoreModel configurations, while keeping resource comparisons explicitly case-specific.
- Adds a migration guide from 0.6.4 and distinguishes owner clean-room reproduction from independent third-party validation.
- Preserves all 0.6.4 public builders and artifact-selection behavior; no supported call-site migration is required.

## 0.6.4

- Canonicalizes process-local OpenQASM gate identifiers before artifact hashing so repeated builds preserve byte-identical QASM and stable lineage digests.
- Separates `semantic_oracle_digest` from the transport-linked `oracle_digest` while keeping both traceable to the same canonical construction.
- Adds external regression coverage for repeated canonical and optimized builds, exact truth tables, candidate identity and clean work ancillas.
- Fixes unary public-expression normalization so logical, null and rounding operations use the canonical single-operand contract.
- Adds outcome-blind builders for numeric threshold expressions and flat or hierarchical ScoreModel v2 inputs.
- Defines an unambiguous public `weighted_sum` shape and exposes per-operation construction routes through capabilities.
- Keeps semantically valid but oversized realizations classified as resource dependent rather than input-contract failures.

## 0.6.3

- Clarifies that Bridge is domain-agnostic within its certified semantic operation set rather than limited to a fixed catalog of industries or business templates.
- Documents general predicates and ScoreModel v2 as composable public paths while preserving explicit operation-coverage and no-bypass requirements.
- Reframes practical limits around certified reversible lowering and materialized resources without expanding the public compiler contract or exposing private implementation rules.

## 0.6.2

- Moves QDSV Bridge from Developer Preview to Public Preview for bounded real-world validation while preserving explicit pre-`1.0`, resource and SLA boundaries.
- Reorganizes the package landing page around the problem-first user journey and moves detailed delivery, outcome, privacy, compatibility and handoff contracts into versioned documentation.
- Adds an executable README Quickstart regression test that preserves circuit-domain identity separately from the user's business reference.
- Updates package metadata from alpha to beta without changing Bridge's logical-artifact boundary or claiming simulator, provider or QPU execution.

## 0.6.1

- Lets reproducible workflows freeze the public logical-optimization contract through `build_predicate_spec(logical_optimization=...)`.
- Preserves server-side validation of the versioned optimization mode, profile and acceptance policy without exposing custom passes or physical-backend settings.

## 0.6.0

- Preserves the canonical ideal artifact while optionally delivering a separately identified exact logical optimization.
- Adds the frozen target-independent `qiskit_structural_exact_v1` profile and `pareto_no_regression_v1` acceptance policy.
- Adds full prepared-state equivalence, register and measurement preservation, valid-domain checks, raw/QPY/structural digests and before/after logical metrics.
- Adds bounded isolated optimization with explicit timeout, memory, validation and fallback states.
- Separates materialization from inline delivery so an accepted optimized artifact may be delivered when the canonical representation exceeds the inline limit.
- Adds `select_recommended_artifact()` for basic users without changing the meaning of `result["artifact"]`.
- Keeps backend selection, layout, routing, scheduling, noise suppression, mitigation and QPU execution outside Bridge.

## 0.5.4

- Adds `build_predicate_spec()` for bounded public predicates with nested `and`, `or` and `xor` composition.
- Supports field-to-field comparisons without routing business rules through ScoreModel or exposing private aggregation mechanics.
- Derives candidate identity from stable row order and never evaluates the predicate or adds expected answers in the SDK.
- Adds a runnable compound supplier-eligibility example and regression tests for deterministic, outcome-blind construction.

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
