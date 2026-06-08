# Contributing To QDSV Bridge

Thanks for helping improve QDSV Bridge.

This repository contains the public SDK, docs, examples and tests for the Bridge client.

## Good Contributions

- Bug reports with compact semantic specs.
- Documentation improvements.
- New examples for supported families.
- Better QASM/Qiskit integration examples.
- Reports of confusing validation messages.
- Suggestions for controlled, bounded Bridge families.

## Out Of Scope

- Raw datasets or private data in issues.
- Requests for arbitrary circuit generation.
- Requests to expose QDSV Runtime internals.
- Requests for hardware execution through Bridge SDK.
- Free-form user-supplied circuits as family contracts.

## Development

```bash
pip install -e .
python -m pytest
```

Before opening an issue, please include:

- package version;
- Python version;
- API endpoint used;
- Bridge mode;
- compact spec;
- expected result;
- actual result or traceback.
