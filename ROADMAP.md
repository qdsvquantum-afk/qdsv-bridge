# QDSV Bridge roadmap

## Completed public evidence

- Reproducible SDK distribution and separate 0.7.0 conformance package,
  published with the 0.7.4 release.
- Public API boundary runnable from a clean environment, without the private
  compiler in the SDK or the verifier.
- CI matrix for Python 3.10–3.12 and Qiskit 2.3–2.5.
- Bounded Aer and IBM `ibm_fez` evidence from the 0.7.0 compiler campaign.

The results and their limits are recorded in
`docs/reference/validation_evidence.rst`.

## Next maturity milestones

- Independent third-party rerun from PyPI and the published conformance
  package, against the current public service and 0.7.4 SDK.
- Forced timeout and internal-service-failure checks, which the 0.7.0
  black-box campaign did not evaluate.
- Explicit support and compatibility policy for a stable SDK release,
  together with documented service reliability and resource limits.
- Re-evaluate the Qiskit Ecosystem maturity declaration when the supported
  public workflow is stable and recommended for production use. The separate
  `Early Project` status is based on repository age and changes automatically.

## Product boundaries

Bridge remains a bounded domain-request-to-artifact service. It does not
provide local circuit generation, target-specific routing, managed QPU
execution, or a Qiskit Function Catalog listing.
