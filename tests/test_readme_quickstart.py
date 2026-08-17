from __future__ import annotations

import re
from pathlib import Path

from qdsv_bridge import QDSVBridgeClient


ROOT = Path(__file__).resolve().parents[1]


def _readme_quickstart_code() -> str:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    section = re.search(
        r"^## Business-First Quickstart\s*$\n(?P<body>.*?)(?=^## )",
        readme,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert section is not None, "README Business-First Quickstart section is missing."
    block = re.search(r"```python\s*\n(?P<code>.*?)```", section.group("body"), re.DOTALL)
    assert block is not None, "README Quickstart Python block is missing."
    return block.group("code")


def test_readme_business_first_quickstart_is_executable(
    monkeypatch,
    capsys,
) -> None:
    captured: dict = {}

    def fake_generate(self, spec):
        captured["spec"] = spec
        return {
            "status": "SUCCESS",
            "artifact": {
                "role": "canonical_ideal_artifact",
                "format": "qasm2",
                "content": "OPENQASM 2.0;",
            },
            "recommended_artifact_role": "canonical_ideal_artifact",
            "construction_verification": {"status": "passed"},
        }

    monkeypatch.setattr(QDSVBridgeClient, "generate", fake_generate)
    exec(compile(_readme_quickstart_code(), "README.md", "exec"), {})

    output = capsys.readouterr().out
    assert "SUCCESS" in output
    assert "canonical_ideal_artifact" in output

    problem = captured["spec"]["problem_spec"]
    dataset = problem["data_binding"]["datasets"][0]
    rows = dataset["rows"]

    assert dataset["index_field"] == "candidate_index"
    assert [row["candidate_index"] for row in rows] == [0, 1, 2]
    assert [row["supplier_id"] for row in rows] == [101, 102, 103]
    assert "supplier_id" not in repr(problem["predicate"])
    assert "expected" not in repr(captured["spec"]).lower()
