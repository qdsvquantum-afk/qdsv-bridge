# Limitations

1. The primary quantitative comparison contains one controlled eight-candidate business case. It supports a case-specific result, not a universal platform ranking.
2. Semantic equivalence is assessed by finite-shot replay (`8,192` shots), not exhaustive formal equivalence.
3. No QPU, target topology, calibration snapshot, routing, noise mitigation, or error suppression is evaluated.
4. Native resource counts are representation-dependent. The common-normalized track reduces but does not eliminate all compiler and frontend differences.
5. Construction latency compares a remote Bridge workflow with local Qrisp construction and compilation; it is not a pure compiler-speed measurement.
6. QDSV's optimized logical artifact is an additional product capability and is excluded from the primary canonical/native comparison.
7. The Qrisp track uses public Qrisp `0.9.6` APIs plus a recorded packaging compatibility shim. The shim does not alter framework source or semantics.
8. The four `v19` field-to-constant cases that exceeded 1,200 seconds are `operational_incomplete` for the evaluated implementation. They are not proof that Qrisp cannot express or synthesize those predicates through another public or maintainer-recommended construction.
9. The benchmark does not evaluate Classiq because the account used for the experiment returned HTTP 403 for synthesis. This avoids treating an authorization limitation as a technical platform result.
10. Effort/LOC measurements describe these transparent implementations. They do not measure maintainability, developer experience across all users, or total platform engineering investment.
11. Results depend on the frozen package versions and may change in later QDSV, Qrisp, Qiskit, or Aer releases.
