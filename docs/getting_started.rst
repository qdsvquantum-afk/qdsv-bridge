Getting Started
===============

Installation
------------

Install QDSV Bridge from PyPI:

.. code-block:: bash

   pip install qdsv-bridge

For optional Qiskit artifact inspection:

.. code-block:: bash

   pip install "qdsv-bridge[qiskit]"

The Qiskit extra is version-capped to the current supported major series
(``qiskit>=2,<3``) to follow Qiskit Ecosystem compatibility guidance.

Create a client for the public developer preview:

.. code-block:: python

   from qdsv_bridge import QDSVBridgeClient

   client = QDSVBridgeClient()

Use a private/local Docker node only when you are running QDSV privately:

.. code-block:: python

   client = QDSVBridgeClient.local()

First Artifact
--------------

Use ``generate`` for the simplest delivery mode:

.. code-block:: python

   spec = {
       "state_space": {
           "kind": "finite_candidates",
           "candidate_count": 2,
           "candidate_id": "candidate",
       },
       "signals": ["eligibility_score"],
       "prepared_candidates": [
           {"eligibility_score": 0},
           {"eligibility_score": 1},
       ],
       "goal": {
           "kind": "marking",
           "threshold": 1,
           "criteria": [
               {"signal": "eligibility_score", "influence": 1, "priority": 1}
           ],
       },
       "target": {
           "format": "qasm3",
           "backend_family": "qiskit",
       },
       "limits": {
           "max_qubits": 8,
           "max_depth": 160,
       },
   }

   result = client.generate(spec)

   print(result["status"])
   print(result["bridge_mode"])
   print(result["artifact"]["format"])

Delivery Modes
--------------

Bridge has one SDK with four delivery modes:

* ``generate`` for users who want canonically materialized, ready-to-run circuits.
* ``build`` for executable OpenQASM/Qiskit artifacts plus materialization evidence.
* ``prepare`` for expert semantic construction inputs.
* ``evaluate`` for expert comparison of possible materializations.

``generate`` and ``build`` reject incomplete circuit specifications. They never
replace the semantic oracle with a placeholder scaffold.

Materialization is capability-driven. The optional legacy ``family`` field is
only a descriptive compatibility label. Use ``client.capabilities()`` to inspect
the operation-level compiler boundary.
