QDSV Bridge 0.7.0 Conformance
==============================

The 0.7.0 conformance profile validates the frozen public boundary only:
``qdsv_bridge_domain.v1`` requests and ``qdsv_bridge_public.v1`` responses.
It does not inspect, import or distribute QDSV compiler internals.

The normative profile lives at
``benchmarks/conformance/bridge-v0.7.0``. It contains separate public-input
and verifier-only expected-output fixtures, the public-boundary declaration,
an isolated Docker verifier and a runner using only Qiskit, Qiskit Aer and
``requests``.

What is tested
--------------

* Exact public envelopes for ``compile``, ``export`` and ``report``.
* Absence of private IR, lowering, materialization and diagnostic fields.
* Generic public errors for malformed, unsupported and resource-limited input.
* SHA-256 integrity for the delivered OpenQASM bytes, request identity and an
  opaque compiler-build attestation.
* Repeated-request reproducibility for the same compiler build.
* OpenQASM 2 loading into ``QuantumCircuit``, Qiskit transpilation, Aer
  execution, input preservation and clean work registers for bounded fixtures.

The expected function is held exclusively by the verifier and is never sent to
Bridge. A third party can therefore run the same suite with access only to the
public API and the published conformance package.

Run the released profile
------------------------

For external validation, download the separately published
``qdsv-bridge-conformance-v0.7.0.tar.gz`` and its ``SHA256SUMS`` from the
release associated with the SDK tag. Verify the archive and its internal
manifest before sending any request:

.. code-block:: shell

   sha256sum -c SHA256SUMS
   tar -xzf qdsv-bridge-conformance-v0.7.0.tar.gz
   cd qdsv-bridge-conformance-v0.7.0
   python suite/verify_manifest.py
   python -m pip install -r requirements.lock
   python suite/run_conformance.py \
     --api-url https://your-bridge.example/api \
     --output ./bridge-070-evidence

The released archive is byte-reproducible from the tag. Or build the isolated
verifier image from its unpacked directory and pass the same arguments. The
image contains no QDSV platform source.

Scope and limitations
---------------------

This profile supports claims about the listed bounded public cases and Qiskit
interoperability. It does not establish unbounded scaling, hardware execution,
hardware advantage, a forced production timeout or internal-service-failure
path, nor independent third-party validation. Those claims require separate
evidence.

Historical 0.6.5 material is archived and is not normative for 0.7.0 because
the public surface and privacy boundary changed.
