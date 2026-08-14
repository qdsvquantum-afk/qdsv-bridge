Select and Audit Logical Artifacts
==================================

Bridge returns an immutable canonical logical artifact and may return an exact
optimized child. This guide shows how to use the recommendation without losing
the canonical audit trail.

Select the Recommended Inline Artifact
--------------------------------------

.. code-block:: python

   from qdsv_bridge import QDSVBridgeClient, select_recommended_artifact

   result = QDSVBridgeClient().generate(spec)
   canonical = result["artifact"]
   recommended = select_recommended_artifact(result)

   print(canonical["role"])
   print(result["recommended_artifact_role"])
   print(recommended["content"])

``select_recommended_artifact`` returns the optimized child only when Bridge
declares it recommended and its content is available inline. Otherwise it
returns the canonical artifact. Metadata-only delivery raises
``QDSVBridgeAPIError`` instead of pretending that circuit content is present.

Inspect Optimization Evidence
-----------------------------

.. code-block:: python

   optimization = result["logical_optimization"]

   print(optimization["status"])
   print(optimization["profile"])
   print(optimization["acceptance_policy"])
   print(optimization["resources_before"])
   print(optimization["resources_after"])
   print(result["digests"])

The exact response may include additional evidence fields as the public
contract evolves. Treat the status, profile, acceptance policy, resources,
digests and artifact roles as evidence; do not infer hardware quality from
them.

Freeze the Public Profile
-------------------------

The bounded-predicate helper can freeze the versioned public contract for a
reproducible run:

.. code-block:: python

   from qdsv_bridge import build_predicate_spec

   spec = build_predicate_spec(
       rows=rows,
       predicate=predicate,
       logical_optimization={
           "mode": "auto",
           "profile": "qiskit_structural_exact_v1",
           "acceptance_policy": "pareto_no_regression_v1",
       },
   )

For a manually assembled specification, place the same mapping in
``target.logical_optimization``. Custom passes, physical targets, layouts,
routing and approximation settings are outside the public Bridge contract.

Request Canonical-only Delivery
-------------------------------

Set ``target.logical_optimization`` to ``false`` when a workflow requires the
byte-for-byte canonical artifact and no optimized child should be attempted.
This does not disable semantic construction verification.

Hand Off to a Physical Workflow
-------------------------------

Choose the logical artifact first, preserve its role and digests, and then pass
it to Runtime/HSP or an equivalent user-controlled target-aware workflow:

.. code-block:: text

   canonical or accepted optimized logical artifact
   -> backend selection and calibration snapshot
   -> target-aware transpilation, layout and routing
   -> exact replay of the frozen physical artifact
   -> authorized provider execution
   -> separate hardware evidence

Bridge does not perform the physical stages in this sequence.
