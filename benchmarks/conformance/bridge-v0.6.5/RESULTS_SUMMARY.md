# Results Summary

Run ID: `20260822T022921Z_bridge_conformance_v01_sdk065`

Target: `https://api.qdsv.cloud/api`

SDK: `0.6.5`

## Conformance

| Track | Result |
|---|---:|
| Bridge conformance cases | `10/10 PASS` |
| Output hashes verified | `21/21` |
| SDK unit tests | `41/41 PASS` |
| Documentation build | `PASS` |
| Clean wheel install | `PASS` |
| Independent third-party attestation | `NOT_EVALUATED` |

## Case Outcomes

| Case | Outcome | Evidence |
|---|---|---|
| `compound_predicate_power2` | `SUCCESS` | independent replay |
| `compound_predicate_data_variant` | `SUCCESS` | independent replay |
| `non_power_of_two_domain` | `SUCCESS` | independent replay |
| `sum_fields_affine` | `SUCCESS` | independent replay |
| `weighted_sum_affine` | `SUCCESS` | independent replay |
| `hierarchical_score_contractual` | `SUCCESS` | contractual |
| `invalid_candidate_identity` | `INVALID_SPEC` | contractual |
| `unsupported_operation` | `UNSUPPORTED` | contractual |
| `resource_guardrail` | `RESOURCE_LIMITED` | contractual |
| `deterministic_repeated_build` | `SUCCESS` | independent replay |

## Benchmark Evidence

| Benchmark | Result | Scope |
|---|---:|---|
| General semantic kernel | `36/36 PASS` | bounded semantic operations |
| ScoreModel | `16/16 PASS` | bounded ScoreModel configurations |
| Manual Qiskit common case | `semantic_accuracy = 1.0` | single controlled comparison case |

## Interpretation

These results support the claim that Bridge `0.6.5` can materialize and
validate bounded semantic programs across the tested public cases while keeping
resource limits and unsupported operations explicit.

They do not claim hardware execution, quantum advantage, production SLA,
unbounded scalability or independent third-party certification.
