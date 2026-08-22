# QDSV Bridge Minimum Normative Contract v0.1

Status: candidate specification for the Bridge Public Preview.

This document defines observable behavior. It does not define or disclose the
private QDSV compiler implementation, private score formulas, planner
heuristics, or backend credentials.

The terms MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are normative.

## 1. Version identity

An evidence record MUST identify the SDK package, public contract, and runtime
implementation independently. A mutable service MUST NOT be identified only by
the client SDK version.

Post-release runtime behavior MUST NOT be attributed retrospectively to an
older source tag. Rebuilt local distributions with hashes different from the
published artifacts MUST be labeled local builds.

## 2. Semantic authority

The bounded problem specification is the semantic source of truth. A circuit
is a derived delivery artifact.

Executable compiler-v2 paths MUST declare `qdsv_operation_compiler.v2` as
their compiler authority. An implementation MUST fail closed when a complete
and verified realization is unavailable.

Expected answers, labels, winners, candidate scores, or predicate truth tables
MUST NOT be accepted as construction inputs for a quantum artifact. Observable
evidence MUST declare `answer_precomputed = false` or an equivalent protected
invariant.

Prepared metrics MAY be supplied as inputs. If a metric was computed before
Bridge, Bridge MUST NOT claim that the circuit computed that upstream metric.

## 3. Canonical semantic program

A successfully compiled request MUST expose stable semantic and program
digests. The typed operation graph MUST contain only registered operations with
declared arity, input type, output type, numeric policy, and error policy.

Canonicalization MUST be deterministic for the same normalized specification,
contract versions, and runtime build. Process-local gate names MUST NOT alter
canonical QASM or lineage digests.

## 4. Reversible realization

For reversible materialization profiles, the canonical artifact MUST:

- preserve the encoded candidate input;
- compute the declared result in the result register;
- return temporary work qubits to zero;
- leave no residual work entanglement;
- avoid embedding a precomputed answer table.

Invalid encoded states outside a bounded candidate domain MUST be rejected,
flagged, or mapped to an explicitly safe unmarked result. They MUST NOT be
counted as valid candidates or silently converted into a semantic mismatch for
valid candidates.

## 5. Artifacts and lineage

The canonical logical artifact MUST remain immutable. An optimized logical
artifact MUST identify its canonical parent by digest and MUST be recommended
only after exact semantic validation and the declared no-regression policy.

Artifact format, role, digest, delivery mode, construction verification, and
resource metrics MUST be explicit. A metadata-only or downloadable delivery
MUST NOT be reported as an inline artifact.

## 6. Outcomes

Conformance and operational outcome MUST be reported separately.

Allowed conformance statuses:

- `PASS`
- `FAIL`
- `NOT_EVALUATED`

Required outcome vocabulary:

- `SUCCESS`
- `SEMANTIC_FAIL`
- `CONTRACT_FAIL`
- `RESOURCE_LIMITED`
- `UNSUPPORTED`
- `INVALID_SPEC`
- `NOT_APPLICABLE`
- `TRANSPORT_ERROR`

A resource limit or unsupported operation MUST NOT be reported as semantic
failure. An invalid user specification MUST be distinguished from a valid
specification whose materialization exceeds active limits.

## 7. Evidence levels

Evidence MUST state the strongest completed level:

- `CONTRACTUAL`: service-declared contract checks only.
- `INDEPENDENT_REPLAY`: an external runner verified the canonical artifact.
- `HARDWARE_CONFIRMED`: separately registered downstream physical evidence.

Bridge itself does not claim hardware confirmation merely by producing a
logical artifact.

## 8. Reproducibility

Each conformance run MUST record versions, commits when available, published
package hashes, runtime identity, fixture hashes, target URL without secrets,
configuration, seeds, results, and output hashes.

Secrets, confidential data, `.env` files, tokens, and private compiler source
MUST NOT be copied into a public conformance bundle.

## 9. Profiles

An operation is conformant only against an explicit profile. Non-applicable
requirements MUST be marked `NOT_APPLICABLE`, not silently omitted.

The initial profiles are defined in `conformance-profiles-v0.1.json`.

