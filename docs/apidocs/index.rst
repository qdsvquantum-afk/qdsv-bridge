API Reference
=============

Client
------

.. autoclass:: qdsv_bridge.QDSVBridgeClient
   :members:
   :undoc-members:
   :show-inheritance:

Domain Requests
---------------

.. autofunction:: qdsv_bridge.predicate_request

.. autofunction:: qdsv_bridge.score_request

Qiskit Adapter
--------------

.. autoclass:: qdsv_bridge.QDSVBridge
   :members:

.. autoclass:: qdsv_bridge.QDSVBridgeArtifact
   :members:

.. autofunction:: qdsv_bridge.to_quantum_circuit

Compatibility Helpers
---------------------

.. autofunction:: qdsv_bridge.to_braket_openqasm

Exceptions
----------

.. autoclass:: qdsv_bridge.QDSVBridgeError
   :members:

.. autoclass:: qdsv_bridge.QDSVBridgeAPIError
   :members:

.. autoclass:: qdsv_bridge.QDSVBridgeArtifactError
   :members:

.. autoclass:: qdsv_bridge.QDSVBridgeHTTPError
   :members:
