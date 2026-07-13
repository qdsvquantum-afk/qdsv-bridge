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

The public SDK exposes the client, CLI, examples, notebooks and public preview
documentation. It does not expose the private runtime, internal compilation or
optimization rules, private backend adapters, secrets or production
configuration.

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

Advanced Internal Boundary
--------------------------

Internally, the supported construction path uses a typed operation graph and a
backend-neutral reversible representation. These terms define the verification
boundary only. Public responses contain stable summaries, capability
identifiers, resource evidence and digests rather than the private graph,
reversible representation or implementation rules.
