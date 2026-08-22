Release Notes
=============

0.6.6
-----

* Aligns package metadata, README and documentation around the public
  positioning "Public Preview: conformance-tested semantic-to-quantum SDK".
* Keeps the functional conformance evidence linked to the frozen 0.6.5
  conformance suite; no private compiler internals, hardware execution claims
  or SLA guarantees are added.

0.6.5
-----

* Updates the public positioning to "Public Preview: conformance-tested
  semantic-to-quantum SDK" while retaining explicit pre-``1.0``, resource,
  hardware and SLA boundaries.
* Freezes the public ``qdsv_bridge_operation_compiler.v2`` and
  ``qdsv_operation_compiler.v2`` identities used by the validated logical
  materializer.
* Adds ``get_release_manifest()`` so an installed wheel exposes its exact
  contract, conformance, runtime-validation and boundary metadata.
* Links the normative conformance outcome model to a frozen external evidence
  archive without packaging the suite or private compiler in this SDK.
* Records 36/36 general-kernel and 16/16 ScoreModel bounded regression results;
  these results demonstrate the evaluated configurations and are not claims of
  unbounded scalability or universal resource superiority.
* Adds a migration guide. Existing 0.6.4 builders, clients and artifact
  selection behavior remain compatible.

0.6.4
-----

* Fixes canonical unary-expression normalization for logical, null and
  rounding operations.
* Adds public outcome-blind helpers for numeric threshold expressions and flat
  or hierarchical ScoreModel v2 specifications.
* Publishes unambiguous weighted-sum and per-operation construction contracts
  while keeping every materialization resource checked.

0.6.3
-----

* Clarifies that Bridge is domain-agnostic within its certified semantic
  operation set rather than limited to industry-specific templates.
* Documents general predicates and ScoreModel v2 as composable public paths.
* Defines practical limits through verified reversible coverage and materialized
  resources without expanding the compiler contract or exposing private rules.

0.6.2
-----

* Moves the public lifecycle designation from Developer Preview to Public
  Preview while retaining explicit pre-``1.0``, resource and SLA boundaries.
* Leads with a business-defined Quickstart and moves the detailed SDK contract
  into versioned reference documentation.
* Adds regression coverage that executes the README Quickstart and verifies
  stable circuit identity separately from the business reference.

0.6.1
-----

* Allows reproducible workflows to freeze the public logical-optimization
  contract through ``build_predicate_spec(logical_optimization=...)``.
* Keeps custom passes and physical-backend settings outside the public helper.
* Documents canonical and optimized artifact roles, recommendation behavior,
  public optimization evidence and the Runtime/HSP physical handoff.

0.6.0
-----

* Keeps the canonical ideal artifact immutable and exposes an optional exact
  target-independent optimized logical child artifact.
* Adds reproducible before/after resources, contractual replay evidence,
  artifact lineage and conservative Pareto acceptance.
* Adds ``select_recommended_artifact`` for basic users while keeping physical
  compilation, noise handling and provider execution in Runtime/HSP.

0.5.4
-----

* Added ``build_predicate_spec()`` for bounded compound business predicates.
* Added deterministic normalization for nested boolean rules and field-to-field comparisons.
* Kept predicate evaluation, expected answers and private ScoreModel aggregation outside the SDK helper.

0.5.3
-----

* Adds a minimal public ScoreModel example based on prepared metrics, a shared
  declared scale and the high-level ``generate()`` contract.
* Clarifies that ``priority`` represents a domain parameter rather than list
  order or execution precedence.
* Keeps private ScoreModel aggregation and compiler rules outside the public
  SDK documentation and adds regression coverage for that boundary.

0.5.2
-----

* Adds a backend-neutral circuit realization package tied to the canonical
  semantic, quantum and reversible-plan identities.
* Separates ideal circuit evidence from target optimization, mitigation and
  provider execution through an explicit hardware handoff contract.
* Clarifies that Bridge delivers the canonical ideal logical circuit; managed
  IBM execution belongs to QDSV Runtime/HSP or an equivalent user-controlled
  physical workflow.
* Keeps unavailable ideal replay evidence explicit and omits private artifact
  locations from public target summaries.

0.5.1
-----

* Reorganizes the package README around installation, delivery modes, outputs,
  limits and support.
* Clarifies conditional circuit delivery, ``evaluate()`` behavior and the
  ``qiskit_blueprint`` artifact.
* Adds tested compatibility, privacy, versioning, error-handling and support
  guidance.

0.5.0
-----

* Routes the complete canonical bounded expression set through the shared QDSV
  operation compiler instead of product-specific circuit paths.
* Adds one general bounded reversible circuit realizer, with resource-aware
  specialized formula synthesis derived from the same canonical program.
* Uses exact valid-domain preparation and diffusion, including non-power-of-two
  candidate domains, with explicit compute-mark-uncompute verification.
* Publishes circuit-generation and QASM-load evidence for all canonical public
  expression operations and keeps physical resource rejection explicit.

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
* Documents the public importance and priority configuration contract while
  keeping aggregation and lowering internals outside the SDK surface.
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
  bounded multi-criteria decisions, penalties and six comparison operators
  within the certified physical profile.
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
