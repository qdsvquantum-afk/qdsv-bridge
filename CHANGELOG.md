# Changelog

## 0.7.3 — Hardened public boundary

- Removes `qiskit_blueprint` from the unauthenticated public delivery formats.
- Keeps Qiskit interoperability through verified QASM2/QASM3 artifacts and
  local `QuantumCircuit` loading.
- Stops publishing build identity, exact service limits and detailed SCE
  certification topology through public responses.
- Requires the stable `qdsv_bridge_domain.v1` request envelope for public
  Bridge endpoints.

## 0.7.2 — Bridge/SCE boundary clarification

- Clarifies that SCE is available to Bridge as a generation/query capability
  for composite operation candidates.
- Keeps Bridge's product scope narrow: verified circuit artifacts, OpenQASM and
  Qiskit-ready outputs.
- Documents that catalog governance, QPU evidence attachment and OFFICIAL
  promotion belong to the Qruba/API governance surface, not the Bridge SDK.

## 0.7.1 — Semantic Composition Engine access

- Adds public SDK accessors for the Bridge backend Semantic Composition Engine:
  `composition_capabilities()` and `generate_composition_candidate()`.
- Documents the SCE evidence gate for generated operations: operation-program
  verification plus semantic cross-check over the declared finite domain before
  an operation can be marked `OFFICIAL_CANDIDATE`.
- Keeps the compiler, private operation synthesis rules and runtime deployment
  material outside the SDK distribution; reference outputs are allowed for
  semantic verification evidence, not materialization.

## 0.7.0 — Public boundary release

- Replaces the former request surface with the stable
  `qdsv_bridge_domain.v1` public domain contract.
- Freezes `qdsv_bridge_public.v1` as the public response boundary.
- Delivers one verified public artifact with request and artifact digests.
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
