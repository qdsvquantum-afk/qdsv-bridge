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
