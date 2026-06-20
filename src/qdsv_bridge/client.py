from __future__ import annotations

import os
from typing import Any, Mapping

import requests

from .exceptions import QDSVBridgeAPIError, QDSVBridgeHTTPError


DEFAULT_API_URL = "https://api.qdsv.cloud/api"
SDK_VERSION = "0.1.5"
PRIVATE_NODE_UNAVAILABLE_MESSAGE = (
    "Private QDSV node temporarily unavailable. It may be offline, reserved for "
    "private processing, or busy. Try again later or use QDSVBridgeClient() for "
    "public cloud examples."
)


class QDSVBridgeClient:
    """Client for QDSV Bridge public API endpoints."""

    def __init__(
        self,
        api_url: str | None = None,
        api_key: str | None = None,
        *,
        timeout: float = 30.0,
        license_key: str | None = None,
        sdk_name: str = "qdsv-bridge",
    ) -> None:
        self.api_url = self._normalize_api_url(
            api_url or os.getenv("QDSV_BRIDGE_API_URL") or os.getenv("QDSV_API_URL") or DEFAULT_API_URL
        )
        self.api_key = api_key or os.getenv("QDSV_BRIDGE_API_KEY") or os.getenv("QDSV_API_KEY")
        self.license_key = license_key or os.getenv("QDSV_LICENSE_KEY")
        self.timeout = timeout
        self.sdk_name = sdk_name
        self._private_node = self._looks_like_private_node(self.api_url)

    @classmethod
    def local(
        cls,
        *,
        api_url: str = "http://localhost:18080/api",
        api_key: str | None = None,
        timeout: float = 30.0,
        license_key: str | None = None,
    ) -> "QDSVBridgeClient":
        return cls(api_url=api_url, api_key=api_key, timeout=timeout, license_key=license_key)

    @staticmethod
    def _normalize_api_url(value: str) -> str:
        clean = str(value or "").strip().rstrip("/")
        if not clean:
            return DEFAULT_API_URL
        return clean if clean.lower().endswith("/api") else f"{clean}/api"

    @staticmethod
    def _looks_like_private_node(api_url: str) -> bool:
        clean = str(api_url or "").lower()
        return "localhost" in clean or "127.0.0.1" in clean or "qintent-local.qdsv.cloud" in clean or "qruba.site" in clean

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "x-sdk-name": self.sdk_name,
            "x-sdk-version": SDK_VERSION,
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
            headers["Authorization"] = f"Bearer {self.api_key}"
        if self.license_key:
            headers["x-license-key"] = self.license_key
        return headers

    @staticmethod
    def _spec_with_mode(spec: Mapping[str, Any], mode: str | None = None) -> dict[str, Any]:
        payload = dict(spec)
        if mode:
            payload["bridge_mode"] = mode
        return payload

    def _request(self, method: str, path: str, *, json: Mapping[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.api_url}{path}"
        kwargs: dict[str, Any] = {"headers": self._headers(), "timeout": self.timeout}
        if json is not None:
            kwargs["json"] = dict(json)
        try:
            response = requests.request(method, url, **kwargs)
        except requests.RequestException as exc:
            if self._private_node:
                raise QDSVBridgeAPIError(PRIVATE_NODE_UNAVAILABLE_MESSAGE) from exc
            raise QDSVBridgeAPIError(str(exc)) from exc
        try:
            payload = response.json()
        except ValueError:
            payload = {"status": "ERROR", "message": response.text}
        if not response.ok:
            raise QDSVBridgeHTTPError(response.status_code, payload)
        if not isinstance(payload, dict):
            raise QDSVBridgeAPIError(f"Unexpected API response type: {type(payload).__name__}")
        return payload

    def families(self) -> dict[str, Any]:
        return self._request("GET", "/bridge/families")

    def validate(self, spec: Mapping[str, Any], *, mode: str | None = None) -> dict[str, Any]:
        return self._request("POST", "/bridge/validate", json={"spec": self._spec_with_mode(spec, mode)})

    def compile(self, spec: Mapping[str, Any], *, mode: str | None = None) -> dict[str, Any]:
        return self._request("POST", "/bridge/compile", json={"spec": self._spec_with_mode(spec, mode)})

    def explain(self, spec: Mapping[str, Any], *, mode: str | None = None) -> dict[str, Any]:
        return self._request("POST", "/bridge/explain", json={"spec": self._spec_with_mode(spec, mode)})

    def export(self, spec: Mapping[str, Any], *, mode: str | None = None) -> dict[str, Any]:
        return self._request("POST", "/bridge/export", json={"spec": self._spec_with_mode(spec, mode)})

    def report(self, spec: Mapping[str, Any], *, mode: str | None = None, format: str = "markdown") -> dict[str, Any]:
        """Generate a shareable Bridge Report in markdown, html or json format."""

        return self._request(
            "POST",
            "/bridge/report",
            json={"spec": self._spec_with_mode(spec, mode), "format": format},
        )

    def generate(self, spec: Mapping[str, Any]) -> dict[str, Any]:
        """Basic-user mode: generate a new circuit package from the problem."""

        return self.export(spec, mode="use")

    def build(self, spec: Mapping[str, Any]) -> dict[str, Any]:
        """Intermediate mode: generated circuit plus editable QASM/Qiskit/IR artifacts."""

        return self.export(spec, mode="build")

    def prepare(self, spec: Mapping[str, Any]) -> dict[str, Any]:
        """Expert-constructor mode: semantic inputs for designing a custom circuit."""

        return self.export(spec, mode="expert_prepare")

    def evaluate(self, spec: Mapping[str, Any]) -> dict[str, Any]:
        """Expert-evaluator mode: suggested QDSV materialization and variants."""

        return self.export(spec, mode="expert_evaluate")
