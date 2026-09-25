QDSV Bridge 0.7 public boundary
================================

The stable request contract is ``qdsv_bridge_domain.v1``. The stable service
response contract is ``qdsv_bridge_public.v1``.

Public SDK contents
-------------------

* Bounded domain-request builders.
* An HTTP client with timeouts and bounded retries.
* Artifact-digest validation.
* QASM2/QASM3 loading into ``QuantumCircuit`` after delivery.

Service-only work
-----------------

The service is the sole place that turns a valid public request into an
artifact. The SDK does not have a second local path to produce a circuit.

Public responses carry a request digest, an artifact digest for delivered
artifacts, verification status, warnings and basic resource metrics. Build
identity, exact operational limits and compiler diagnostics are not part of
the unauthenticated public boundary. It is not a diagnostic trace.

Distribution guard
------------------

Before publication, the release workflow builds the wheel and source archive
and checks them against ``qdsv_bridge_public_distribution.v1``. Unexpected
modules, historical documentation and prohibited implementation markers fail
the release.
