QDSV Bridge Documentation
=========================

QDSV Bridge is a Python SDK for moving from controlled problem-first
semantic specifications toward executable quantum circuit artifacts,
including OpenQASM/Qiskit workflows, the tested Amazon Braket
``LocalSimulator`` conversion workflow and reproducibility reports.

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
* Start with ``client.generate(spec)`` when you want a canonically materialized,
  ready-to-run circuit.
* Use ``client.build(spec)`` when you want executable OpenQASM/Qiskit
  artifacts, stable public summaries, construction contracts, actual metrics,
  digests and reports.

Current Public Role
-------------------

Bridge is a developer-preview interoperability layer. It does not expose
the private runtime, internal compilation or optimization rules, private
backend adapters, secrets or production configuration.
It does not export placeholder oracle scaffolds as completed circuits.
