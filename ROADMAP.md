# QDSV Bridge Roadmap

QDSV Bridge is in Developer Preview. The SDK is a public client; the private QDSV Runtime and semantic compiler internals remain closed.

## Current

- Public Python SDK on PyPI.
- Public Bridge API client.
- Family-based validation, compile, explain and export.
- Output modes: `use`, `build`, `expert_prepare`, `expert_evaluate`.
- Controlled fallback family: `bounded_semantic_marking`.
- Resource limits and raw-data rejection.
- Circuit-origin metadata: `qdsv_derived`.

## Next

- More family examples.
- More QASM/Qiskit blueprint examples.
- Clearer preservation reports.
- Better examples for basic, intermediate and expert users.
- More diagnostics for unsupported specs.
- Notebooks that compare prebuilt-template workflows vs problem-derived Bridge outputs.

## Later

- More specialized Bridge families.
- More export target variants.
- TypeScript client preview.
- Stronger public examples for Qiskit/PennyLane/Braket users.
- GitHub Discussions after initial technical feedback.

## Boundaries

Bridge will remain a controlled semantic-to-circuit interface. It will not become an arbitrary circuit generator, a template selector, a bulk-data processor or a hardware execution SDK.
