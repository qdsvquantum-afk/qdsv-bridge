Migration To 0.6.5
==================

QDSV Bridge 0.6.5 is a contract-and-evidence stabilization release. Existing
0.6.4 uses of ``QDSVBridgeClient``, ``build_predicate_spec()``,
``build_score_expression_spec()``, ``build_score_model_spec()`` and
``select_recommended_artifact()`` remain compatible.

What Changed
------------

* The SDK version now identifies the post-0.6.4 public contract and evidence
  bundle as one release unit.
* ``get_release_manifest()`` exposes machine-readable contract identities,
  validated runtime identities, conformance results and explicit boundaries.
* The normative conformance outcomes distinguish semantic failure from
  invalid input, unsupported capability and resource limits.
* Regression summaries cover the evaluated general-kernel and ScoreModel
  configurations without converting bounded evidence into universal claims.

What Did Not Change
-------------------

* The private compiler is not shipped in the SDK.
* ``result["artifact"]`` remains the canonical logical artifact.
* The optional optimized artifact remains a separately identified child and is
  recommended only after exact validation and no-regression acceptance.
* Bridge still stops before backend selection, routing, scheduling, mitigation
  and QPU execution.
* No expected answer or class label is accepted as a substitute for quantum
  materialization.

Recommended Upgrade Check
-------------------------

.. code-block:: python

   import qdsv_bridge

   manifest = qdsv_bridge.get_release_manifest()
   assert qdsv_bridge.__version__ == "0.6.5"
   assert manifest["contracts"]["bridge"] == "qdsv_bridge_operation_compiler.v2"
   assert manifest["boundaries"]["contains_private_compiler"] is False

Then rerun the same semantic specification and compare problem, IR,
materialization and artifact digests according to the public contract. A
resource-limited result must not be relabeled as a semantic failure.
