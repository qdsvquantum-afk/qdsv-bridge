from __future__ import annotations

import os
import time
from typing import Any, Mapping

import requests

from .exceptions import QDSVBridgeAPIError, QDSVBridgeHTTPError


DEFAULT_API_URL = "https://api.qdsv.cloud/api"
SDK_VERSION = "0.7.0"
SERVICE_UNAVAILABLE_MESSAGE = "QDSV Bridge service is temporarily unavailable. Try again later."
_RETRYABLE_STATUS_CODES = frozenset({429, 502, 503, 504})


class QDSVBridgeClient:
    """Client for QDSV Bridge public API endpoints."""

    def __init__(
        self,
        api_url: str | None = None,
        api_key: str | None = None,
        *,
        timeout: float = 30.0,
        max_retries: int = 2,
        retry_backoff: float = 0.25,
        license_key: str | None = None,
        sdk_name: str = "qdsv-bridge",
    ) -> None:
        self.api_url = self._normalize_api_url(
            api_url or os.getenv("QDSV_BRIDGE_API_URL") or os.getenv("QDSV_API_URL") or DEFAULT_API_URL
        )
        self.api_key = api_key or os.getenv("QDSV_BRIDGE_API_KEY") or os.getenv("QDSV_API_KEY")
        self.license_key = license_key or os.getenv("QDSV_LICENSE_KEY")
        self.timeout = timeout
        if not isinstance(max_retries, int) or max_retries < 0:
            raise ValueError("max_retries must be a non-negative integer.")
        if retry_backoff < 0:
            raise ValueError("retry_backoff must be non-negative.")
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.sdk_name = sdk_name

    @classmethod
    def local(
        cls,
        *,
        api_url: str = "http://localhost:18080/api",
        api_key: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 2,
        retry_backoff: float = 0.25,
        license_key: str | None = None,
    ) -> "QDSVBridgeClient":
        return cls(
            api_url=api_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
            retry_backoff=retry_backoff,
            license_key=license_key,
        )

    @staticmethod
    def _normalize_api_url(value: str) -> str:
        clean = str(value or "").strip().rstrip("/")
        if not clean:
            return DEFAULT_API_URL
        return clean if clean.lower().endswith("/api") else f"{clean}/api"

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
            if payload.get("contract") == "qdsv_bridge_domain.v1":
                delivery = dict(payload.get("delivery") or {})
                delivery["mode"] = mode
                payload["delivery"] = delivery
            else:
                payload["bridge_mode"] = mode
        return payload

    def _request(self, method: str, path: str, *, json: Mapping[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.api_url}{path}"
        kwargs: dict[str, Any] = {"headers": self._headers(), "timeout": self.timeout}
        if json is not None:
            kwargs["json"] = dict(json)
        attempts = self.max_retries + 1
        last_transport_error: requests.RequestException | None = None
        for attempt in range(attempts):
            try:
                response = requests.request(method, url, **kwargs)
            except requests.RequestException as exc:
                last_transport_error = exc
                if attempt + 1 < attempts:
                    self._wait_before_retry(attempt)
                    continue
                raise QDSVBridgeAPIError(SERVICE_UNAVAILABLE_MESSAGE) from exc

            try:
                payload = response.json()
            except ValueError:
                payload = {
                    "detail": {
                        "error_code": "E_BRIDGE_INVALID_RESPONSE",
                        "message": "Bridge service returned an invalid public response.",
                        "detail": {},
                    }
                }
            if response.status_code in _RETRYABLE_STATUS_CODES and attempt + 1 < attempts:
                self._wait_before_retry(attempt)
                continue
            if not response.ok:
                raise QDSVBridgeHTTPError(response.status_code, payload)
            if not isinstance(payload, dict):
                raise QDSVBridgeAPIError("Bridge service returned an unexpected public response.")
            return payload
        raise QDSVBridgeAPIError(SERVICE_UNAVAILABLE_MESSAGE) from last_transport_error

    def _wait_before_retry(self, attempt: int) -> None:
        delay = self.retry_backoff * (2**attempt)
        if delay:
            time.sleep(delay)

    def families(self) -> dict[str, Any]:
        """Compatibility alias for the capability catalog endpoint."""

        return self._request("GET", "/bridge/families")

    def capabilities(self) -> dict[str, Any]:
        """Return operation-level compiler capabilities and service limits."""

        return self._request("GET", "/bridge/capabilities")

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
        """Generate a canonical circuit and optional validated logical child."""

        return self.export(spec, mode="use")

    def build(self, spec: Mapping[str, Any]) -> dict[str, Any]:
        """Return logical artifacts, editable views, evidence and digests."""

        return self.export(spec, mode="build")
