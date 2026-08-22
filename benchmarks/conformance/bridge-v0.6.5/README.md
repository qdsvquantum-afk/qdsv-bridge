# QDSV Bridge Conformance v0.1 For SDK 0.6.5

This directory publishes the reduced public evidence package for QDSV Bridge
`0.6.5`.

The purpose is to let reviewers inspect how Bridge was evaluated without
exposing private compiler internals, production configuration, credentials,
notebooks, raw service logs or sensitive data.

## What This Evaluates

The benchmark starts from bounded semantic problem specifications, not from
pre-designed circuits. It checks whether Bridge can derive and document
verified logical quantum artifacts while preserving the declared problem
meaning.

The public conformance package covers:

- semantic compilation through `qdsv_operation_compiler.v2`;
- reversible materialization when a supported construction exists;
- canonical logical artifact generation;
- exact independent replay for selected cases;
- deterministic repeated builds and stable digests;
- supported error outcomes for invalid specs, unsupported operations and
  resource limits;
- separation between semantic, logical, normalized and physical evidence.

## Summary

- SDK version: `0.6.5`
- Release commit: `f747c1a9068aef1ef57f9092ad4602c4864d3722`
- Conformance contract: `qdsv_bridge_conformance.v0.1`
- Bridge contract: `qdsv_bridge_operation_compiler.v2`
- Compiler authority: `qdsv_operation_compiler.v2`
- Conformance cases: `10/10 PASS`
- General kernel benchmark: `36/36 PASS`
- ScoreModel benchmark: `16/16 PASS`
- SDK unit tests: `41/41 PASS`

## Included

- `spec/`: public normative minimum and conformance profiles.
- `schema/`: report and manifest schemas.
- `fixtures/`: public inputs and expected outcomes for the suite.
- `suite/`: public runner scripts.
- `evidence/`: summarized final run report and manifest.
- `benchmarks/`: summarized kernel and ScoreModel benchmark manifests.

## Not Included

- private compiler implementation;
- private lowering rules or formulas;
- credentials, API keys, headers or production configuration;
- notebooks and exploratory development files;
- raw service logs or full private evidence bundles;
- IBM hardware evidence, which belongs to a separate downstream validation
  track.

## Reproduce

Create a clean environment, install the SDK version under test, and run:

```powershell
python -m pip install qdsv-bridge==0.6.5
python .\suite\run_conformance.py `
  --api-url https://api.qdsv.cloud/api `
  --output .\local-evidence
```

The public service may enforce quota and resource limits. A `RESOURCE_LIMITED`
outcome is a valid contract result when a public quota or configured resource
limit is reached; it is not a semantic failure.

## Full Evidence

This repository contains the public evidence layer. The complete owner-side
evidence bundle, notebooks and extended raw artifacts are retained separately
and may be shared under an appropriate review context.
