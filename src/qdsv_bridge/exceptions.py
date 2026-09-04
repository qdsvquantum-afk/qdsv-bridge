from __future__ import annotations

from typing import Any


class QDSVBridgeError(Exception):
    """Base exception for the QDSV Bridge SDK."""


class QDSVBridgeHTTPError(QDSVBridgeError):
    """Raised when the API returns an HTTP error response."""

    def __init__(self, status_code: int, payload: Any) -> None:
        self.status_code = status_code
        self.payload = payload
        error_code = "unknown_error"
        if isinstance(payload, dict):
            detail = payload.get("detail")
            if isinstance(detail, dict) and isinstance(detail.get("error_code"), str):
                error_code = detail["error_code"]
        super().__init__(f"QDSV Bridge API HTTP {status_code} ({error_code}).")


class QDSVBridgeAPIError(QDSVBridgeError):
    """Raised when a transport error prevents calling the API."""


class QDSVBridgeArtifactError(QDSVBridgeError):
    """Raised when a public artifact cannot be verified or loaded safely."""
