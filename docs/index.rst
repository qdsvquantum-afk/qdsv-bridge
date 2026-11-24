QDSV Bridge
===========

QDSV Bridge accepts bounded public domain requests and returns verified,
portable OpenQASM artifacts. The SDK contains request builders, a network
client and framework adapters; the service performs the remote transformation.

The 0.7.x public release has a versioned public contract,
capability discovery, published guardrails and digest-bound artifact delivery.
A consumer can inspect the delivered circuit, its digest and public resource
data, but the package has no local fallback that derives a circuit from a
domain request.

.. toctree::
   :hidden:

   Documentation Home <self>
   Getting Started <getting_started_070>
   Migration from 0.6.x <migration_0_7_0>
   Public Contract Reference <reference/index>
   API Reference <apidocs/index>
   GitHub <https://github.com/qdsvquantum-afk/qdsv-bridge>

Start Here
----------

* Install the SDK: ``pip install qdsv-bridge``.
* Build a request with the public domain helpers.
* Explicitly call ``QDSVBridge.export(request)``.
* Verify and load the returned artifact into the user's own Qiskit workflow.

User modes
----------

``use`` serves ``basic_user`` and returns a verified portable artifact.
``build`` serves ``intermediate_builder`` and adds safe build details.
``expert_prepare`` serves ``expert_constructor`` and returns semantic
construction guidance without forcing a final artifact. ``expert_evaluate``
serves ``expert_evaluator`` and returns an artifact with public alternatives
and comparison data.

Use ``QDSVBridgeClient.generate()``, ``build()``, ``prepare()`` and
``evaluate()`` respectively. The Qiskit ``QDSVBridge`` facade consumes only
responses that contain a circuit artifact.

Bridge does not select hardware, transpile for a device, execute a simulator or
QPU, or interpret execution results.

Public service posture
----------------------

The running service exposes ``/api/bridge/capabilities`` so integrations can
discover the contract version, supported modes, formats, endpoints, limits and
execution boundary before submitting a request. Bridge is available for
technical adoption and commercial use within its published capabilities and
limits; it does not claim unlimited capacity, quantum advantage or a
provider-level SLA.
