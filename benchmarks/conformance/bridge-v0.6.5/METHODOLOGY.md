# Methodology

QDSV Bridge Conformance v0.1 evaluates whether the public SDK and service
preserve the declared semantic problem through construction of logical quantum
artifacts.

## Principles

- The semantic problem specification is the source of truth.
- Circuits are derived artifacts, not the definition of the problem.
- Expected answers are stored separately and are not sent to Bridge.
- Resource limits and unsupported operations are reported as contract outcomes,
  not relabeled as semantic failures.
- Hardware execution is outside this Bridge conformance track.

## Evidence Layers

The report separates four layers:

- `semantic`: exact replay or contractual semantic evidence.
- `logical`: canonical and optimized logical artifact resources.
- `normalized`: common transpilation benchmark track, kept separate.
- `physical`: downstream hardware or backend evidence, not included here.

## Conformance Outcomes

The suite accepts these public outcomes:

- `SUCCESS`
- `INVALID_SPEC`
- `UNSUPPORTED`
- `RESOURCE_LIMITED`

Passing conformance means the observed outcome matches the declared contract
for that case. For example, an intentionally unsupported operation passes only
when Bridge rejects it with the expected unsupported-operation contract.

## Scope Boundary

This package does not certify production uptime, hardware execution, quantum
advantage, noise mitigation, routing, backend selection or third-party
attestation. It evaluates the public semantic-to-logical-artifact boundary for
SDK `0.6.5`.
