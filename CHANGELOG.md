# Changelog

## 0.7.0 — Public boundary release

- Replaces the former request surface with the stable
  `qdsv_bridge_domain.v1` public domain contract.
- Freezes `qdsv_bridge_public.v1` as the public response boundary.
- Delivers one verified public artifact with `request_digest`,
  `artifact_digest`, and opaque `compiler_build_digest` attestations.
- Adds the explicit Qiskit adapter: public export, byte-level artifact-digest
  verification, then local QASM2/QASM3 loading into `QuantumCircuit`.
- Adds bounded retry handling that never surfaces raw non-public service bodies.
- Adds release-gating for wheel and source distributions, including an
  allowlist of package files and prohibited implementation markers.
- Adds a separate, black-box 0.7.0 conformance package for third-party runs.

## Historical releases

The 0.6.x release line is archived at the immutable `v0.6.7` Git tag. It is
not part of the 0.7.0 source tree, public documentation set, or conformance
baseline.
