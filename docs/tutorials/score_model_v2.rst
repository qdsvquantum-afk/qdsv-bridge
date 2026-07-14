ScoreModel v2 Circuit Delivery
==============================

ScoreModel v2 lets Bridge request a circuit from the canonical QDSV path for a
bounded multi-criteria decision. It is the broadest decision-oriented circuit
path currently exposed through Bridge, but it is not tied to one industry or to
similarity alone.

Supported value routes
----------------------

Each decision term can consume either:

* a prepared finite numeric metric supplied by the user or another system; or
* a bounded QDSV numeric expression over prepared fields.

A prepared metric can represent a probability, normalized distance, risk
measure, correlation, externally calculated similarity, model output or domain
measurement. Bridge preserves its declared provenance but does not claim to have
computed an externally supplied metric.

The current physical profile can also calculate bounded scalar numeric
similarity and supported arithmetic expressions inside the materialized
operation. Arbitrary vector or cosine similarity is not calculated by this
profile; users may instead provide such a result as a prepared finite numeric
metric.

Implemented decision structure
------------------------------

The canonical ScoreModel v2 implementation supports:

* flat and hierarchical multi-criteria decisions;
* term and block importance and priority values;
* signed contextual adjustments;
* normalization and zero-mass protection;
* flat/global and hierarchical block/global penalties;
* declared fixed-point precision, deterministic rounding and overflow rejection;
* ``eq``, ``ne``, ``lt``, ``lte``, ``gt`` and ``gte`` threshold decisions;
* reversible formula computation, decision marking, measurement and uncompute;
* optional bounded Grover amplification inside the ScoreModel v2 profile,
  without a classical winner scan. This is not a general Grover recipe.

Public vocabulary
-----------------

User-facing ScoreModel specifications use ``importance`` and ``priority``:

.. code-block:: python

   term = {
       "value": prepared_metric,
       "importance": 2,
       "priority": 3,
   }

``importance`` describes relative contribution and ``priority`` describes
declared urgency or severity. Their product is used in the weighted numerator
and normalization mass. A zero value removes the term or block from the
aggregate; ``priority`` is not execution order or precedence. Legacy
``weight`` and ``criticality`` inputs remain accepted for compatibility, but
new SDK code and public responses use the user-facing names. Canonical
mathematical naming remains internal to the QDSV operation compiler.

This capability can represent eligibility and approval screening, multi-criteria
selection, risk-benefit assessment, evaluation of projects or alternatives,
context-aware decisions and hierarchical acceptance policies, provided the
problem is finite, numeric and threshold-based.

Bridge only claims the operations and materialization profiles listed by its
public capability contract. Capabilities outside that contract are not inferred
or substituted.

Run the public example from the repository root:

.. code-block:: bash

   python examples/score_model_v2.py

The example sends a canonical ``problem_spec`` and requests OpenQASM 2 through
``client.build``. A successful response includes:

* an executable circuit artifact;
* actual qubit and depth metrics;
* formula, circuit and operation-program digests;
* evidence that candidate answers were not precomputed;
* the public capability profile identifier, without private implementation details.

The physical profile is deliberately bounded. If a formula exceeds the current
input-state or artifact limits, Bridge rejects the circuit request instead of
returning a partial scaffold. ``client.prepare`` remains available when expert
construction inputs are useful but a complete circuit cannot be certified.

Delivery evidence and boundaries
--------------------------------

The public response exposes the capability profile identifier, program and
artifact digests, actual qubit and depth metrics, and explicit
no-precomputation evidence. It does not expose private compiler implementation,
internal optimization rules, intermediate candidate scores or precomputed
answers.

Physical synthesis is constrained by ``max_input_qubits`` and
``max_function_states`` in the numeric contract. Cost can grow rapidly with the
number and precision of prepared fields.

Bridge stops after delivering the circuit artifact or expert construction
inputs. It does not execute the circuit on a simulator or QPU or validate the
problem result; hardware validation is not part of the Bridge delivery contract.
Execution resources, provider credentials and result validation remain the
user's responsibility.
