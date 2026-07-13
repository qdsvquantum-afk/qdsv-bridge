# QDSV Bridge Roadmap

QDSV Bridge is in Developer Preview. The SDK is a public client; the private runtime and internal compilation rules are not included.

## Current

- Public Python SDK on PyPI.
- Public Bridge API client.
- Capability-driven validation, compile, explain and export.
- Bridge Report generation in JSON, Markdown and HTML.
- Output modes: `use`, `build`, `expert_prepare`, `expert_evaluate`.
- Legacy family labels accepted as optional compatibility metadata only.
- Resource limits and raw-data rejection.
- Circuit-origin metadata: `qdsv_canonical_problem_ir_materializer`.

## Next

- More problem-first capability examples.
- More QASM/Qiskit blueprint examples.
- Clearer preservation reports.
- Better examples for basic, intermediate and expert users.
- More diagnostics for unsupported specs.
- Notebooks that compare prebuilt-template workflows vs problem-derived Bridge outputs.
- Recipes for supported operation combinations and explicit examples of unsupported capability requests.

## Later

- More certified operation compositions and construction profiles.
- More export target variants.
- PennyLane, Azure Quantum/Q#, Cirq and VS Code integrations as planned integrations, not current public capabilities. Amazon Braket remains limited to the tested LocalSimulator OpenQASM conversion workflow.
- Packaged NISQ workflow examples such as QUBO/QAOA/VQE/Grover as recipes built on top of Bridge artifacts.
- TypeScript client preview.
- Stronger public examples for Qiskit/PennyLane/Braket users.
- GitHub Discussions after initial technical feedback.

## Boundaries

Bridge will remain a controlled semantic-to-circuit interface. It will not become an arbitrary circuit generator, a template selector, a bulk-data processor or a hardware execution SDK.
