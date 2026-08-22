# QDSV Benchmark Evidence Catalog

This directory consolidates selected, frozen evidence without copying notebooks,
private compiler code, datasets, credentials or operational services.

## Measurement tracks

| Track | Question | Evidence | Must not be claimed as |
|---|---|---|---|
| Semantic | Does the artifact implement the frozen business predicate? | Independent replay, mismatches, invalid states | Hardware performance |
| Reversibility | Are candidate identity and work ancillas preserved? | Basis-state replay and clean-ancilla probability | Noise robustness |
| Logical resources | What does the portable artifact require? | Qubits, depth and operations before physical targeting | QPU-ready cost |
| Common normalization | How do artifacts compare under one Qiskit basis and transpiler policy? | Qubits, depth, CX and total operations | Device-specific routing |
| Hardware | What occurred on a named physical backend and snapshot? | Job, shots, coverage and statistical acceptance | Logical equivalence alone |

The first four tracks are represented here. Hardware evidence remains in the
separate thesis evidence archive and is not merged into logical benchmark rows.

## Frozen results

### General semantic kernel

- 36/36 successful configurations.
- Operations: `eq`, `ne`, `lt`, `lte`, `gt`, `gte`, `and`, `or`, `xor`.
- Candidate counts: 2, 4, 8 and 16.
- Every row records independent semantic replay, zero mismatches and the
  `qdsv_operation_compiler.v2` authority.
- Maximum measured normalized depth in this frozen run: 2,181.
- Maximum measured normalized CX count in this frozen run: 1,248.

### ScoreModel generalization

- 16/16 successful configurations with independent replay.
- Candidate counts: 2, 4, 8 and 16.
- Signal counts: 2, 3, 4 and 5.
- Maximum measured normalized depth in this frozen run: 2,062.
- Maximum measured normalized CX count in this frozen run: 1,191.

These are bounded tests, not claims of unlimited scalability.

### Controlled 8-candidate comparison

The frozen retest preserved semantic accuracy 1.0 and changed the normalized
Bridge artifact from 11 qubits / depth 5,086 / 2,913 CX / 6,519 operations to
10 qubits / depth 1,038 / 580 CX / 1,423 operations. Under the same recorded
normalization, the manual Qiskit baseline used 16 qubits / depth 1,868 / 1,061
CX / 2,368 operations.

This comparison is valid for the frozen common case only. It does not establish
universal superiority over manual Qiskit or another platform.

## Evidence files

- `evidence/bridge_kernel_generalization.csv`
- `evidence/bridge_scoremodel_generalization.csv`
- `evidence/bridge_vs_best_manual_qiskit.csv`
- `evidence/bridge_improvement_retest_8c.csv`
- `evidence/run_manifest.json`
- `evidence_manifest.json`

The source run used Bridge SDK 0.6.2. It is historical benchmark evidence and
must not be relabeled as a Bridge 0.6.4 execution.
