from __future__ import annotations

from hashlib import sha256

import pytest
import requests

import qdsv_bridge
from qdsv_bridge import (
    QDSVBridge,
    QDSVBridgeArtifact,
    QDSVBridgeArtifactError,
    QDSVBridgeClient,
    const,
    field,
    predicate_request,
    select_recommended_artifact,
)
from qdsv_bridge.client import SDK_VERSION
from qdsv_bridge.exceptions import QDSVBridgeAPIError, QDSVBridgeHTTPError


def test_package_version_is_current() -> None:
    assert qdsv_bridge.__version__ == "0.7.3"
    assert SDK_VERSION == qdsv_bridge.__version__


def test_selects_optimized_logical_artifact_when_recommended() -> None:
    result = {
        "artifact": {"role": "canonical_ideal_artifact", "content": "canonical"},
        "optimized_logical_artifact": {
            "role": "optimized_logical_artifact",
            "status": "accepted",
            "content": "optimized",
        },
        "recommended_artifact_role": "optimized_logical_artifact",
    }

    selected = select_recommended_artifact(result)

    assert selected["content"] == "optimized"
    assert result["artifact"]["content"] == "canonical"


def test_recommended_artifact_helper_falls_back_to_canonical() -> None:
    result = {
        "artifact": {"role": "canonical_ideal_artifact", "content": "canonical"},
        "optimized_logical_artifact": {"status": "no_material_improvement"},
        "recommended_artifact_role": "canonical_ideal_artifact",
    }

    assert select_recommended_artifact(result)["content"] == "canonical"


def test_recommended_artifact_helper_rejects_metadata_only_delivery() -> None:
    with pytest.raises(QDSVBridgeAPIError):
        select_recommended_artifact(
            {
                "artifact": {"content": None, "delivery_mode": "metadata_only"},
                "recommended_artifact_role": "canonical_ideal_artifact",
            }
        )


def test_normalizes_api_url() -> None:
    assert QDSVBridgeClient("https://api.qdsv.cloud").api_url == "https://api.qdsv.cloud/api"
    assert QDSVBridgeClient("https://api.qdsv.cloud/api").api_url == "https://api.qdsv.cloud/api"
    assert QDSVBridgeClient.local().api_url == "http://localhost:18080/api"


def test_families_get_has_no_json_body(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {}

    class FakeResponse:
        ok = True
        status_code = 200

        @staticmethod
        def json():
            return {"status": "SUCCESS", "families": {}}

    def fake_request(method, url, **kwargs):
        calls["method"] = method
        calls["url"] = url
        calls["kwargs"] = kwargs
        return FakeResponse()

    monkeypatch.setattr("qdsv_bridge.client.requests.request", fake_request)
    result = QDSVBridgeClient().families()

    assert result["status"] == "SUCCESS"
    assert calls["method"] == "GET"
    assert calls["url"].endswith("/bridge/families")
    assert "json" not in calls["kwargs"]


def test_capabilities_uses_primary_operation_catalog_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {}

    class FakeResponse:
        ok = True
        status_code = 200

        @staticmethod
        def json():
            return {"status": "SUCCESS", "operation_capabilities": {}}

    def fake_request(method, url, **kwargs):
        calls["url"] = url
        return FakeResponse()

    monkeypatch.setattr("qdsv_bridge.client.requests.request", fake_request)
    result = QDSVBridgeClient().capabilities()

    assert result["status"] == "SUCCESS"
    assert calls["url"].endswith("/bridge/capabilities")


def test_composition_capabilities_uses_public_sce_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {}

    class FakeResponse:
        ok = True
        status_code = 200

        @staticmethod
        def json():
            return {
                "status": "SUCCESS",
                "semantic_composition_engine": {
                    "version": "qdsv_semantic_composition_engine.v1",
                    "public_generation_requires_auth": True,
                },
            }

    def fake_request(method, url, **kwargs):
        calls["method"] = method
        calls["url"] = url
        calls["kwargs"] = kwargs
        return FakeResponse()

    monkeypatch.setattr("qdsv_bridge.client.requests.request", fake_request)
    result = QDSVBridgeClient().composition_capabilities()

    assert result["semantic_composition_engine"]["version"] == "qdsv_semantic_composition_engine.v1"
    assert calls["method"] == "GET"
    assert calls["url"].endswith("/product/composition/capabilities")
    assert "json" not in calls["kwargs"]


def test_generate_composition_candidate_posts_public_candidate_request(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {}

    class FakeResponse:
        ok = True
        status_code = 200

        @staticmethod
        def json():
            return {
                "status": "SUCCESS",
                "candidate": {
                    "operation": "policy_gate_score_v1",
                    "state": "OFFICIAL_CANDIDATE",
                    "publication": {"bridge_public": True, "official_without_human_review": False},
                },
                "evidence": {
                    "operation_program_verification": {"status": "passed"},
                    "semantic_cross_check": {"status": "passed", "case_count": 64, "failure_count": 0},
                    "reference_answers_used_for_materialization": False,
                    "reference_answers_used_for_semantic_verification": True,
                },
            }

    def fake_request(method, url, **kwargs):
        calls["method"] = method
        calls["url"] = url
        calls["kwargs"] = kwargs
        return FakeResponse()

    monkeypatch.setattr("qdsv_bridge.client.requests.request", fake_request)
    result = QDSVBridgeClient().generate_composition_candidate(
        name="policy_gate_score_v1",
        description="Select an adjusted score when a threshold predicate is satisfied.",
        expression={
            "op": "select_if",
            "args": [
                {"op": "gte", "args": [{"var": "risk"}, 5]},
                {"op": "add", "args": [{"op": "mul", "args": [{"var": "risk"}, 2]}, {"var": "impact"}]},
                {"var": "impact"},
            ],
        },
        domains=[
            {"type": "int_range", "variable": "risk", "start": 0, "end": 7},
            {"type": "int_range", "variable": "impact", "start": 0, "end": 7},
        ],
        semantic_cross_check_max_cases=128,
    )

    payload = calls["kwargs"]["json"]
    assert result["candidate"]["state"] == "OFFICIAL_CANDIDATE"
    assert result["evidence"]["semantic_cross_check"]["status"] == "passed"
    assert result["evidence"]["reference_answers_used_for_materialization"] is False
    assert calls["method"] == "POST"
    assert calls["url"].endswith("/product/composition/generate")
    assert payload["name"] == "policy_gate_score_v1"
    assert payload["publication_target"] == "internal_candidate"
    assert payload["semantic_cross_check_max_cases"] == 128
    assert payload["domains"][0]["variable"] == "risk"


def test_export_posts_spec(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {}

    class FakeResponse:
        ok = True
        status_code = 200

        @staticmethod
        def json():
            return {"status": "SUCCESS", "artifact": {"format": "qasm3"}}

    def fake_request(method, url, **kwargs):
        calls["method"] = method
        calls["url"] = url
        calls["kwargs"] = kwargs
        return FakeResponse()

    monkeypatch.setattr("qdsv_bridge.client.requests.request", fake_request)
    request = predicate_request(
        candidates=[{"value": 1}],
        rule={"op": "eq", "left": field("value"), "right": const(1)},
    )
    result = QDSVBridgeClient().export(request)

    assert result["artifact"]["format"] == "qasm3"
    assert calls["method"] == "POST"
    assert calls["url"].endswith("/bridge/export")
    assert calls["kwargs"]["json"]["spec"]["contract"] == "qdsv_bridge_domain.v1"


def test_build_keeps_the_public_domain_request_intact(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {}

    class FakeResponse:
        ok = True
        status_code = 200

        @staticmethod
        def json():
            return {"status": "SUCCESS"}

    def fake_request(method, url, **kwargs):
        calls["spec"] = kwargs["json"]["spec"]
        return FakeResponse()

    monkeypatch.setattr("qdsv_bridge.client.requests.request", fake_request)
    spec = predicate_request(
        candidates=[{"value": 1}],
        rule={"op": "eq", "left": field("value"), "right": const(1)},
    )

    QDSVBridgeClient().build(spec)

    assert calls["spec"]["contract"] == "qdsv_bridge_domain.v1"
    assert "problem_spec" not in calls["spec"]


def test_api_key_is_sent_as_header_and_bearer(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {}

    class FakeResponse:
        ok = True
        status_code = 200

        @staticmethod
        def json():
            return {"status": "SUCCESS", "families": {}}

    def fake_request(method, url, **kwargs):
        calls["kwargs"] = kwargs
        return FakeResponse()

    monkeypatch.setattr("qdsv_bridge.client.requests.request", fake_request)

    QDSVBridgeClient(api_key="qdsvb_demo_key").families()

    headers = calls["kwargs"]["headers"]
    assert headers["x-api-key"] == "qdsvb_demo_key"
    assert headers["Authorization"] == "Bearer qdsvb_demo_key"


def test_private_node_transport_error_is_user_friendly(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_request(method, url, **kwargs):
        raise requests.ConnectionError("connection refused")

    monkeypatch.setattr("qdsv_bridge.client.requests.request", fake_request)
    with pytest.raises(QDSVBridgeAPIError) as exc:
        QDSVBridgeClient.local().families()

    assert str(exc.value) == "QDSV Bridge service is temporarily unavailable. Try again later."


def test_http_error_is_not_hidden(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        ok = False
        status_code = 400

        @staticmethod
        def json():
            return {"detail": {"error_code": "E_BRIDGE_UNSUPPORTED_FAMILY"}}

    def fake_request(method, url, **kwargs):
        return FakeResponse()

    monkeypatch.setattr("qdsv_bridge.client.requests.request", fake_request)
    with pytest.raises(QDSVBridgeHTTPError) as exc:
        QDSVBridgeClient.local().families()

    assert exc.value.status_code == 400
    assert exc.value.payload["detail"]["error_code"] == "E_BRIDGE_UNSUPPORTED_FAMILY"
    assert "E_BRIDGE_UNSUPPORTED_FAMILY" in str(exc.value)


def test_retries_retryable_public_service_responses(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    class RetryResponse:
        ok = False
        status_code = 503

        @staticmethod
        def json():
            return {"detail": {"error_code": "E_BRIDGE_UNAVAILABLE"}}

    class SuccessResponse:
        ok = True
        status_code = 200

        @staticmethod
        def json():
            return {"status": "SUCCESS", "families": {}}

    def fake_request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        return RetryResponse() if len(calls) == 1 else SuccessResponse()

    monkeypatch.setattr("qdsv_bridge.client.requests.request", fake_request)
    monkeypatch.setattr("qdsv_bridge.client.time.sleep", lambda _delay: None)

    assert QDSVBridgeClient(max_retries=1).families()["status"] == "SUCCESS"
    assert len(calls) == 2


def test_invalid_non_json_service_body_is_not_exposed(monkeypatch: pytest.MonkeyPatch) -> None:
    class InvalidResponse:
        ok = False
        status_code = 500
        text = "internal stack trace that must not reach callers"

        @staticmethod
        def json():
            raise ValueError("not json")

    monkeypatch.setattr("qdsv_bridge.client.requests.request", lambda *args, **kwargs: InvalidResponse())

    with pytest.raises(QDSVBridgeHTTPError) as exc:
        QDSVBridgeClient(max_retries=0).families()

    assert exc.value.payload["detail"]["error_code"] == "E_BRIDGE_INVALID_RESPONSE"
    assert "stack trace" not in str(exc.value)



def test_export_accepts_mode_argument(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {}

    class FakeResponse:
        ok = True
        status_code = 200

        @staticmethod
        def json():
            return {"status": "SUCCESS", "bridge_mode": "use"}

    def fake_request(method, url, **kwargs):
        calls["kwargs"] = kwargs
        return FakeResponse()

    monkeypatch.setattr("qdsv_bridge.client.requests.request", fake_request)
    request = predicate_request(
        candidates=[{"value": 1}],
        rule={"op": "eq", "left": field("value"), "right": const(1)},
    )
    result = QDSVBridgeClient().export(request, mode="use")

    assert result["bridge_mode"] == "use"
    assert calls["kwargs"]["json"]["spec"]["delivery"]["mode"] == "use"


def test_report_posts_spec_format_and_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {}

    class FakeResponse:
        ok = True
        status_code = 200

        @staticmethod
        def json():
            return {"status": "SUCCESS", "report_format": "markdown", "content": "# QDSV Bridge Report\n"}

    def fake_request(method, url, **kwargs):
        calls["method"] = method
        calls["url"] = url
        calls["kwargs"] = kwargs
        return FakeResponse()

    monkeypatch.setattr("qdsv_bridge.client.requests.request", fake_request)
    request = predicate_request(
        candidates=[{"value": 1}],
        rule={"op": "eq", "left": field("value"), "right": const(1)},
    )
    result = QDSVBridgeClient().report(request, mode="build", format="markdown")

    assert result["report_format"] == "markdown"
    assert calls["method"] == "POST"
    assert calls["url"].endswith("/bridge/report")
    assert calls["kwargs"]["json"]["format"] == "markdown"
    assert calls["kwargs"]["json"]["spec"]["delivery"]["mode"] == "build"


def test_convenience_methods_select_expected_modes(monkeypatch: pytest.MonkeyPatch) -> None:
    modes = []
    requested_specs = []

    class FakeResponse:
        ok = True
        status_code = 200

        @staticmethod
        def json():
            return {"status": "SUCCESS"}

    def fake_request(method, url, **kwargs):
        modes.append(kwargs["json"]["spec"]["delivery"]["mode"])
        requested_specs.append(kwargs["json"]["spec"])
        return FakeResponse()

    monkeypatch.setattr("qdsv_bridge.client.requests.request", fake_request)
    client = QDSVBridgeClient()
    spec = predicate_request(
        candidates=[{"value": 1}],
        rule={"op": "eq", "left": field("value"), "right": const(1)},
    )
    client.generate(spec)
    client.build(spec)

    assert modes == ["use", "build"]
    assert all("problem_spec" not in requested for requested in requested_specs)


def _public_export_response(content: str = "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[1];\n") -> dict:
    artifact_digest = "sha256:" + sha256(content.encode("utf-8")).hexdigest()
    return {
        "contract": "qdsv_bridge_public.v1",
        "status": "SUCCESS",
        "artifact": {
            "format": "qasm2",
            "language": "openqasm2",
            "content": content,
            "materialization_status": "complete",
        },
        "digests": {
            "request_digest": "sha256:" + "1" * 64,
            "artifact_digest": artifact_digest,
        },
        "verification": {"status": "passed", "circuit_materialized": None, "artifact_verified": True},
        "resources": {"logical_qubits": 1},
        "warnings": [],
    }


def test_public_artifact_refuses_digest_mismatch() -> None:
    response = _public_export_response()
    response["digests"]["artifact_digest"] = "sha256:" + "0" * 64

    with pytest.raises(QDSVBridgeArtifactError, match="does not match"):
        QDSVBridgeArtifact.from_public_response(response)


def test_qiskit_facade_only_accepts_domain_v1_and_exports_explicitly() -> None:
    calls = []

    class FakeClient:
        def export(self, request, *, mode=None):
            calls.append((request, mode))
            return _public_export_response()

    bridge = QDSVBridge(FakeClient())
    request = predicate_request(
        candidates=[{"value": 1}],
        rule={"op": "eq", "left": field("value"), "right": const(1)},
    )

    artifact = bridge.export(request, mode="use")

    assert artifact.artifact_digest == _public_export_response()["digests"]["artifact_digest"]
    assert calls == [(request, "use")]
    with pytest.raises(QDSVBridgeArtifactError, match="domain.v1"):
        bridge.export({"problem": {}})


def test_verified_artifact_load_is_separate_from_network(monkeypatch: pytest.MonkeyPatch) -> None:
    artifact = QDSVBridgeArtifact.from_public_response(_public_export_response())
    captured = {}

    def fake_loader(source, artifact_format):
        captured["source"] = source
        captured["format"] = artifact_format
        return "quantum-circuit"

    monkeypatch.setattr("qdsv_bridge.qiskit._load_openqasm", fake_loader)

    assert artifact.to_quantum_circuit() == "quantum-circuit"
    assert captured == {"source": artifact.content, "format": "qasm2"}
