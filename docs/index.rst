QDSV Bridge Documentation
=========================

QDSV Bridge is a Public Preview: conformance-tested semantic-to-quantum SDK
for moving from controlled problem-first semantic specifications to executable
quantum circuit artifacts. Version 0.6.6 delivers an immutable canonical
logical artifact and, when its exact validation and no-regression policy pass,
an optional optimized logical child artifact.

Bridge is domain-agnostic within its certified semantic operation set. It
composes bounded numeric and logical operations, including general predicates
and ScoreModel v2, rather than selecting circuits from an industry-template
catalog. Circuit delivery remains subject to complete reversible coverage and
declared materialization limits.

Bridge is part of the Qiskit Ecosystem and uses OpenQASM as a public
artifact boundary between higher-level problem representation and
framework-specific quantum software tooling.

The benchmark and optimization layers do not change the declared problem.
They preserve the semantic contract while making artifact identity, lineage,
resources and validation evidence inspectable.

.. toctree::
   :hidden:

   Documentation Home <self>
   Getting Started <getting_started>
   Tutorials <tutorials/index>
   How-to Guides <how_to/index>
   Public Contract Reference <reference/index>
   Migration To 0.6.5 <migration_0_6_5>
   API Reference <apidocs/index>
   Explanations <explanations/index>
   Release Notes <release_notes>
   GitHub <https://github.com/qdsvquantum-afk/qdsv-bridge>

Start Here
----------

* Install the SDK from PyPI: ``pip install qdsv-bridge``.
* Use ``QDSVBridgeClient()`` for the Public Preview.
* Start with ``client.generate(spec)`` when you want a completed logical
  circuit without designing the circuit manually.
* Use ``select_recommended_artifact(result)`` to receive the accepted optimized
  child when available and otherwise the canonical source of truth.
* Use ``client.build(spec)`` when you want executable OpenQASM/Qiskit
  artifacts, stable public summaries, construction contracts, actual metrics,
  digests and reports.

Artifact Roles
--------------

``result["artifact"]`` is always the canonical ideal artifact. Bridge never
replaces it silently. ``result["optimized_logical_artifact"]`` is optional and
is linked to its parent by digest. ``result["recommended_artifact_role"]``
records which artifact passed the public recommendation policy.

The default optimization profile is exact and target-independent. It preserves
the prepared state, registers, measurements and valid candidate domain, and it
is accepted only when protected logical resource metrics do not regress. It is
not backend routing, calibration-aware compilation, noise reduction, error
mitigation or QPU execution.

Current Public Role
-------------------

Bridge is a conformance-tested Public Preview interoperability layer. It
publicly exposes the versioned logical-optimization profile, declared public
pass sequence, artifact roles, before/after resources, validation status,
lineage and conformance evidence needed to audit its output. It does not expose
private compiler implementation rules, backend adapters, secrets or production
configuration, and it does not export placeholder oracle scaffolds as completed
circuits.

Bridge stops at the portable logical-artifact boundary. Runtime/HSP or an
equivalent user-controlled workflow remains responsible for backend selection,
layout, routing, scheduling, calibration review, mitigation and hardware
evidence.

Release Identity
----------------

Version 0.6.6 packages a machine-readable release manifest containing its
public contract identities, frozen conformance archive digest, bounded
regression summary and the Docker/Cloud Run builds used during release
validation. Use ``qdsv_bridge.get_release_manifest()`` to read it locally.

Those deployment identities describe validated reference builds. They do not
promise that a mutable public endpoint will always serve the same revision.
