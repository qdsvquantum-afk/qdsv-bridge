"""Qiskit adapter for verified public QDSV Bridge artifacts.

The adapter deliberately has two steps: ``export`` asks the remote Bridge
service to produce an artifact, and ``to_quantum_circuit`` verifies and loads
that delivered artifact locally. It contains no local request evaluator,
circuit-construction rules, or transpiler plugin that can contact the service
implicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import re
from typing import Any, Mapping

from .client import QDSVBridgeClient
from .domain import PUBLIC_DOMAIN_CONTRACT
from .exceptions import QDSVBridgeArtifactError


PUBLIC_RESPONSE_CONTRACT = "qdsv_bridge_public.v1"
_DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
_QASM_FORMATS = frozenset({"qasm2", "qasm3"})


@dataclass(frozen=True)
class QDSVBridgeArtifact:
    """A verified public OpenQASM artifact delivered by Bridge.

    Instances are created only from an ``export`` response whose public
    artifact digest matches the exact delivered OpenQASM bytes.
    """

    content: str
    format: str
    language: str
    request_digest: str
    artifact_digest: str
    compiler_build_digest: str
    resources: Mapping[str, Any]
    warnings: tuple[str, ...]

    @classmethod
    def from_public_response(cls, response: Mapping[str, Any]) -> "QDSVBridgeArtifact":
        """Validate a frozen 0.7 public export response before local parsing."""

        if not isinstance(response, Mapping):
            raise QDSVBridgeArtifactError("Bridge export response must be a public JSON object.")
        if response.get("contract") != PUBLIC_RESPONSE_CONTRACT:
            raise QDSVBridgeArtifactError("Bridge export response has an unsupported public contract.")
        if response.get("status") != "SUCCESS":
            raise QDSVBridgeArtifactError("Bridge did not return a successful public artifact.")

        artifact = response.get("artifact")
        digests = response.get("digests")
        verification = response.get("verification")
        if not isinstance(artifact, Mapping) or not isinstance(digests, Mapping) or not isinstance(verification, Mapping):
            raise QDSVBridgeArtifactError("Bridge export response is missing required public artifact fields.")
        if verification.get("status") != "passed" or verification.get("artifact_verified") is not True:
            raise QDSVBridgeArtifactError("Bridge artifact did not pass its public verification status.")

        content = artifact.get("content")
        artifact_format = str(artifact.get("format") or "").lower()
        if not isinstance(content, str) or not content:
            raise QDSVBridgeArtifactError("Bridge artifact has no inline OpenQASM content.")
        if artifact_format not in _QASM_FORMATS:
            raise QDSVBridgeArtifactError(
                "The Qiskit adapter accepts only qasm2 or qasm3 public artifacts."
            )

        request_digest = _require_digest(digests.get("request_digest"), "request_digest")
        artifact_digest = _require_digest(digests.get("artifact_digest"), "artifact_digest")
        compiler_build_digest = _require_digest(
            digests.get("compiler_build_digest"), "compiler_build_digest"
        )
        delivered_digest = "sha256:" + sha256(content.encode("utf-8")).hexdigest()
        if artifact_digest != delivered_digest:
            raise QDSVBridgeArtifactError(
                "Bridge artifact digest does not match the delivered OpenQASM bytes."
            )
        resources = response.get("resources")
        if not isinstance(resources, Mapping):
            raise QDSVBridgeArtifactError("Bridge export response has invalid public resources.")
        warnings = response.get("warnings")
        if not isinstance(warnings, list) or not all(isinstance(item, str) for item in warnings):
            raise QDSVBridgeArtifactError("Bridge export response has invalid public warnings.")
        return cls(
            content=content,
            format=artifact_format,
            language=str(artifact.get("language") or ""),
            request_digest=request_digest,
            artifact_digest=artifact_digest,
            compiler_build_digest=compiler_build_digest,
            resources=dict(resources),
            warnings=tuple(warnings),
        )

    def to_quantum_circuit(self) -> Any:
        """Load this already verified artifact into ``QuantumCircuit``.

        This method never calls Bridge or any other network service.
        """

        return _load_openqasm(self.content, self.format)


class QDSVBridge:
    """Explicit Bridge-to-Qiskit facade.

    Calling :meth:`export` is the only remote operation. Circuit loading is
    separate and works only on the verified public artifact returned by that
    call. The facade rejects non-domain-v1 input rather than accepting any
    lower-level representation.
    """

    def __init__(self, client: QDSVBridgeClient | None = None) -> None:
        self.client = client or QDSVBridgeClient()

    def export(self, request: Mapping[str, Any], *, mode: str | None = None) -> QDSVBridgeArtifact:
        """Request a public artifact from QDSV and verify its delivery digest."""

        if not isinstance(request, Mapping) or request.get("contract") != PUBLIC_DOMAIN_CONTRACT:
            raise QDSVBridgeArtifactError(
                "QDSVBridge accepts only qdsv_bridge_domain.v1 public requests."
            )
        return QDSVBridgeArtifact.from_public_response(self.client.export(request, mode=mode))

    def materialize(self, request: Mapping[str, Any], *, mode: str | None = None) -> Any:
        """Explicitly export from Bridge, verify bytes, then return a QuantumCircuit."""

        return self.export(request, mode=mode).to_quantum_circuit()


def to_quantum_circuit(response: Mapping[str, Any]) -> Any:
    """Compatibility helper that verifies then loads a public export response."""

    return QDSVBridgeArtifact.from_public_response(response).to_quantum_circuit()


def _require_digest(value: Any, name: str) -> str:
    if not isinstance(value, str) or not _DIGEST_PATTERN.fullmatch(value):
        raise QDSVBridgeArtifactError(f"Bridge {name} is not a valid public SHA-256 digest.")
    return value


def _load_openqasm(source: str, artifact_format: str) -> Any:
    try:
        if artifact_format == "qasm2":
            from qiskit import qasm2

            return qasm2.loads(source)
        if artifact_format == "qasm3":
            from qiskit import qasm3

            return qasm3.loads(source)
    except ImportError as exc:
        raise QDSVBridgeArtifactError(
            "Install qdsv-bridge[qiskit] to load Bridge artifacts into Qiskit."
        ) from exc
    except Exception as exc:
        raise QDSVBridgeArtifactError("Qiskit could not load the verified public artifact.") from exc
    raise QDSVBridgeArtifactError(f"Unsupported Qiskit artifact format: {artifact_format}.")


__all__ = [
    "PUBLIC_RESPONSE_CONTRACT",
    "QDSVBridge",
    "QDSVBridgeArtifact",
    "to_quantum_circuit",
]
