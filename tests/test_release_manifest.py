from __future__ import annotations

import qdsv_bridge


def test_release_manifest_matches_package_and_public_contract() -> None:
    manifest = qdsv_bridge.get_release_manifest()

    assert manifest["sdk_version"] == qdsv_bridge.__version__
    assert manifest["contracts"]["domain_request"] == "qdsv_bridge_domain.v1"
    assert manifest["contracts"]["service_response"] == "qdsv_bridge_public.v1"
    assert manifest["boundaries"]["contains_private_compiler"] is False
    assert manifest["boundaries"]["executes_qpu"] is False
    assert manifest["boundaries"]["contains_internal_intermediate_representation"] is False
    assert manifest["boundaries"]["contains_nonpublic_execution_plans"] is False
    assert manifest["qiskit_integration"]["performs_remote_calls_during_transpile"] is False
    assert manifest["distribution_conformance"]["checks_wheel_and_sdist"] is True
    assert manifest["distribution_conformance"]["allows_private_implementation_material"] is False


def test_release_manifest_is_returned_as_an_independent_value() -> None:
    first = qdsv_bridge.get_release_manifest()
    first["sdk_version"] = "modified"

    assert qdsv_bridge.get_release_manifest()["sdk_version"] == "0.7.1"
