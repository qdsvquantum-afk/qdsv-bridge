from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_public_documentation_describes_composable_semantic_scope() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    explanations = (ROOT / "docs" / "explanations" / "index.rst").read_text(
        encoding="utf-8"
    )
    public_text = re.sub(r"\s+", " ", f"{readme}\n{explanations}")

    assert "domain-agnostic within its certified semantic operation set" in public_text
    assert "general predicates and ScoreModel v2" in public_text
    assert "not by a fixed catalog of industries or use cases" in public_text

    assert "For supported problem families" not in readme
    assert "Bridge supports bounded problem families" not in readme


def test_public_documentation_keeps_materialization_limits_explicit() -> None:
    readme = re.sub(
        r"\s+", " ", (ROOT / "README.md").read_text(encoding="utf-8")
    )

    assert "certified reversible lowering" in readme
    assert "resource limits" in readme
    assert "does not accept every arbitrary business or quantum program" in readme
