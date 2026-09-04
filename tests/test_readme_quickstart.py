from __future__ import annotations

import re
from pathlib import Path

from qdsv_bridge import QDSVBridge, QDSVBridgeArtifact


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

    def fake_export(self, spec):
        captured["spec"] = spec
        return QDSVBridgeArtifact(
            content="OPENQASM 2.0;",
            format="qasm2",
            language="openqasm2",
            request_digest="sha256:" + "1" * 64,
            artifact_digest="sha256:" + "2" * 64,
            compiler_build_digest="sha256:" + "3" * 64,
            resources={},
            warnings=(),
        )

    monkeypatch.setattr(QDSVBridge, "export", fake_export)
    exec(compile(_readme_quickstart_code(), "README.md", "exec"), {})

    output = capsys.readouterr().out
    assert "qasm2" in output
    assert "sha256:" in output

    request = captured["spec"]
    assert request["contract"] == "qdsv_bridge_domain.v1"
    assert [row["supplier_id"] for row in request["problem"]["candidates"]] == [101, 102, 103]
    assert request["problem"]["candidate_id_field"] == "candidate_index"
    assert "problem_spec" not in request
    assert "expected" not in repr(request).lower()
