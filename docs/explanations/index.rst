Explanations
============

Problem-first Boundary
----------------------

Bridge starts from controlled semantic problem specifications rather than
from handwritten circuit templates. The public artifact boundary is canonical
QDSV ProblemSpec/IR, a typed operation graph and backend-neutral reversible IR,
followed by executable OpenQASM/Qiskit output plus reproducibility evidence.

Operation Compiler Boundary
---------------------------

Problem-family labels do not select a circuit implementation. The QDSV
Operation Compiler checks every graph node and only declares a circuit ready
when the complete graph has a certified reversible lowering. Otherwise Bridge
returns construction inputs and the exact missing capabilities.

Public SDK, Private Runtime
---------------------------

The public SDK exposes the client, CLI, examples, notebooks and public
preview documentation. It does not expose the private QDSV Runtime, CAP,
production lowering internals, private backend adapters, secrets or
production configuration.

Delivery Model
--------------

Bridge supports different delivery modes for different users:

* Basic users can request canonically materialized circuits and ready-to-run
  outputs when their specification contains computable semantics.
* Intermediate users can inspect executable OpenQASM/Qiskit artifacts and
  the evidence proving how they were materialized.
* Expert users can request semantic construction inputs or compare possible
  materializations.

Bridge does not label uniform-superposition scaffolds as completed semantic
circuits. Specifications without prepared numeric signals or canonical
predicate IR remain expert inputs.
