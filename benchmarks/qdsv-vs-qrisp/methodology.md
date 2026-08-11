# Methodology

## Experimental question

Given the same public business data and decision rule, what semantically valid logical artifact does each evaluated public platform path deliver, what work remains with the user, and what resources are observed before and after a common normalization?

The benchmark starts from a business problem, not from a reference circuit. No platform receives a predesigned circuit or the frozen expected answers as construction input.

## Frozen protocol

1. Freeze public input data, predicate meaning, candidate order, expected answers, versions, seeds, shots, and budgets.
2. Keep frozen expectations outside platform construction inputs.
3. Build each artifact through an independent platform-specific implementation using public interfaces.
4. Export each artifact into the common Qiskit-based evidence harness.
5. Replay with 8,192 shots, seed `20260805`, and Aer MPS.
6. Reject resource comparison unless both artifacts satisfy marking, domain, and ancilla-cleanliness checks.
7. Normalize each valid native artifact independently with basis `rz`, `sx`, `x`, `cx`, optimization level 3, and the frozen transpiler seed.
8. Report canonical/native comparison as the neutral primary track. Report QDSV's separately delivered optimized artifact only as an additional track.

## Semantic acceptance

The common replay evaluates:

- candidate/predicate outcomes against frozen expectations;
- probability assigned outside the valid candidate domain;
- residual probability in nonzero ancilla states;
- statistical consistency under the frozen shot budget.

`sampled_consistent` is a finite-shot result. It is not exhaustive state-space equivalence and does not predict physical-hardware quality.

## Independence contract

The two implementations share only:

- public business data;
- public predicate meaning;
- frozen expected answers used by the post-construction evaluator;
- common replay and measurement logic;
- common normalization policy.

QDSV uses `build_predicate_spec()` and Bridge generation. Qrisp uses native field allocation, reversible loading, comparisons, control environments, compilation, and Qiskit conversion. QDSV-specific construction code is not used to build the Qrisp circuit, and Qrisp-specific construction code is not used to build the QDSV circuit.

The evaluated Qrisp environment includes an audited packaging compatibility shim for `qrisp.permeability.unqomp`. It does not modify Qrisp source or predicate semantics and is recorded in the evidence.

## Metrics

Native metrics describe each platform's exported artifact. Normalized metrics describe the output of the same external Qiskit normalization policy.

Effort metrics separate:

- shared platform infrastructure;
- case-specific platform logic;
- end-user invocation;
- neutral predicate specification.

Lines of code are descriptive, not a universal productivity measure. They help locate where the business-to-circuit translation resides in these notebooks.

## Reproducibility

Open the notebooks in Google Colab or a compatible Python 3.12 environment. The QDSV path requires valid Bridge credentials and available public quota. The Qrisp path executes locally. Reproduction must preserve the frozen fixture, versions, seed, shots, budgets, and normalization settings, or be labeled as a new experiment.
