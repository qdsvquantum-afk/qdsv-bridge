First Bridge Workflow
=====================

This tutorial shows the basic Bridge route:

.. code-block:: text

   problem specification -> Bridge artifact -> inspection/report

Use ``generate`` when you want a simpler starting point:

.. code-block:: python

   from qdsv_bridge import QDSVBridgeClient

   client = QDSVBridgeClient()

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
               {"signal": "eligibility_score", "importance": 1, "priority": 1}
           ],
       },
       "target": {
           "format": "qasm3",
           "backend_family": "qiskit",
       },
       "limits": {"max_qubits": 8, "max_depth": 160},
   }

   result = client.generate(spec)
   print(result["artifact"]["content"])
   print(result["construction_verification"])

Use ``build`` when you need additional editable artifacts and
reproducibility evidence:

.. code-block:: python

   result = client.build(spec)
   print(result["editable_artifacts"]["ir_summary"])
   print(result["digests"])
