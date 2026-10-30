Get started with 0.7.0
======================

Install the optional Qiskit adapter:

.. code-block:: shell

   pip install "qdsv-bridge[qiskit]"

Create a public domain request and explicitly ask Bridge to export an artifact:

.. code-block:: python

   from qdsv_bridge import QDSVBridge, const, field, predicate_request

   request = predicate_request(
       candidates=[{"supplier_id": 101, "quality": 820, "compliance": 1}],
       rule={
           "op": "and",
           "args": [
               {"op": "gte", "left": field("quality"), "right": const(700)},
               {"op": "eq", "left": field("compliance"), "right": const(1)},
           ],
       },
       format="qasm2",
   )

   artifact = QDSVBridge().export(request)
   circuit = artifact.to_quantum_circuit()

``export()`` is the only network operation in this flow. The adapter confirms
that the returned ``artifact_digest`` binds the exact OpenQASM bytes before it
loads them. ``to_quantum_circuit()`` does not call a network service.

The returned ``QuantumCircuit`` belongs to the user's Qiskit workflow. Choose
a backend, transpile and execute it only under the user's own provider
configuration.

Candidate records and identifiers
---------------------------------

The same candidate rule applies to ``predicate_request()`` and
``score_request()``. Submit a non-empty list of prepared records; the position
of each record in that list is its computational index ``0..N-1``. The default
``candidate_id_field`` is ``candidate_index``. You can omit that field and let
the service assign it. If you provide it, its integer value must match the
record's zero-based position. A custom ``candidate_id_field`` changes only
the field name. A mismatch produces ``E_BRIDGE_PUBLIC_CANDIDATE_ID``.

When sampling or reordering source data, assign new positional indices for
the submitted list and keep the source identifiers in a separate lookup:

.. code-block:: python

   selected_rows = [
       {"source_id": 47, "metric": 8},
       {"source_id": 12, "metric": 3},
   ]
   source_by_candidate = {
       index: row["source_id"] for index, row in enumerate(selected_rows)
   }
   candidates = [
       {"candidate_index": index, "metric": row["metric"]}
       for index, row in enumerate(selected_rows)
   ]

Pass ``candidates`` to either request builder. Use ``source_by_candidate`` to
interpret the returned candidate indices against the original data. Keep
reference labels and expected answers outside the request when they are only
needed for later comparison.

ScoreModel request
------------------

For a bounded score decision, each criterion must contain a ``value``
expression. Refer to a prepared candidate field with ``field(...)``. The
decision uses ``operator`` and ``threshold``:

.. code-block:: python

   from qdsv_bridge import QDSVBridge, field, score_request

   request = score_request(
       candidates=[
           {"candidate_index": 0, "readiness": 0},
           {"candidate_index": 1, "readiness": 1},
       ],
       criteria=[
           {"name": "readiness", "value": field("readiness"), "importance": 1},
       ],
       decision={"operator": "gte", "threshold": 1},
       format="qasm2",
   )
   artifact = QDSVBridge().export(request)

Using ``field`` as a criterion key instead of ``value`` produces
``E_BRIDGE_PUBLIC_SCORE_VALUE``. This error concerns the request structure;
changing the score scale or ``numeric_preferences`` does not supply the
missing value expression.
