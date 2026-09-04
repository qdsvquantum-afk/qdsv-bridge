# QDSV Bridge 0.7.0 Conformance

This is a new black-box conformance profile for the frozen public boundary:
`qdsv_bridge_domain.v1` to `qdsv_bridge_public.v1`. It replaces neither nor
interprets the historical 0.6.5 suite, whose private-structure assertions are
not valid for this boundary.

The runner imports only Qiskit, Qiskit Aer and `requests`. It sends public
domain requests to Bridge, parses the returned OpenQASM 2 circuit with Qiskit,
transpiles it, and evaluates the bounded expected function with Aer and a
statevector. Expected answers live in a separate verifier-only fixture and
are never included in a request.

## Run

```shell
python -m pip install -r requirements.lock
python suite/run_conformance.py \
  --api-url http://127.0.0.1:18080/api \
  --output ./evidence/run-001
```

## Released verifier package

For an external campaign, use the separately published
`qdsv-bridge-conformance-v0.7.0.tar.gz`, not a checkout of the SDK repository.
First verify its SHA-256 entry in the accompanying `SHA256SUMS`, unpack it and
then verify every frozen component before making a request:

```shell
sha256sum -c SHA256SUMS
tar -xzf qdsv-bridge-conformance-v0.7.0.tar.gz
cd qdsv-bridge-conformance-v0.7.0
python suite/verify_manifest.py
python -m pip install -r requirements.lock
python suite/run_conformance.py --api-url https://your-bridge.example/api --output ./evidence
```

The package is byte-reproducible from the tagged source. Its `manifest.json`
hashes the runner, fixtures, schemas and normative profile. The expected
outputs remain inside the verifier package and are never sent to Bridge.

An isolated verifier image can be built with `docker build -t
qdsv-bridge-conformance:0.7.0 .`. It contains the public runner and its Qiskit
dependencies only; it does not contain the QDSV platform source.

The output contains only public contract projections and hashes. It does not
store circuit source, private compiler code, logs, environment data or secrets.

## Scope

The suite validates exact public envelopes, forbidden metadata absence,
generic negative responses, digest shape and binding, repeated-request
reproducibility, QASM loading, Qiskit transpilation, Aer execution and bounded
function correctness. It does not claim a hardware execution result, unlimited
scalability, a forced production timeout/5xx path or third-party validation.
