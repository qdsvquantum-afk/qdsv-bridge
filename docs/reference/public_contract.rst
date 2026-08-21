Public SDK Contract
===================

QDSV Bridge accepts compact semantic specifications and bounded prepared
numeric inputs. Circuit delivery remains conditional on operation support,
complete construction and active resource limits. Bridge never substitutes an
unsupported operation with a placeholder or a precomputed answer.

Delivery Modes
--------------

One semantic specification can be used at four output depths:

.. list-table::
   :header-rows: 1
   :widths: 18 27 55

   * - Method
     - Intended user
     - Result
   * - ``generate()``
     - User requesting the quantum core
     - Completed circuit, loading guidance, resources and construction
       evidence when materialization succeeds.
   * - ``build()``
     - QASM or Qiskit integrator
     - Editable artifact, public construction summaries, resources and
       digests when materialization succeeds.
   * - ``prepare()``
     - Expert constructor
     - Validated construction requirements and capability gaps without
       forcing a final circuit.
   * - ``evaluate()``
     - Expert reviewer
     - Materialization evidence and explicitly labeled construction
       alternatives. It does not execute a simulator or QPU.

Start with the same ``spec`` used by the business-first Quickstart:

.. code-block:: python

   result = client.generate(spec)
   recommended = select_recommended_artifact(result)

   package = client.build(spec)
   prepared = client.prepare(spec)
   review = client.evaluate(spec)

Canonical And Optimized Artifacts
---------------------------------

``result["artifact"]`` is the immutable canonical artifact. The optional
``result["optimized_logical_artifact"]`` is a child linked to its parent by
digest. Bridge recommends the child only when exact replay, register and
measurement preservation, valid-domain checks and the public no-regression
policy pass.

.. code-block:: python

   canonical = result["artifact"]
   recommended = select_recommended_artifact(result)

   print(result["logical_optimization"]["resources_before"])
   print(result["logical_optimization"]["resources_after"])
   print(result["recommended_artifact_role"])

Reproducible workflows can freeze the public logical profile:

.. code-block:: python

   spec = build_predicate_spec(
       rows=rows,
       predicate=predicate,
       logical_optimization={
           "mode": "auto",
           "profile": "qiskit_structural_exact_v1",
           "acceptance_policy": "pareto_no_regression_v1",
       },
   )

``mode`` is the versioned public switch. Custom passes, target layouts,
routing and approximation settings are outside the Bridge contract. See
:doc:`../how_to/logical_artifacts` for the complete audit workflow.

Digest Reproducibility
----------------------

For a frozen Bridge compiler, Qiskit version and optimization profile, the
same normalized specification produces byte-identical canonical OpenQASM and
stable artifact digests. Bridge canonicalizes process-local names introduced
by circuit serialization before it computes those digests.

``semantic_oracle_digest`` identifies the oracle contract without transport
serialization. ``oracle_digest`` additionally links that contract to the
canonical materialized QASM. ``canonical_qasm_digest``, ``artifact_digest``
and ``recommended_artifact_digest`` identify their corresponding delivered
artifacts. This separation lets an auditor distinguish semantic stability
from transport stability without exposing private compiler rules.

Artifact Targets
----------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Target
     - Output
   * - ``qasm2``
     - Completed OpenQASM 2 circuit.
   * - ``qasm3``
     - Completed OpenQASM 3 circuit.
   * - ``qiskit_blueprint``
     - Python loader generated from completed canonical QASM, not a partial
       circuit blueprint.
   * - ``oracle_spec``
     - Public expert construction contract.
   * - ``problem_spec``
     - Normalized public problem specification.
   * - ``ir``
     - Stable public summary, not the private compiler representation.

Outcomes And Errors
-------------------

Circuit-oriented targets are returned only after the complete supported
construction succeeds. Unsupported capabilities, resource limits and invalid
specifications are explicit HTTP errors; transport and service failures remain
API errors.

.. code-block:: python

   from qdsv_bridge import QDSVBridgeAPIError, QDSVBridgeHTTPError

   try:
       result = client.generate(spec)
   except QDSVBridgeHTTPError as error:
       print(error.status_code)
       print(error.payload)
   except QDSVBridgeAPIError as error:
       print(f"Bridge service unavailable: {error}")

Use ``client.capabilities()`` for the current operation catalog and deployment
limits.

Logical And Physical Handoff
----------------------------

The backend-neutral ``circuit_realization_package`` links the logical circuit
to semantic, quantum and reversible-plan digests and includes result,
measurement and decoder contracts. It establishes what the ideal circuit
represents; it is not evidence that a specific QPU preserves that result.

Backend selection, target transpilation, layout, routing, scheduling,
calibration review, mitigation and provider execution remain downstream in
Qiskit, Qruba, Runtime/HSP or an equivalent user-controlled workflow. See
:doc:`../integrations/ibm_quantum` for the IBM/Qiskit handoff.

Limits And Privacy
------------------

The Public Preview is not a bulk-data service and does not accept raw datasets
or hardware-execution requests. Payload, compilation time, artifact size,
qubit and depth ceilings are deployment-controlled. A semantically valid
problem can be rejected when its realization exceeds those limits.

Do not send personal, confidential, regulated or security-sensitive data to
the public endpoint. The Public Preview has no SLA or contractual retention
guarantee. Use a private deployment for sensitive workloads and follow the
project security policy.

.. code-block:: python

   public_client = QDSVBridgeClient()       # https://api.qdsv.cloud/api
   private_client = QDSVBridgeClient.local()  # http://localhost:18080/api

Reports
-------

Bridge can render public construction evidence as JSON, Markdown or HTML:

.. code-block:: python

   report = client.report(spec, mode="build", format="markdown")
   print(report["content"])

Reports identify the accepted specification, delivered artifact, warnings,
resource evidence and digests. They do not claim simulator or hardware
execution.

Tested Compatibility
--------------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Component
     - Tested or supported boundary
   * - Python
     - ``>=3.9``
   * - Qiskit SDK
     - ``>=2,<3``
   * - Qiskit Aer
     - ``>=0.17,<0.18``
   * - Qiskit QASM 3 importer
     - ``>=0.5,<0.7``
   * - OpenQASM
     - QASM 2 and QASM 3 artifacts generated by Bridge.
   * - Amazon Braket SDK
     - Optional OpenQASM conversion tested with ``LocalSimulator``; it is not
       an official managed Amazon Braket integration.

Bridge does not provide managed IBM Quantum or Amazon Braket hardware
execution.
