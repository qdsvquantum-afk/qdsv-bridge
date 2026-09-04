Migration from 0.6.x
====================

Version 0.7.0 is a deliberate public-boundary break. The historical 0.6.x
source is retained at Git tag ``v0.6.7`` and is not part of this release tree.

Replace legacy request construction with a bounded domain request:

.. code-block:: python

   from qdsv_bridge import QDSVBridge, const, field, predicate_request

   request = predicate_request(
       candidates=[{"value": 4}],
       rule={"op": "eq", "left": field("value"), "right": const(4)},
       format="qasm2",
   )
   artifact = QDSVBridge().export(request)
   circuit = artifact.to_quantum_circuit()

The SDK no longer accepts previous request representations as an alternate
path. The response is a public artifact envelope with its digest attestation;
use ``QDSVBridgeArtifact`` rather than selecting between legacy artifact roles.
