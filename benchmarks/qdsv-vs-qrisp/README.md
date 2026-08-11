# QDSV Bridge vs Qrisp: problem-to-circuit benchmark

This benchmark evaluates what a user obtains when starting from the same public business problem and using each platform's public interfaces to produce a verifiable logical quantum artifact. It is not a benchmark of predesigned circuits, hardware execution, noise mitigation, or backend-specific transpilation.

The benchmark begins with business semantics, not with a pre-designed quantum circuit.

The primary result is the controlled `budget_value_8` experiment (`v20.1`). A complementary comparator-diagnostics track (`v19`) records where the evaluated native Qrisp construction completed or did not complete under frozen operational budgets. The two tracks answer different questions and are reported separately.

## Why Qrisp

Qrisp was selected because it is open source, high level, locally reproducible, able to export into the Qiskit ecosystem, and sufficiently expressive to implement the tested business predicate transparently through public APIs. It therefore provides a more reproducible comparison for this experiment than a platform requiring remote synthesis authorization.

Selection does not imply that Qrisp and QDSV have identical product scope. QDSV Bridge accepts a problem-oriented semantic specification and delegates circuit realization to its materializer. In the evaluated Qrisp path, a technical user translates the same rule into native quantum-programming constructs.

## Primary experiment

The frozen public rule for `budget_value_8` combines two comparisons over eight supplier candidates. Both platforms receive the same public data and predicate meaning. Expected answers are frozen separately and are not passed to either construction path.

The experiment uses:

- QDSV Bridge `0.6.1` and Qrisp `0.9.6`;
- Python `3.12.13`, Qiskit `2.5.1`, and Qiskit Aer `0.17.2`;
- 8,192 replay shots with seed `20260805` and Aer matrix-product-state simulation;
- a common external normalization to `rz`, `sx`, `x`, and `cx`, with Qiskit optimization level 3;
- resource comparison only after both artifacts satisfy the same sampled semantic contract.

See [methodology.md](methodology.md) and [problem_expression.md](problem_expression.md) for the complete experimental boundary.

## Results

### Correctness gate

Both artifacts were `sampled_consistent` under the common 8,192-shot replay:

| Platform artifact | Mismatch probability | Invalid-domain probability | Dirty-ancilla probability |
|---|---:|---:|---:|
| QDSV canonical | 0 | 0 | 0 |
| Qrisp native | 0 | 0 | 0 |

This establishes sampled consistency under the frozen protocol. It is not a claim of exhaustive mathematical equivalence or hardware performance.

### Native artifacts

| Metric | QDSV canonical | Qrisp native | QDSV reduction |
|---|---:|---:|---:|
| Qubits | 11 | 47 | 76.60% |
| Depth | 542 | 4,784 | 88.67% |
| Operations | 794 | 9,145 | 91.32% |
| Observed construction latency | 6.19 s | 13.48 s | 54.08% |

Construction latency is an observed end-to-end measurement, not a pure compiler-speed comparison: QDSV includes a remote Bridge request, while Qrisp constructs and compiles locally.

### Common normalized artifacts

| Metric | QDSV canonical | Qrisp native | QDSV reduction |
|---|---:|---:|---:|
| Qubits | 11 | 47 | 76.60% |
| Depth | 7,518 | 26,322 | 71.44% |
| Operations | 9,067 | 42,596 | 78.71% |
| CX | 3,997 | 16,858 | 76.29% |
| One-qubit operations | 5,070 | 25,738 | 80.30% |

The normalized track is the primary resource comparison because both input artifacts pass through the same external transpilation policy.

### Additional QDSV logical-optimization track

Bridge also returned an independently identified optimized logical artifact: 11 qubits, depth 368, and 494 operations, compared with depth 542 and 794 operations in the canonical artifact. Internal validation reported prepared-state equivalence, fidelity approximately `0.99999999999935`, zero invalid-domain probability, and a passed semantic validation.

This optimized artifact is reported as an additional Bridge capability. It is not substituted for the canonical QDSV artifact in the neutral primary comparison.

## Responsibility boundary

Both tracks share public business data, predicate meaning, frozen expectations, replay, and neutral normalization. Their construction implementations are independent and use only their respective public interfaces.

| Task | QDSV Bridge | Evaluated native Qrisp path |
|---|---|---|
| Provide business data | User | User |
| Define the business rule | User | User |
| Select a quantum representation | Bridge, automatic | Technical user |
| Define registers and fields | Bridge, automatic | Technical user declares them; Qrisp allocates them |
| Prepare the candidate domain | Bridge, automatic | Technical user expresses the preparation with Qrisp |
| Load data reversibly | Bridge, automatic | Technical user expresses the loading; Qrisp compiles it |
| Build comparisons | Bridge, automatic | Technical user uses native Qrisp conditions |
| Compose the Boolean rule | Bridge, automatic | Technical user composes native control environments |
| Define temporary values | Bridge/materializer, automatic | Technical user defines them; Qrisp compiles them |
| Manage ancillas | Bridge/materializer, automatic | Qrisp compiler plus cleanup expressed or coordinated by the technical user |
| Perform uncomputation | Bridge, automatic | Qrisp compiler plus the technical user's construction |
| Materialize the logical circuit | Bridge, automatic | Qrisp compiler, after the native implementation is supplied |
| Export the artifact | Bridge, automatic | Technical user configures export through Qrisp/Qiskit |
| Internal semantic validation | Bridge evidence | No equivalent internal certification evaluated in this track |
| Independent replay | Common harness | Common harness |
| Neutral normalization | Common policy | Common policy |
| Additional logical optimization | Bridge, automatic additional track | Qrisp compilation; no separately delivered optimized artifact evaluated |
| Authorize and run the experiment | User | User |
| Review the evidence | User | User |

Here, **technical user** means a person with quantum-programming knowledge who translates the business rule into platform-specific constructs. **Automatic** means automatic after Bridge accepts a valid, supported specification; it does not mean that the user supplies no data or rule.

The notebook still contains platform-specific integration code for both systems. The precise statement is not “without adapters,” but **independent platform-specific implementations using public interfaces**. For QDSV, circuit generation is delegated exclusively to `qdsv-bridge`; the notebook contains a local layer that forms the public specification.

## Complementary diagnostics

The `v19` track evaluates five native comparator cases under a frozen 1,200-second per-case Qrisp construction budget. QDSV produced sampled-consistent artifacts for all five cases. The evaluated Qrisp path produced one sampled-consistent contractual artifact (`cost_lte_field_8`); four field-to-constant constructions did not complete entry into the native `ConditionEnvironment` within the budget.

For the one common valid case, QDSV used 9 qubits, depth 118, and 168 operations; Qrisp used 26 qubits, depth 489, and 1,542 operations. After common normalization, the respective depths were 1,370 and 4,422.

The incomplete cases are operational observations about the evaluated implementation, versions, and budget. They do not demonstrate a theoretical inability of Qrisp, and they are not included in the primary quantitative resource ranking. See [limitations.md](limitations.md).

## Evidence

- [Primary v20.1 selected evidence](https://github.com/qdsvquantum-afk/qdsv-bridge/tree/main/benchmarks/qdsv-vs-qrisp/results/v20_1)
- [Complementary v19 selected evidence](https://github.com/qdsvquantum-afk/qdsv-bridge/tree/main/benchmarks/qdsv-vs-qrisp/results/v19)
- [Executable notebooks](https://github.com/qdsvquantum-afk/qdsv-bridge/tree/main/benchmarks/qdsv-vs-qrisp/notebooks)
- [Evidence inventory and ZIP hashes](evidence/README.md)

The repository stores the notebooks, review-sized evidence files, and complete immutable ZIP bundles under [`evidence/bundles/`](https://github.com/qdsvquantum-afk/qdsv-bridge/tree/main/benchmarks/qdsv-vs-qrisp/evidence/bundles). Every bundle is identified by SHA-256 in [`evidence/SHA256SUMS`](evidence/SHA256SUMS).

## Conclusion

Both platforms produced semantically consistent artifacts in the controlled common case. For this controlled common case, the QDSV canonical artifact was materially smaller before and after common normalization. The broader diagnostics additionally show a difference in the amount of platform-specific reversible construction required from the technical user under the evaluated paths.

The defensible conclusion is limited to these frozen fixtures, versions, budgets, and integration strategies. It does not establish universal superiority, hardware advantage, fault tolerance, or a general limitation of Qrisp.
