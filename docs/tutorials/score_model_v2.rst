ScoreModel v2 Circuit Delivery
==============================

ScoreModel v2 lets Bridge request a circuit from the canonical QDSV path for a
bounded formula that combines value expressions, contextual adjustments,
weights, criticalities, penalties and a final decision threshold.

Run the public example from the repository root:

.. code-block:: bash

   python examples/score_model_v2.py

The example sends a canonical ``problem_spec`` and requests OpenQASM 2 through
``client.build``. A successful response includes:

* an executable circuit artifact;
* actual qubit and depth metrics;
* formula, circuit and operation-program digests;
* evidence that candidate answers were not precomputed;
* the certified lowering profile, without private lowering tables.

The physical profile is deliberately bounded. If a formula exceeds the current
input-state or artifact limits, Bridge rejects the circuit request instead of
returning a partial scaffold. ``client.prepare`` remains available when expert
construction inputs are useful but a complete circuit cannot be certified.
