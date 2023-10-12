from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk


def is_valid_s3_filepath(value: str, context: dict[str, Any]) -> Any:
    if not value.endswith("/"):
        raise tk.Invalid(f"Invalid s3 filepath: {value}")

    return value


def get_validators():
    return {"is_valid_s3_filepath": is_valid_s3_filepath}
