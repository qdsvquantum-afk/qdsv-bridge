# QDSV Bridge: Public Technical Preview

QDSV Bridge is the QDSV interoperability service for circuit-based quantum
workflows. Applications submit a bounded decision request and receive a
portable OpenQASM or Qiskit-ready artifact when the request is within the
service's supported scope.

Version `0.7.x` is a Public Technical Preview with a deliberately narrow public boundary. The SDK
contains domain request builders, an HTTP client and artifact adapters. The
QDSV translation and implementation that derive an artifact run only in the
Bridge service.

- [Documentation](https://qdsvquantum-afk.github.io/qdsv-bridge/)
- [PyPI](https://pypi.org/project/qdsv-bridge/)
- [Source](https://github.com/qdsvquantum-afk/qdsv-bridge)

## Business-First Quickstart

Describe the prepared candidates and decision rule; Bridge returns a portable
artifact without requiring the application to author a quantum circuit.

```python
from qdsv_bridge import (
    QDSVBridge,
    const,
    field,
    predicate_request,
)

suppliers = [
    {"supplier_id": 101, "quality": 820, "compliance": 1},
    {"supplier_id": 102, "quality": 680, "compliance": 1},
    {"supplier_id": 103, "quality": 760, "compliance": 0},
]

request = predicate_request(
    candidates=suppliers,
    rule={
        "op": "and",
        "args": [
            {"op": "gte", "left": field("quality"), "right": const(700)},
            {"op": "eq", "left": field("compliance"), "right": const(1)},
        ],
    },
    format="qasm2",
)

artifact = QDSVBridge().export(request)

print(artifact.format)
print(artifact.artifact_digest)
```

The SDK sends the bounded public request to Bridge; it does not construct a
circuit locally.

## Prepare candidates for any supported problem

Both `predicate_request()` and `score_request()` receive a non-empty list of
prepared candidate records. Each record is one alternative that Bridge can
evaluate using the fields named in the rule or score model. Choose a bounded
set of candidates and prepare those fields before calling the SDK.

The candidate's position in the submitted list is its computational index:
`0, 1, ..., N-1`. The default `candidate_id_field` is `candidate_index`. You may
omit that field and let the service assign the index. If you include it, its
integer value **must equal the record's zero-based position in this request**.
Changing `candidate_id_field` changes the field name, not this positional rule.
Otherwise Bridge returns `E_BRIDGE_PUBLIC_CANDIDATE_ID`.

For a sample or a reordered list, assign fresh positional indices and keep
the original record identifiers in a separate lookup for interpreting results:

```python
selected_rows = [
    {"source_id": 47, "metric": 8},
    {"source_id": 12, "metric": 3},
]
source_by_candidate = {
    index: row["source_id"] for index, row in enumerate(selected_rows)
}
candidates = [
    {"candidate_index": index, "metric": row["metric"]}
    for index, row in enumerate(selected_rows)
]
# candidates now have candidate_index 0 and 1; source_by_candidate keeps 47 and 12.
```

Use the prepared `candidates` in either request builder. Keep reference labels
or expected answers outside the request when they are only for later
comparison. A valid request can still be rejected by capability or resource
checks; candidate indexing is only one part of the public input contract.

## ScoreModel request shape

For a multi-criterion threshold decision, use `score_request()`. Each criterion
needs a `value` expression that reads a prepared candidate field. `field` is
not a substitute for the criterion's `value` key. The decision uses
`operator` and `threshold`:

```python
from qdsv_bridge import QDSVBridge, field, score_request

request = score_request(
    candidates=[
        {"candidate_index": 0, "readiness": 0},
        {"candidate_index": 1, "readiness": 1},
    ],
    criteria=[
        {"name": "readiness", "value": field("readiness"), "importance": 1, "priority": 1},
    ],
    decision={"operator": "gte", "threshold": 1},
    format="qasm2",
)
artifact = QDSVBridge().export(request)
```

If a criterion omits `value`, the service rejects the request with
`E_BRIDGE_PUBLIC_SCORE_VALUE` before it evaluates numeric scales or thresholds.
`numeric_preferences` controls optional numeric configuration; it cannot
replace a missing criterion value.

## User modes and exact public result

The same public request can select how much result detail Bridge returns:

| Mode | User profile | Public result |
| --- | --- | --- |
| `use` | `basic_user` | Verified portable artifact, resources and digests. |
| `build` | `intermediate_builder` | The artifact plus safe build details. |
| `expert_prepare` | `expert_constructor` | Semantic construction guidance; `artifact` and `artifact_digest` are `None`. |
| `expert_evaluate` | `expert_evaluator` | The artifact plus public alternatives and comparison data. |

Use the client helpers when you want the response dictionary for a specific
profile:

```python
from qdsv_bridge import QDSVBridgeClient

client = QDSVBridgeClient()
basic_result = client.generate(request)
intermediate_result = client.build(request)
expert_inputs = client.prepare(request)
expert_evaluation = client.evaluate(request)
```

Every response identifies its resolved `mode` and `user_profile`.
`QDSVBridge().export(request)` remains the circuit adapter for the three modes
that deliver an artifact. Use `QDSVBridgeClient.prepare(request)` for
`expert_prepare`, whose result is guidance for expert construction rather than
a finished circuit.

## Qiskit integration

Install the optional adapter:

```bash
pip install "qdsv-bridge[qiskit]"
```

Then load the recommended artifact into your own Qiskit workflow:

```python
from qdsv_bridge import QDSVBridge

bridge = QDSVBridge()
artifact = bridge.export(request)
qc = artifact.to_quantum_circuit()
```

``export()`` is explicit: it sends only the public domain request to Bridge.
Before Qiskit parses anything, the adapter confirms that ``artifact_digest``
matches the exact returned OpenQASM bytes and that the public verification
status passed. ``to_quantum_circuit()`` makes no network request.

Bridge does not select a backend, transpile for a device, execute a simulator
or QPU, or interpret execution results. Those remain under the user's Qiskit
or provider workflow. The SDK has no local construction or circuit-generation
fallback.

## Semantic composition candidates

The official Bridge backend can also report the status of QDSV's Semantic
Composition Engine (SCE). SCE generates composite operation candidates from
bounded structured expressions and only marks them `OFFICIAL_CANDIDATE` when
the backend evidence includes both operation-program verification and semantic
cross-check over the declared finite domain.

The public capability endpoint only returns a summary. Candidate generation and
evidence packages require an authenticated Qruba/Bridge governance context.

```python
from qdsv_bridge import QDSVBridgeClient

client = QDSVBridgeClient(api_key="...")
capabilities = client.composition_capabilities()

candidate = client.generate_composition_candidate(
    name="policy_gate_score_v1",
    expression={
        "op": "select_if",
        "args": [
            {"op": "gte", "args": [{"var": "risk"}, 5]},
            {"op": "add", "args": [{"op": "mul", "args": [{"var": "risk"}, 2]}, {"var": "impact"}]},
            {"var": "impact"},
        ],
    },
    domains=[
        {"type": "int_range", "variable": "risk", "start": 0, "end": 7},
        {"type": "int_range", "variable": "impact", "start": 0, "end": 7},
    ],
)

print(candidate["candidate"]["state"])
print(candidate["evidence"]["semantic_cross_check"]["status"])
```

Reference outputs may be used by the backend to verify candidate semantics, but
the evidence must report `reference_answers_used_for_materialization = false`.
The SDK does not include the private compiler or operation synthesis internals.
SCE is available to Bridge as a generation/query capability for composite
operation candidates. It does not change Bridge's product boundary: Bridge
continues to return verified circuit artifacts/OpenQASM/Qiskit-ready outputs;
catalog governance, QPU evidence attachment and OFFICIAL promotion belong to
the Qruba/API governance surface.

## Public boundary

The SDK's stable contracts are `qdsv_bridge_domain.v1` for requests and
`qdsv_bridge_public.v1` for responses. The Qiskit adapter accepts `qasm2` and
`qasm3` artifacts.

The public service does not return internal intermediate representations,
lowering plans, private build identities, exact operational limits, SCE
certification topology or compilation diagnostics. Do not send confidential,
regulated or secret data to a public endpoint.

The distributable wheel and source package are checked before release against
the 0.7 public-distribution policy. The check fails when an unexpected module,
historical documentation, implementation marker or unapproved package file is
present.

## Migration from 0.6.x

Release `0.7.0` was intentionally breaking. Replace legacy request builders
with `predicate_request()` or `score_request()`, and receive a verified public
artifact through `QDSVBridge().export(request)`. See the 0.7 migration guide
in the documentation before upgrading an existing integration.
