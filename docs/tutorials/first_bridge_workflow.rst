First Bridge Workflow
=====================

This tutorial shows the basic Bridge route:

.. code-block:: text

   problem specification -> Bridge artifact -> inspection/report

Use ``generate`` when you want a simpler starting point:

.. code-block:: python

   from qdsv_bridge import QDSVBridgeClient, select_recommended_artifact

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
   canonical = result["artifact"]
   recommended = select_recommended_artifact(result)

   print(canonical["role"])
   print(result["recommended_artifact_role"])
   print(recommended["content"])
   print(result["construction_verification"])
   print(result["logical_optimization"])

The canonical artifact remains available even when Bridge recommends the
optimized child. This keeps the original logical realization auditable and
makes the recommendation explicit rather than silently replacing output.

Use ``build`` when you need additional editable artifacts and
reproducibility evidence:

.. code-block:: python

   result = client.build(spec)
   print(result["editable_artifacts"]["ir_summary"])
   print(result["digests"])

For real hardware, hand the selected logical artifact and its contracts to
Runtime/HSP or an equivalent target-aware workflow. Do not interpret logical
optimization as layout, routing, noise reduction or hardware validation.
