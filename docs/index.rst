QDSV Bridge 0.7.0 Documentation
================================

QDSV Bridge accepts bounded public domain requests and returns verified,
portable OpenQASM artifacts. The SDK contains request builders, a network
client and framework adapters; the service performs the remote transformation.

The 0.7.0 public boundary is intentionally narrow. A consumer can inspect the
delivered circuit, its digest and public resource data, but the package has no
local fallback that derives a circuit from a domain request.

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

Bridge does not select hardware, transpile for a device, execute a simulator or
QPU, or interpret execution results.
