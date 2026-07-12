Release Notes
=============

0.1.7
-----

* Removes the placeholder semantic-oracle circuit generator.
* Routes circuit exports through canonical QDSV ProblemSpec/IR materialization.
* Adds compact prepared-signal inputs and structured coherent-score goals.
* Adds formula, precomputation, reversibility, QASM and actual-resource evidence.
* Rejects incomplete circuit claims instead of returning a uniform-superposition scaffold.

0.1.6
-----

* Adds the optional ``qiskit`` extra with an explicit ``qiskit>=2,<3`` compatibility cap.
* Updates Qiskit-oriented installation examples to use ``qdsv-bridge[qiskit]``.
* Keeps the base Bridge SDK lightweight: Qiskit remains optional, not a required runtime dependency.

0.1.5
-----

* Clarifies Bridge delivery modes for basic, intermediate and expert users.
* Documents Qiskit and Braket-oriented OpenQASM workflows.
* Adds Qiskit Ecosystem documentation scaffolding.
