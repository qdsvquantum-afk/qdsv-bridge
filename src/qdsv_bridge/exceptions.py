from __future__ import annotations

from typing import Any


class QDSVBridgeError(Exception):
    """Base exception for the QDSV Bridge SDK."""


class QDSVBridgeHTTPError(QDSVBridgeError):
    """Raised when the API returns an HTTP error response."""

    def __init__(self, status_code: int, payload: Any) -> None:
        self.status_code = status_code
        self.payload = payload
        super().__init__(f"QDSV Bridge API HTTP {status_code}: {payload}")


class QDSVBridgeAPIError(QDSVBridgeError):
    """Raised when a transport error prevents calling the API."""
