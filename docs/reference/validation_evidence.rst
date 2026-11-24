Validation evidence and maturity
================================

This page separates tested behavior from the scope of the public service.
The current 0.7.x release is a public product for bounded requests.
The SDK sends the request to a remote compiler and does not generate circuits
locally.

Published SDK checks
--------------------

* The `0.7.4 release <https://github.com/qdsvquantum-afk/qdsv-bridge/releases/tag/v0.7.4>`_
  contains the SDK distributions, distribution checks and the separately
  packaged 0.7.0 black-box conformance verifier.
* The `current CI workflow <https://github.com/qdsvquantum-afk/qdsv-bridge/actions/workflows/conformance-070.yml>`_
  tests the SDK on Python 3.10–3.12 and Qiskit 2.3–2.5. CI tests the checked-out
  source and build artifacts; it is not an independent public-service audit.
* The request and response envelopes are versioned as
  ``qdsv_bridge_domain.v1`` and ``qdsv_bridge_public.v1``.

Bounded service and hardware campaign
-------------------------------------

On 2026-09-04, the 0.7.0 black-box conformance runner reported five passes,
zero failures and two checks not evaluated against the Cloud Run service. The
passes covered public predicate and score fixtures, negative public errors,
and repeated-request reproducibility. Forced timeout and internal-service-
failure paths were not evaluated.

The same dated compiler campaign submitted three preregistered bounded
fixtures to IBM ``ibm_fez`` after exact Aer checks. Each used 4,096 shots,
Qiskit optimization level 3 and no mitigation. All three met the campaign's
declared acceptance criteria:

=======================  ===============
Fixture                  Decision accuracy
=======================  ===============
Power-of-two predicate   95.31%
Non-power-of-two case    66.21%
Score threshold          87.94%
=======================  ===============

These were 0.7.0 compiler-build results. They do not validate every later
service build, every input size or the full 0.7.4 user-mode surface. The QPU
campaign was not a controlled hardware comparison and is not evidence of
quantum advantage or provider-level SLA. The full campaign artifacts have
not been independently rerun from this repository.

Scope declaration
------------------

Bridge is a public product for the bounded workflows listed in its capability
contract. This declaration does not imply unrestricted scaling, quantum
advantage or provider-level service guarantees. New operation families and
larger workloads are added through versioned capability releases.

See the `Qiskit Ecosystem classification rules
<https://qiskit.github.io/ecosystem/classifications/>`_ and the
`roadmap <https://github.com/qdsvquantum-afk/qdsv-bridge/blob/main/ROADMAP.md>`_
for the remaining evidence and support milestones.
