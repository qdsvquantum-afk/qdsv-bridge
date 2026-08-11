from __future__ import annotations

from qdsv_bridge import QDSVBridgeClient, build_predicate_spec, select_recommended_artifact


def build_spec() -> dict:
    rows = [
        {"quality": 800, "delivery": 700, "compliance": 1},
        {"quality": 720, "delivery": 600, "compliance": 1},
        {"quality": 690, "delivery": 800, "compliance": 1},
        {"quality": 900, "delivery": 680, "compliance": 0},
    ]
    predicate = {
        "op": "and",
        "args": [
            {
                "op": "gte",
                "left": {"op": "field", "name": "quality"},
                "right": {"op": "const", "value": 700},
            },
            {
                "op": "gte",
                "left": {"op": "field", "name": "delivery"},
                "right": {"op": "const", "value": 650},
            },
            {
                "op": "eq",
                "left": {"op": "field", "name": "compliance"},
                "right": {"op": "const", "value": 1},
            },
        ],
    }
    return build_predicate_spec(rows=rows, predicate=predicate, shots=1024)


def main() -> None:
    result = QDSVBridgeClient().generate(build_spec())
    recommended = select_recommended_artifact(result)
    print(result["status"])
    print(result["artifact"]["format"])
    print(result["recommended_artifact_role"])
    print(recommended["format"])
    print(result["construction_verification"])


if __name__ == "__main__":
    main()
