from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_public_documentation_describes_the_070_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "interoperability service for circuit-based quantum" in readme
    assert "deliberately narrow public boundary" in readme
    assert "does not construct a circuit locally" in readme


def test_public_documentation_keeps_materialization_limits_explicit() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "does not select a backend" in readme
    assert "does not return internal intermediate representations" in readme
