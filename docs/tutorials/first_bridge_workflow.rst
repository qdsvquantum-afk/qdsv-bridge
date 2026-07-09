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
   }

   result = client.generate(spec)
   print(result["artifact"]["source"])

Use ``build`` when you need additional editable artifacts and
reproducibility evidence:

.. code-block:: python

   result = client.build(spec)
   print(result["editable_artifacts"]["ir_summary"])
   print(result["digests"])
