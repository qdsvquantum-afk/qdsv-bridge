from __future__ import annotations

from typing import Any, Mapping

from .exceptions import QDSVBridgeAPIError


def select_recommended_artifact(result: Mapping[str, Any]) -> dict[str, Any]:
    """Return the recommended inline logical artifact.

    The canonical artifact remains available in ``result["artifact"]``. This
    helper returns an accepted optimized child only when
    ``recommended_artifact_role`` selects it and inline content is present;
    otherwise it returns the canonical inline artifact.

    Args:
        result: A Bridge ``generate`` or ``build`` response.

    Returns:
        A copy of the recommended inline artifact mapping.

    Raises:
        QDSVBridgeAPIError: If neither recommended nor canonical circuit
            content is available inline.
    """

    role = str(result.get("recommended_artifact_role") or "canonical_ideal_artifact")
    if role == "optimized_logical_artifact":
        optimized = result.get("optimized_logical_artifact")
        if isinstance(optimized, Mapping) and isinstance(optimized.get("content"), str):
            return dict(optimized)
    canonical = result.get("artifact")
    if isinstance(canonical, Mapping) and isinstance(canonical.get("content"), str):
        return dict(canonical)
    raise QDSVBridgeAPIError(
        "The recommended Bridge artifact is not available inline. Inspect artifact_delivery and digests."
    )


__all__ = ["select_recommended_artifact"]
