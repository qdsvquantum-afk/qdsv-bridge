from __future__ import annotations

from typing import Any, Mapping

from .exceptions import QDSVBridgeAPIError


def select_recommended_artifact(result: Mapping[str, Any]) -> dict[str, Any]:
    """Return the best delivered logical artifact without hiding the canonical one."""

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
