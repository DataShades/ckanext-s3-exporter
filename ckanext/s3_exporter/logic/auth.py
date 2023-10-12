from __future__ import annotations

from typing import Any


def update_s3_extracted_resources(
    context: dict[str, Any], data_dict: dict[str, Any]
) -> dict[str, bool]:
    return {"success": False}


def get_auth_functions():
    return {"update_s3_extracted_resources": update_s3_extracted_resources}
