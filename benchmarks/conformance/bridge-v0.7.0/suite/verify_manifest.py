"""Verify the contents of a released QDSV Bridge conformance package."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys


def digest(path: Path) -> str:
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures: list[str] = []
    for item in manifest["files"]:
        path = root / item["path"]
        if not path.is_file():
            failures.append(f"missing {item['path']}")
        elif digest(path) != item["sha256"]:
            failures.append(f"digest mismatch {item['path']}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
