from __future__ import annotations

import pytest
import requests

import qdsv_bridge
from qdsv_bridge import QDSVBridgeClient
from qdsv_bridge.exceptions import QDSVBridgeAPIError, QDSVBridgeHTTPError


def test_package_version_is_current() -> None:
    assert qdsv_bridge.__version__ == "0.4.0"


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
    result = QDSVBridgeClient().export({"family": "semantic_signal_classification"})

    assert result["artifact"]["format"] == "qasm3"
    assert calls["method"] == "POST"
    assert calls["url"].endswith("/bridge/export")
    assert calls["kwargs"]["json"]["spec"]["family"] == "semantic_signal_classification"


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

    assert "Private QDSV node temporarily unavailable" in str(exc.value)


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
    result = QDSVBridgeClient().export({"family": "semantic_signal_classification"}, mode="use")

    assert result["bridge_mode"] == "use"
    assert calls["kwargs"]["json"]["spec"]["bridge_mode"] == "use"


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
    result = QDSVBridgeClient().report({"family": "semantic_signal_classification"}, mode="build", format="markdown")

    assert result["report_format"] == "markdown"
    assert calls["method"] == "POST"
    assert calls["url"].endswith("/bridge/report")
    assert calls["kwargs"]["json"]["format"] == "markdown"
    assert calls["kwargs"]["json"]["spec"]["bridge_mode"] == "build"


def test_convenience_methods_select_expected_modes(monkeypatch: pytest.MonkeyPatch) -> None:
    modes = []

    class FakeResponse:
        ok = True
        status_code = 200

        @staticmethod
        def json():
            return {"status": "SUCCESS"}

    def fake_request(method, url, **kwargs):
        modes.append(kwargs["json"]["spec"]["bridge_mode"])
        return FakeResponse()

    monkeypatch.setattr("qdsv_bridge.client.requests.request", fake_request)
    client = QDSVBridgeClient()
    spec = {"family": "semantic_signal_classification"}
    client.generate(spec)
    client.build(spec)
    client.prepare(spec)
    client.evaluate(spec)

    assert modes == ["use", "build", "expert_prepare", "expert_evaluate"]
