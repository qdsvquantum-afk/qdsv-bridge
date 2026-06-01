from __future__ import annotations

import pytest
import requests

from qdsv_bridge import QDSVBridgeClient
from qdsv_bridge.exceptions import QDSVBridgeAPIError, QDSVBridgeHTTPError


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
