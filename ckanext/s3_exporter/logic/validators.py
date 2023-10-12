from typing import Any

import ckan.plugins.toolkit as tk
import ckan.types as types


def is_valid_s3_filepath(value: str, context: types.Context) -> Any:
    if not value.endswith("/"):
        raise tk.Invalid(f"Invalid s3 filepath: {value}")

    return value
