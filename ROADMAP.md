# QDSV Bridge roadmap

## 0.7.0 release gate

- Publish a reproducible SDK distribution and separate conformance package.
- Make the public API boundary independently runnable from a clean environment.
- Preserve implementation exclusively within the QDSV service.

## Next evidence milestones

- Clean-room PyPI reproduction against a controlled public endpoint.
- Aer and IBM Quantum hardware evidence for preregistered bounded cases.
- Independent third-party rerun using the published conformance package.

## Product boundaries

Bridge remains a bounded domain-request-to-artifact service. It does not
provide local circuit generation, target-specific routing, managed QPU
execution, or a Qiskit Function Catalog listing.
