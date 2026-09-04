"""Build the independently distributable QDSV Bridge 0.7.0 conformance asset."""

from __future__ import annotations

import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tarfile
import tempfile
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "benchmarks" / "conformance" / "bridge-v0.7.0"
PACKAGE_NAME = "qdsv-bridge-conformance-v0.7.0"
INCLUDED_ROOT_FILES = ("Dockerfile", "README.md", "requirements.lock")
INCLUDED_DIRECTORIES = ("fixtures", "schema", "spec", "suite")


def sha256_file(path: Path) -> str:
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def iter_package_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file() and "__pycache__" not in path.parts)


def copy_source(destination: Path) -> None:
    for name in INCLUDED_ROOT_FILES:
        shutil.copy2(SOURCE / name, destination / name)
    for name in INCLUDED_DIRECTORIES:
        shutil.copytree(
            SOURCE / name,
            destination / name,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )


def write_manifest(destination: Path) -> None:
    files = []
    for path in iter_package_files(destination):
        relative = path.relative_to(destination).as_posix()
        if relative == "manifest.json":
            continue
        files.append({"path": relative, "sha256": sha256_file(path)})
    manifest = {
        "schema_version": "qdsv_bridge_conformance_package.v0.7",
        "package": PACKAGE_NAME,
        "sdk_version": "0.7.0",
        "contracts": {
            "domain": "qdsv_bridge_domain.v1",
            "response": "qdsv_bridge_public.v1"
        },
        "verifier_only_expected_outputs": True,
        "expected_outputs_sent_to_bridge": False,
        "private_compiler_access": False,
        "files": files,
    }
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_checksum(path: Path, output: Path) -> None:
    output.write_text(f"{sha256_file(path).removeprefix('sha256:')}  {path.name}\n", encoding="utf-8")


def add_deterministic_archive(archive: Path, package_root: Path) -> None:
    """Create a byte-reproducible gzip tarball from the frozen profile."""

    with archive.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as tar:
                root_info = tarfile.TarInfo(PACKAGE_NAME)
                root_info.type = tarfile.DIRTYPE
                root_info.mode = 0o755
                root_info.uid = root_info.gid = 0
                root_info.uname = root_info.gname = ""
                root_info.mtime = 0
                tar.addfile(root_info)
                for path in iter_package_files(package_root):
                    relative = path.relative_to(package_root).as_posix()
                    info = tarfile.TarInfo(f"{PACKAGE_NAME}/{relative}")
                    info.size = path.stat().st_size
                    info.mode = 0o644
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    info.mtime = 0
                    with path.open("rb") as source:
                        tar.addfile(info, source)


def build(output: Path) -> tuple[Path, Path]:
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"{PACKAGE_NAME}.tar.gz"
    checksums = output / "SHA256SUMS"
    with tempfile.TemporaryDirectory(prefix="qdsv-conformance-") as temporary:
        package_root = Path(temporary) / PACKAGE_NAME
        package_root.mkdir()
        copy_source(package_root)
        write_manifest(package_root)
        add_deterministic_archive(archive, package_root)
    write_checksum(archive, checksums)
    return archive, checksums


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    archive, checksums = build(args.output.resolve())
    print(archive)
    print(checksums)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
