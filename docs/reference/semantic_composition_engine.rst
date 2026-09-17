Semantic Composition Engine
===========================

QDSV Bridge can expose the public status of server-side composite operation
generation through the Semantic Composition Engine (SCE). The SCE runs in the
Bridge backend; the SDK submits structured requests and receives candidate
evidence packages. The SDK does not contain the private compiler, private
operation synthesis rules, deployment secrets, or backend runtime.

Public Endpoints
----------------

``GET /api/product/composition/capabilities``
   Returns the SCE version, state model, publication policy and semantic
   cross-check policy.

``POST /api/product/composition/generate``
   Requests a composite operation candidate from a bounded expression and
   declared finite domains.

Candidate States
----------------

``AUTO_GENERATED``
   Internal transient state before evidence gates.

``EXPERIMENTAL``
   The operation has a candidate package but did not pass every publication
   gate. Bridge must not expose it as public.

``OFFICIAL_CANDIDATE``
   The operation passed automatic evidence gates and may be exposed by Bridge
   as a controlled public candidate.

``OFFICIAL``
   Reserved for an explicit governance step. The generator never promotes a
   candidate to ``OFFICIAL`` by itself.

Evidence Required For ``OFFICIAL_CANDIDATE``
--------------------------------------------

An ``OFFICIAL_CANDIDATE`` requires both:

* operation-program verification through the QDSV v2 compiler pipeline;
* semantic cross-check over the declared finite domain.

The semantic cross-check:

* enumerates the declared finite domain when it is within the configured limit;
* evaluates the expression with the logical ``ProblemSpec`` reference;
* evaluates the same expression with the canonical QDSV reference;
* compiles case fixtures using expected outputs only as verification references;
* executes the canonical reversible machine and checks result correctness;
* verifies input preservation and clean ancillas.

If the domain is too large to check exhaustively, or any case fails, the
candidate remains ``EXPERIMENTAL`` and is not Bridge-public.

No Classical Bypass
-------------------

The evidence package distinguishes verification from materialization:

``reference_answers_used_for_semantic_verification = true``
   Reference outputs may be used to verify a candidate.

``reference_answers_used_for_materialization = false``
   Reference outputs are not used to build or substitute the realization.

This keeps the public claim narrow: SCE candidates are evidence-backed
operation packages, not precomputed answers.

SDK Usage
---------

.. code-block:: python

   from qdsv_bridge import QDSVBridgeClient

   client = QDSVBridgeClient()

   capabilities = client.composition_capabilities()
   print(capabilities["semantic_composition_engine"]["version"])

   result = client.generate_composition_candidate(
       name="policy_gate_score_v1",
       expression={
           "op": "select_if",
           "args": [
               {"op": "gte", "args": [{"var": "risk"}, 5]},
               {
                   "op": "add",
                   "args": [
                       {"op": "mul", "args": [{"var": "risk"}, 2]},
                       {"var": "impact"},
                   ],
               },
               {"var": "impact"},
           ],
       },
       domains=[
           {"type": "int_range", "variable": "risk", "start": 0, "end": 7},
           {"type": "int_range", "variable": "impact", "start": 0, "end": 7},
       ],
   )

   print(result["candidate"]["state"])
   print(result["evidence"]["semantic_cross_check"]["status"])

