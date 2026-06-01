from __future__ import annotations

import argparse
import json
from pathlib import Path

from .client import QDSVBridgeClient


def main() -> None:
    parser = argparse.ArgumentParser(description="QDSV Bridge SDK CLI")
    parser.add_argument("command", choices=["families", "validate", "compile", "explain", "export"])
    parser.add_argument("spec", nargs="?", help="Path to a Semantic Circuit Spec JSON file.")
    parser.add_argument("--api-url", default=None)
    parser.add_argument("--local", action="store_true", help="Use http://localhost:18080/api")
    args = parser.parse_args()

    client = QDSVBridgeClient.local() if args.local else QDSVBridgeClient(api_url=args.api_url)
    if args.command == "families":
        print(json.dumps(client.families(), indent=2, ensure_ascii=False))
        return
    if not args.spec:
        parser.error("spec JSON file is required for this command")
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    result = getattr(client, args.command)(spec)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
