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
(``qiskit>=2,<3``) to preserve compatibility with the currently tested Qiskit
major version.

Create a client for the Public Preview:

.. code-block:: python

   from qdsv_bridge import (
       QDSVBridgeClient,
       build_predicate_spec,
       select_recommended_artifact,
   )

   client = QDSVBridgeClient()

Use a private/local Docker node only when you are running QDSV privately:

.. code-block:: python

   client = QDSVBridgeClient.local()

First Business-Defined Artifact
-------------------------------

Start with prepared candidates and a supported functional rule. The user does
not design gates, registers, ancillas or reversible cleanup:

.. code-block:: python

   suppliers = [
       {"candidate_index": 0, "supplier_id": 101, "quality": 820, "compliance": 1},
       {"candidate_index": 1, "supplier_id": 102, "quality": 680, "compliance": 1},
       {"candidate_index": 2, "supplier_id": 103, "quality": 760, "compliance": 0},
   ]

   business_rule = {
       "op": "and",
       "args": [
           {
               "op": "gte",
               "left": {"op": "field", "name": "quality"},
               "right": {"op": "const", "value": 700},
           },
           {
               "op": "eq",
               "left": {"op": "field", "name": "compliance"},
               "right": {"op": "const", "value": 1},
           },
       ],
   }

   spec = build_predicate_spec(rows=suppliers, predicate=business_rule)
   result = client.generate(spec)
   canonical = result["artifact"]
   recommended = select_recommended_artifact(result)

   print(result["status"])
   print(canonical["role"])
   print(result["recommended_artifact_role"])
   print(recommended["format"])
   print(result["construction_verification"])

``candidate_index`` is the stable circuit-domain identity. ``supplier_id`` is
preserved as the organization's business reference. The helper normalizes the
rule without evaluating it or adding expected answers.

Canonical and Recommended Artifacts
-----------------------------------

The canonical artifact is the immutable source of truth for the generated
logical circuit. Bridge may also derive an exact target-independent optimized
child and recommend it after contractual replay and Pareto no-regression checks.

Inspect both roles when you need audit evidence:

.. code-block:: python

   print(result["digests"]["artifact_digest"])
   print(result["digests"].get("optimized_artifact_digest"))
   print(result.get("optimized_logical_artifact"))
   print(result["logical_optimization"])

Use ``select_recommended_artifact`` for normal inline delivery. The helper
returns the accepted optimized artifact when available and otherwise the
canonical artifact. If delivery is metadata-only, it raises an explicit API
error rather than inventing inline circuit content.

The public optimization profile does not select a backend or apply layout,
routing, scheduling, approximation, mitigation or noise handling. See
:doc:`how_to/logical_artifacts` for reproducible configuration and audit steps.
The complete delivery, outcome, privacy and compatibility contract is in
:doc:`reference/public_contract`.

Delivery Modes
--------------

Bridge has one SDK with four delivery modes:

* ``generate`` for users who want completed logical circuits and a safe
  recommended-artifact selection.
* ``build`` for executable OpenQASM/Qiskit artifacts plus materialization evidence.
* ``prepare`` for expert semantic construction inputs.
* ``evaluate`` for the actual materialization evidence plus explicitly labeled
  conceptual alternatives. It evaluates construction evidence; it does not
  execute a circuit or claim a simulator/QPU comparison.

``generate`` and ``build`` reject incomplete circuit specifications. They never
replace the semantic oracle with a placeholder scaffold.

Materialization is capability-driven. The optional legacy ``family`` field is
only a descriptive compatibility label. Use ``client.capabilities()`` to inspect
the operation-level compiler boundary.

Construction verification
-------------------------

Every completed circuit includes a ``construction_verification`` passport. It
records semantic validation, complete operation-graph coverage, reversible
contract checks, no-precomputed-answer checks, actual resource enforcement and
digest linkage. Bridge does not execute the artifact or validate the truth of
the user's domain model or data.

``logical_optimization`` is separate evidence. It reports the frozen profile,
acceptance policy, parent/child lineage, exact replay result and before/after
logical resources. A successful optimization is not evidence that a physical
backend will preserve the same result.
