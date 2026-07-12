from __future__ import annotations

import pytest

from qdsv_bridge import to_braket_openqasm


def test_to_braket_openqasm_materializes_required_gate_definitions() -> None:
    source = '''OPENQASM 3.0;
include "stdgates.inc";
bit[1] c;
qubit[2] q;
h q[0];
cx q[0], q[1];
c[0] = measure q[1];
'''

    converted = to_braket_openqasm(source)

    assert converted.startswith("OPENQASM 3;\n")
    assert 'include "stdgates.inc";' not in converted
    assert "gate cnot a, b" in converted
    assert "cnot q[0], q[1];" in converted
    assert "cx q[0], q[1];" not in converted


def test_to_braket_openqasm_rejects_non_qasm3_input() -> None:
    with pytest.raises(ValueError):
        to_braket_openqasm("not qasm")
