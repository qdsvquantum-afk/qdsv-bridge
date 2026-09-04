"""Verify that a built QDSV Bridge distribution contains only its public SDK.

This checker is intentionally independent from the installed package. It reads
the wheel and source distribution as release consumers would see them and fails
closed for unexpected modules, source trees, or prohibited implementation
markers. It never attempts to inspect or contact a QDSV service.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
from typing import Iterable
import zipfile


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "packaging" / "public-distribution-policy.json"
TEXT_SUFFIXES = {".json", ".md", ".py", ".toml", ".txt"}


class DistributionPolicyError(RuntimeError):
    """Raised if a release archive violates the frozen public boundary."""


def load_policy() -> dict[str, object]:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def file_bytes_from_wheel(archive: zipfile.ZipFile, name: str) -> bytes:
    return archive.read(name)


def file_bytes_from_sdist(archive: tarfile.TarFile, name: str) -> bytes:
    member = archive.getmember(name)
    extracted = archive.extractfile(member)
    if extracted is None:
        return b""
    return extracted.read()


def check_content(name: str, content: bytes, policy: dict[str, object]) -> None:
    if PurePosixPath(name).suffix.lower() not in TEXT_SUFFIXES:
        return
    text = content.decode("utf-8", errors="replace").lower()
    for marker in policy["forbidden_content_markers"]:
        if str(marker).lower() in text:
            raise DistributionPolicyError(f"{name} contains forbidden implementation marker: {marker}")


def check_wheel(path: Path, policy: dict[str, object]) -> dict[str, object]:
    with zipfile.ZipFile(path) as archive:
        names = sorted(name for name in archive.namelist() if not name.endswith("/"))
        package_files = [name.removeprefix("qdsv_bridge/") for name in names if name.startswith("qdsv_bridge/")]
        expected = set(str(name) for name in policy["allowed_package_files"])
        actual = set(package_files)
        unexpected = sorted(actual - expected)
        missing = sorted(expected - actual)
        if unexpected or missing:
            raise DistributionPolicyError(
                f"{path.name} public package files differ from policy; unexpected={unexpected}, missing={missing}"
            )
        if not any(name.endswith(".dist-info/RECORD") for name in names):
            raise DistributionPolicyError(f"{path.name} does not contain a wheel RECORD.")
        for package_file in package_files:
            stem = PurePosixPath(package_file).stem.lower()
            if stem in {str(value).lower() for value in policy["forbidden_module_stems"]}:
                raise DistributionPolicyError(f"{path.name} contains forbidden module name: {package_file}")
        for name in names:
            check_content(name, file_bytes_from_wheel(archive, name), policy)
    return {"artifact": path.name, "kind": "wheel", "files": len(names), "status": "PASS"}


def check_sdist(path: Path, policy: dict[str, object]) -> dict[str, object]:
    with tarfile.open(path, "r:gz") as archive:
        members = [member for member in archive.getmembers() if member.isfile()]
        names = sorted(member.name for member in members)
        roots = {PurePosixPath(name).parts[0] for name in names}
        if len(roots) != 1:
            raise DistributionPolicyError(f"{path.name} must have one source-distribution root; found {sorted(roots)}")
        root = next(iter(roots))
        public_files = set(str(value) for value in policy["allowed_package_files"])
        public_roots = set(str(value) for value in policy["allowed_sdist_root_files"])
        for name in names:
            relative = PurePosixPath(name).relative_to(root)
            parts = relative.parts
            allowed = (
                len(parts) == 1 and parts[0] in public_roots
            ) or (
                len(parts) == 3 and parts[:2] == ("src", "qdsv_bridge") and parts[2] in public_files
            )
            if not allowed:
                raise DistributionPolicyError(f"{path.name} contains unapproved source-distribution member: {relative}")
            if len(parts) == 3 and parts[:2] == ("src", "qdsv_bridge"):
                stem = PurePosixPath(parts[2]).stem.lower()
                if stem in {str(value).lower() for value in policy["forbidden_module_stems"]}:
                    raise DistributionPolicyError(f"{path.name} contains forbidden module name: {relative}")
            check_content(name, file_bytes_from_sdist(archive, name), policy)
    return {"artifact": path.name, "kind": "sdist", "files": len(names), "status": "PASS"}


def find_one(dist_dir: Path, suffix: str) -> Path:
    matches = sorted(dist_dir.glob(suffix))
    if len(matches) != 1:
        raise DistributionPolicyError(f"Expected exactly one {suffix} in {dist_dir}; found {len(matches)}")
    return matches[0]


def verify(dist_dir: Path) -> dict[str, object]:
    policy = load_policy()
    wheel = find_one(dist_dir, "qdsv_bridge-*.whl")
    sdist = find_one(dist_dir, "qdsv_bridge-*.tar.gz")
    checks = [check_wheel(wheel, policy), check_sdist(sdist, policy)]
    return {
        "schema_version": policy["schema_version"],
        "sdk_version": policy["sdk_version"],
        "checks": checks,
        "status": "PASS",
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = verify(args.dist_dir.resolve())
    except DistributionPolicyError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.report.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
