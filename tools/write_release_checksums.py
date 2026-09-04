"""Write a stable SHA-256 manifest for the public release files."""

from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
from typing import Iterable


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def write_manifest(output: Path, inputs: Iterable[Path]) -> None:
    files = sorted((path.resolve() for path in inputs), key=lambda path: path.name)
    if not files or any(not path.is_file() for path in files):
        raise ValueError("all release inputs must be existing files")
    names = [path.name for path in files]
    if len(set(names)) != len(names):
        raise ValueError("release inputs must have unique file names")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "".join(f"{digest(path)}  {path.name}\n" for path in files),
        encoding="utf-8",
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("inputs", type=Path, nargs="+")
    args = parser.parse_args(argv)
    write_manifest(args.output.resolve(), args.inputs)
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
