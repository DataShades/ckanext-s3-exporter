from __future__ import annotations

from ckan import types


def update_s3_extracted_resources(
    context: types.Context, data_dict: types.DataDict
) -> types.AuthResult:
    return {"success": False}
