from __future__ import annotations

from typing import Any, Dict

from ckan.logic.schema import validator_args

Schema = Dict[str, Any]


@validator_args
def update_s3_extracted_resources_schema(
    ignore_empty, unicode_safe, package_id_or_name_exists
) -> Schema:
    return {
        "package_id": [ignore_empty, unicode_safe, package_id_or_name_exists],
    }
