Getting Started
===============

Installation
------------

Install QDSV Bridge from PyPI:

.. code-block:: bash

   pip install qdsv-bridge

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
       "family": "bounded_semantic_marking",
       "state_space": {
           "kind": "finite_candidates",
           "candidate_count": 8,
           "candidate_id": "candidate",
       },
       "signals": ["eligibility_score", "risk_score"],
       "goal": {
           "kind": "marking",
           "predicate": "eligible_candidate",
       },
       "target": {
           "format": "qasm3",
           "backend_family": "qiskit",
       },
       "limits": {
           "max_qubits": 5,
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

* ``generate`` for users who want ready-to-use problem-derived artifacts.
* ``build`` for inspectable OpenQASM/Qiskit/Braket-oriented artifacts.
* ``prepare`` for expert semantic construction inputs.
* ``evaluate`` for expert comparison of possible materializations.
