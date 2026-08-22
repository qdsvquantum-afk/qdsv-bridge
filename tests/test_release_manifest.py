from __future__ import annotations

import qdsv_bridge


def test_release_manifest_matches_package_and_public_contract() -> None:
    manifest = qdsv_bridge.get_release_manifest()

    assert manifest["sdk_version"] == qdsv_bridge.__version__
    assert manifest["contracts"]["bridge"] == "qdsv_bridge_operation_compiler.v2"
    assert (
        manifest["contracts"]["operation_compiler_authority"]
        == "qdsv_operation_compiler.v2"
    )
    assert manifest["conformance"]["bridge_cases"] == {"passed": 10, "total": 10}
    assert manifest["conformance"]["runner_sdk_version"] == "0.6.5"
    assert (
        manifest["conformance"]["archive_sha256"]
        == "4232238f03ff68adac7711b4a523d2ff8e6109abdbad15211c40a33537dfd113"
    )
    assert manifest["boundaries"]["contains_private_compiler"] is False
    assert manifest["boundaries"]["executes_qpu"] is False


def test_release_manifest_is_returned_as_an_independent_value() -> None:
    first = qdsv_bridge.get_release_manifest()
    first["sdk_version"] = "modified"

    assert qdsv_bridge.get_release_manifest()["sdk_version"] == "0.6.6"
