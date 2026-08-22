Conformance And Release Identity
================================

The QDSV Bridge Conformance Suite evaluates the observable public contract. It
does not inspect or distribute private compiler implementation rules.

Normative Outcomes
------------------

Every evaluated case has one primary outcome:

``PASS``
   The expected public contract and, when applicable, independent semantic
   replay succeeded.

``SEMANTIC_FAIL``
   A materialized artifact disagreed with the declared valid-domain semantics.

``CONTRACT_FAIL``
   The response violated a required public field, invariant, digest or lineage
   rule.

``RESOURCE_LIMITED``
   The semantic input was admitted but the requested realization exceeded an
   active resource limit. This is not a semantic failure.

``UNSUPPORTED``
   No certified public realization exists for the requested capability.

``INVALID_SPEC``
   The input did not satisfy the public specification contract.

``NOT_APPLICABLE``
   The check does not apply to the selected method, artifact or operation.

``NOT_EVALUATED``
   Evidence was unavailable or the evaluator lacked the required independent
   access. This is not a pass.

Frozen 0.6.5 Evidence
---------------------

The release was validated with the v0.1 contract runner frozen specifically for
SDK 0.6.5 in the archive
``QDSV_Bridge_Conformance_v0.1_SDK_0.6.5.zip``. Its SHA-256 is:

``4232238f03ff68adac7711b4a523d2ff8e6109abdbad15211c40a33537dfd113``

The archive is distributed with the v0.6.5 GitHub release rather than stored
inside the operational SDK repository. It contains the normative specification,
fixtures, schemas and notebook-independent runner. The separate release
evidence bundle contains reports and manifests. Generated virtual environments,
caches, credentials and private compiler sources are excluded.

Evaluated Results
-----------------

* Bridge conformance: 10/10 passed.
* Transversal anti-bypass checks: 10/10 passed.
* Owner clean-room installation and run: 10/10 passed.
* General semantic kernel: 36/36 evaluated configurations passed.
* ScoreModel: 16/16 evaluated configurations passed.
* Independent third-party validation: ``NOT_EVALUATED``.

The bounded regression results verify the listed fixtures and sizes. They do
not establish unbounded scalability, hardware advantage or universal circuit
resource superiority.

Machine-Readable Identity
-------------------------

Use the packaged manifest to bind an installed client to the evidence:

.. code-block:: python

   from qdsv_bridge import get_release_manifest

   identity = get_release_manifest()
   print(identity["contracts"])
   print(identity["validated_runtime_identity"])
   print(identity["conformance"])

The Docker image and Cloud Run revision are validation references, not hidden
requirements and not an availability guarantee. A future deployment must
publish its own identity if it claims equivalence with this release baseline.
