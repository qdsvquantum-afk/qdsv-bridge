# QDSV Bridge Conformance Report

Run: `20260822T022921Z_bridge_conformance_v01_sdk065`
Target: `https://api.qdsv.cloud/api`
SDK: `0.6.5`

- PASS: 10
- FAIL: 0
- NOT_EVALUATED: 0

| Case | Conformance | Outcome | Evidence |
|---|---|---|---|
| compound_predicate_power2 | PASS | SUCCESS | INDEPENDENT_REPLAY |
| compound_predicate_data_variant | PASS | SUCCESS | INDEPENDENT_REPLAY |
| non_power_of_two_domain | PASS | SUCCESS | INDEPENDENT_REPLAY |
| sum_fields_affine | PASS | SUCCESS | INDEPENDENT_REPLAY |
| weighted_sum_affine | PASS | SUCCESS | INDEPENDENT_REPLAY |
| hierarchical_score_contractual | PASS | SUCCESS | CONTRACTUAL |
| invalid_candidate_identity | PASS | INVALID_SPEC | CONTRACTUAL |
| unsupported_operation | PASS | UNSUPPORTED | CONTRACTUAL |
| resource_guardrail | PASS | RESOURCE_LIMITED | CONTRACTUAL |
| deterministic_repeated_build | PASS | SUCCESS | INDEPENDENT_REPLAY |

## Profile coverage

| Profile | Status | Cases |
|---|---|---:|
| semantic_compile | PASS | 8 |
| reversible_materialization | PASS | 7 |
| canonical_artifact | PASS | 7 |
| optimized_logical_artifact | PASS | 1 |
| independent_replay | PASS | 5 |
| specialized_runtime | NOT_EVALUATED | 0 |
| hardware_handoff | NOT_EVALUATED | 0 |

## Omissions

| Scope | Status | Reason |
|---|---|---|
| specialized_runtime | NOT_EVALUATED | Bridge logical conformance does not invoke a specialized runtime. |
| hardware_handoff | NOT_EVALUATED | Hardware submission is outside Bridge and requires a separate downstream profile. |

Expected outcomes were stored separately and were not sent to Bridge.
Resource and support outcomes are not classified as semantic failures.
