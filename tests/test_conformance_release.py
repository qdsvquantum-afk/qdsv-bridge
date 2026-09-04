from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile


ROOT = Path(__file__).resolve().parents[1]


def test_conformance_release_asset_is_self_verifying(tmp_path: Path) -> None:
    output = tmp_path / "release-assets-a"
    second_output = tmp_path / "release-assets-b"
    subprocess.run(
        [sys.executable, "tools/build_conformance_release.py", "--output", str(output)],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [sys.executable, "tools/build_conformance_release.py", "--output", str(second_output)],
        cwd=ROOT,
        check=True,
    )
    archive = output / "qdsv-bridge-conformance-v0.7.0.tar.gz"
    second_archive = second_output / archive.name
    checksum = (output / "SHA256SUMS").read_text(encoding="utf-8").strip()

    assert archive.is_file()
    assert archive.read_bytes() == second_archive.read_bytes()
    assert checksum == f"{hashlib.sha256(archive.read_bytes()).hexdigest()}  {archive.name}"
    with tarfile.open(archive, "r:gz") as tar:
        members = {member.name for member in tar.getmembers() if member.isfile()}
        manifest = json.loads(tar.extractfile("qdsv-bridge-conformance-v0.7.0/manifest.json").read())

    assert "qdsv-bridge-conformance-v0.7.0/schema/conformance-report.schema.json" in members
    assert "qdsv-bridge-conformance-v0.7.0/suite/verify_manifest.py" in members
    assert manifest["private_compiler_access"] is False
    assert manifest["expected_outputs_sent_to_bridge"] is False


def test_release_checksums_have_stable_names_and_digests(tmp_path: Path) -> None:
    first = tmp_path / "qdsv_bridge-0.7.0-py3-none-any.whl"
    second = tmp_path / "qdsv-bridge-conformance-v0.7.0.tar.gz"
    first.write_bytes(b"wheel")
    second.write_bytes(b"conformance")
    output = tmp_path / "RELEASE-SHA256SUMS"

    subprocess.run(
        [
            sys.executable,
            "tools/write_release_checksums.py",
            "--output",
            str(output),
            str(second),
            str(first),
        ],
        cwd=ROOT,
        check=True,
    )

    assert output.read_text(encoding="utf-8") == (
        f"{hashlib.sha256(second.read_bytes()).hexdigest()}  {second.name}\n"
        f"{hashlib.sha256(first.read_bytes()).hexdigest()}  {first.name}\n"
    )
