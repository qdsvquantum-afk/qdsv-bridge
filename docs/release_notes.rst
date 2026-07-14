Release Notes
=============

0.4.4
-----

* Narrows the public contract to circuit delivery and expert construction
  artifacts, removing unrelated terminology from the Bridge surface.
* Rejects unsupported abbreviated goals before circuit materialization instead
  of silently substituting another intent.
* Ensures ``prepare()`` requests an expert construction artifact rather than a
  final circuit and verifies ``operation_coverage`` in the correct delivery mode.
* Installs the OpenQASM 3 importer in the end-user Colab validation workflow.

0.4.3
-----

* Clarifies the public artifact boundary for every delivery mode and keeps
  private compiler representations and implementation rules out of responses.
* Makes active examples capability-driven and limits Amazon Braket wording to
  the tested ``LocalSimulator`` OpenQASM conversion workflow.
* Updates the first workflow tutorial to use a directly materializable problem
  specification without a family selector.

0.4.2
-----

* Adds an explicit semantic-to-circuit ``construction_verification`` passport
  without claiming simulator or hardware execution.
* Documents exact outputs and responsibilities for basic, intermediate and
  expert users.
* Reports only actual materializations as materialized; other expert designs
  remain labeled conceptual until independently built.
* Documents the public importance-priority aggregation semantics and the exact
  flat/global and hierarchical block/global penalty scope.
* Adds end-to-end evidence for modulo, absolute value, absolute difference,
  scalar similarity, all six decisions, hierarchical decisions, bounded Grover
  amplification and work-register cleanup.

0.4.1
-----

* Uses ``importance`` and ``priority`` as the public ScoreModel v2 vocabulary.
* Keeps legacy ``weight`` and ``criticality`` inputs as compatibility aliases.
* Separates Bridge circuit delivery from QDSV backend validation: public
  capabilities no longer publish simulator or hardware execution status.
* Returns public ScoreModel artifacts with user-facing decision terminology while
  retaining canonical mathematical names inside the QDSV compiler.

0.4.0
-----

* Adds canonical ScoreModel v2 circuit delivery for bounded flat and hierarchical
  formulas supported by QDSV Operation Compiler.
* Supports nonlinear value expressions, signed contextual adjustments,
  weighted-criticality aggregation, normalization, penalties and six comparison
  operators within the certified physical profile.
* Returns a public materialization passport with circuit and compiler digests,
  actual resources and no-precomputation evidence.
* Does not expose private lowering data, functional rows, candidate-score tables,
  quantized offsets or precomputed answers.
* Ensures exported OpenQASM 2 programs use instructions that Qiskit can load again.
* Makes ``/bridge/capabilities`` the primary catalog endpoint and keeps
  ``/bridge/families`` only as a compatibility alias.
* Separates global payload admission limits from physical circuit capacity,
  which is decided by the certified lowering profile and actual resources.

0.3.0
-----

* Removes the legacy circuit route that classically enumerated predicate results.
* Exports circuits only when QDSV Operation Compiler produces a reversible semantic
  formula without precomputed answers.
* Keeps standalone predicates available as expert construction inputs rather than
  presenting them as executable circuits.
* Reports ``formula_materialized_in`` and explicit no-bypass evidence in generated
  artifacts.
* Rejects unsupported circuit requests with capability gaps and a safe expert-mode
  alternative.

0.2.0
-----

* Uses QDSV Operation Compiler v1 as the circuit-capability authority.
* Adds typed operation graph, reversible IR, strategy, resource and verification evidence.
* Accepts canonical ``problem_spec`` input without a family selector.
* Treats legacy family values as compatibility labels only.
* Adds ``client.capabilities()`` while retaining ``families()`` as an alias.
* Returns exact missing operation capabilities instead of selecting a family fallback.

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
* Documents Qiskit and the tested Amazon Braket LocalSimulator OpenQASM workflow.
* Adds Qiskit Ecosystem documentation scaffolding.
