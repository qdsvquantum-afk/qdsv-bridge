QDSV Bridge Public Technical Preview boundary
=============================================

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

Published user modes
--------------------

All four public modes use the same ``qdsv_bridge_domain.v1`` request:

* ``use`` returns the ``basic_user`` artifact result.
* ``build`` returns the ``intermediate_builder`` artifact and safe build details.
* ``expert_prepare`` returns ``expert_constructor`` guidance, with no artifact.
* ``expert_evaluate`` returns the ``expert_evaluator`` artifact and public
  evaluation data.

The response always includes ``mode`` and ``user_profile``. For
``expert_prepare``, ``artifact`` and ``artifact_digest`` are ``None`` by
contract; callers use ``QDSVBridgeClient.prepare()``. Circuit-bearing modes can
be passed through the Qiskit adapter after digest verification.

Distribution guard
------------------

Before publication, the release workflow builds the wheel and source archive
and checks them against ``qdsv_bridge_public_distribution.v1``. Unexpected
modules, historical documentation and prohibited implementation markers fail
the release.
