from __future__ import annotations


_BRAKET_GATE_DEFINITIONS = (
    "gate x a { U(pi, 0, pi) a; }",
    "gate h a { U(pi/2, 0, pi) a; }",
    "gate rz(lambda) a { gphase(-lambda/2); U(0, 0, lambda) a; }",
    "gate cnot a, b { ctrl @ x a, b; }",
)


def to_braket_openqasm(source: str) -> str:
    """Convert a canonical Bridge QASM3 artifact for Braket execution."""

    if not isinstance(source, str) or "OPENQASM 3" not in source:
        raise ValueError("A canonical OpenQASM 3 source string is required.")

    lines: list[str] = []
    inserted_definitions = False
    for line in source.splitlines():
        stripped = line.strip()
        if stripped in {"OPENQASM 3.0;", "OPENQASM 3;"}:
            lines.append("OPENQASM 3;")
            lines.extend(_BRAKET_GATE_DEFINITIONS)
            inserted_definitions = True
        elif stripped == 'include "stdgates.inc";':
            continue
        elif stripped.startswith("cx "):
            lines.append(line.replace("cx ", "cnot ", 1))
        else:
            lines.append(line)

    if not inserted_definitions:
        raise ValueError("The source does not contain a supported OpenQASM 3 header.")
    return "\n".join(lines) + "\n"


__all__ = ["to_braket_openqasm"]
