from __future__ import annotations

import argparse
import json
from pathlib import Path

from .client import QDSVBridgeClient


def main() -> None:
    parser = argparse.ArgumentParser(description="QDSV Bridge SDK CLI")
    parser.add_argument("command", choices=["capabilities", "families", "validate", "compile", "explain", "export", "report"])
    parser.add_argument("spec", nargs="?", help="Path to a Semantic Circuit Spec JSON file.")
    parser.add_argument("--api-url", default=None)
    parser.add_argument("--api-key", default=None, help="Optional QDSV Bridge API key")
    parser.add_argument("--license-key", default=None, help="Optional QDSV/Qruba license key")
    parser.add_argument("--local", action="store_true", help="Use http://localhost:18080/api")
    parser.add_argument(
        "--mode",
        choices=["use", "build", "expert_prepare", "expert_evaluate"],
        default=None,
        help="Bridge output depth: basic use, intermediate build, expert construction inputs, or expert evaluation.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown", "md", "html"],
        default="markdown",
        help="Bridge Report format when command=report.",
    )
    parser.add_argument("--output", default=None, help="Optional output path for Bridge Report content.")
    args = parser.parse_args()

    client = (
        QDSVBridgeClient.local(api_key=args.api_key, license_key=args.license_key)
        if args.local
        else QDSVBridgeClient(api_url=args.api_url, api_key=args.api_key, license_key=args.license_key)
    )
    if args.command in {"capabilities", "families"}:
        print(json.dumps(client.capabilities(), indent=2, ensure_ascii=False))
        return
    if not args.spec:
        parser.error("spec JSON file is required for this command")
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    method = getattr(client, args.command)
    if args.command == "report":
        result = client.report(spec, mode=args.mode, format=args.format)
        if args.output:
            content = result["content"]
            output_path = Path(args.output)
            if isinstance(content, str):
                output_path.write_text(content, encoding="utf-8")
            else:
                output_path.write_text(json.dumps(content, indent=2, ensure_ascii=False), encoding="utf-8")
            print(str(output_path))
            return
    elif args.command in {"validate", "compile", "explain", "export"}:
        result = method(spec, mode=args.mode)
    else:
        result = method(spec)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
