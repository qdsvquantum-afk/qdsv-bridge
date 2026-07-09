Explanations
============

Problem-first Boundary
----------------------

Bridge starts from controlled semantic problem specifications rather than
from handwritten circuit templates. The public artifact boundary is
OpenQASM/Qiskit-oriented output plus reproducibility evidence.

Public SDK, Private Runtime
---------------------------

The public SDK exposes the client, CLI, examples, notebooks and public
preview documentation. It does not expose the private QDSV Runtime, CAP,
production lowering internals, private backend adapters, secrets or
production configuration.

Delivery Model
--------------

Bridge supports different delivery modes for different users:

* Basic users can request problem-derived circuit artifacts and
  ready-to-use outputs.
* Intermediate users can inspect OpenQASM/Qiskit/Braket-oriented artifacts.
* Expert users can request semantic construction inputs or compare possible
  materializations.
