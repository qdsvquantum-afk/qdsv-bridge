from __future__ import annotations

from qdsv_bridge import field, score_request


def test_score_request_keeps_prepared_inputs_and_cutoff_in_the_public_contract() -> None:
    request = score_request(
        candidates=[
            {"readiness": 800, "reliability": 700},
            {"readiness": 400, "reliability": 900},
        ],
        decision={"operator": "gte", "threshold": 700},
        criteria=[
            {"name": "readiness", "value": field("readiness"), "importance": 1},
            {"name": "reliability", "value": field("reliability"), "importance": 1},
        ],
    )

    assert request["problem"]["kind"] == "bounded_score"
    assert len(request["problem"]["candidates"]) == 2
    assert request["problem"]["model"]["decision"]["threshold"] == 700
    assert "problem_spec" not in request
    assert "expected" not in repr(request).lower()
