QDSV Bridge Documentation
=========================

QDSV Bridge is a Python SDK for moving from controlled problem-first
semantic specifications toward inspectable quantum-oriented artifacts,
including OpenQASM/Qiskit workflows, Braket-oriented workflows and
reproducibility reports.

Bridge is part of the Qiskit Ecosystem and uses OpenQASM as a public
artifact boundary between higher-level problem representation and
framework-specific quantum software tooling.

.. toctree::
   :hidden:

   Documentation Home <self>
   Getting Started <getting_started>
   Tutorials <tutorials/index>
   How-to Guides <how_to/index>
   API Reference <apidocs/index>
   Explanations <explanations/index>
   Release Notes <release_notes>
   GitHub <https://github.com/qdsvquantum-afk/qdsv-bridge>

Start Here
----------

* Install the SDK from PyPI: ``pip install qdsv-bridge``.
* Use ``QDSVBridgeClient()`` for the public developer preview.
* Start with ``client.generate(spec)`` when you want ready-to-use,
  problem-derived circuit artifacts.
* Use ``client.build(spec)`` when you want inspectable OpenQASM/Qiskit
  artifacts, IR summaries, oracle specs, digests and reports.

Current Public Role
-------------------

Bridge is a developer-preview interoperability layer. It does not expose
the private QDSV Runtime, production lowering internals, backend-routing
heuristics, private adapters, secrets or production configuration.
