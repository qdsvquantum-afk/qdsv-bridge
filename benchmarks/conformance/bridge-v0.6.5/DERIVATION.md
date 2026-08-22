# QDSV Bridge Conformance v0.1 Runner For SDK 0.6.5

This directory is derived from the frozen QDSV Bridge Conformance v0.1 suite
used for SDK 0.6.4.

The normative specification, schemas, public inputs, expected outputs and test
assertions are unchanged. The only functional changes are:

- the environment lock requires `qdsv-bridge==0.6.5`;
- the runner rejects any SDK version other than `0.6.5`;
- run identifiers include `sdk065` to prevent evidence from being confused
  with the historical 0.6.4 run.

This derivation does not import the private compiler, add expected answers to
requests, bypass service validation or reinterpret resource limits as passes.
