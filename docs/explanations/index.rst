Explanations
============

Problem-first Boundary
----------------------

Bridge starts from controlled semantic problem specifications rather than
from handwritten circuit templates. The public artifact boundary consists of
an executable circuit or expert construction package plus reproducibility
evidence. Internal compiler representations are not part of that boundary.

Operation Compiler Boundary
---------------------------

Problem-family labels do not select a circuit implementation. The compiler
checks every required operation and only declares a circuit ready when the
complete supported construction path succeeds. Otherwise Bridge returns public
construction inputs and the exact missing capabilities.

Public SDK, Private Runtime
---------------------------

The public SDK exposes the client, CLI, examples, notebooks, versioned logical
optimization contract and public preview documentation. It does not expose the
private runtime, compiler implementation rules, private backend adapters,
secrets or production configuration.

Delivery Model
--------------

Bridge supports different delivery modes for different users:

* Basic users can request canonically materialized circuits and ready-to-run
  outputs when their specification contains computable semantics.
* Intermediate users can inspect executable OpenQASM/Qiskit artifacts and
  the evidence proving how they were materialized.
* Expert users can request semantic construction inputs or inspect the actual
  materialization evidence. Alternatives remain explicitly conceptual until
  independently materialized.

Construction Verification Boundary
----------------------------------

Bridge verifies the semantic-to-circuit construction path, complete operation
coverage, reversible contracts, no-precomputed-answer invariants, concrete
resources and digest linkage. It does not validate the user's domain assumptions,
the truth of input data, provider execution or simulator/hardware results.

Bridge does not label uniform-superposition scaffolds as completed semantic
circuits. Specifications without prepared numeric signals or canonical
predicate IR remain expert inputs.

Similarity Boundary
-------------------

Bridge distinguishes prepared metrics from declared similarity operations. An
externally supplied similarity score remains an attributed input; Bridge does
not claim to have calculated it. The public operation contract includes bounded
scalar similarity and a fixed normalized-overlap/fidelity operation for bounded
prepared numeric vectors. It does not provide arbitrary vector metrics or a
general cosine-similarity interface. Materialization remains capability- and
resource-dependent.

Advanced Internal Boundary
--------------------------

Internally, the supported construction path uses a typed operation graph and a
backend-neutral reversible representation. These terms define the verification
boundary only. Public responses contain stable summaries, capability
identifiers, resource evidence and digests rather than the private graph,
reversible representation or implementation rules.

Logical Artifact Lifecycle
--------------------------

The current Bridge contract separates artifact identity from artifact
recommendation:

.. code-block:: text

   semantic specification
   -> canonical logical materialization
   -> immutable canonical artifact and digest
   -> optional exact logical optimization
   -> validated child artifact and parent digest
   -> conservative recommendation
   -> physical handoff outside Bridge

The canonical artifact remains the source of truth. The optimized artifact is
an optional child realization of the same semantic program, not a new problem
definition. Bridge records its lineage and keeps both roles visible.

Exact Logical Optimization
--------------------------

The public ``qiskit_structural_exact_v1`` profile is target-independent. Its
acceptance contract checks prepared-state equivalence, register and measurement
preservation, valid-domain behavior and protected logical resource metrics. The
``pareto_no_regression_v1`` policy can recommend a child only when validation
passes and protected metrics do not regress.

Public evidence includes the requested profile, declared pass sequence,
acceptance status, before/after resources, artifact identities and validation
outcome. Private compiler implementation rules, custom passes and target-aware
decision logic are not part of the SDK contract.

Logical and Physical Responsibilities
-------------------------------------

Logical optimization reduces or simplifies a portable logical artifact without
selecting a device. It does not include physical qubit layout, connectivity
routing, scheduling, calibration-aware target selection, noise suppression,
error mitigation or provider execution.

Those target-aware responsibilities belong to Runtime/HSP or an equivalent
user-controlled physical workflow. Hardware evidence must remain separate from
Bridge construction and logical-equivalence evidence.
