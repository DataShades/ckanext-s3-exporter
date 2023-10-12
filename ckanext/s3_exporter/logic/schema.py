from __future__ import annotations


from ckan.logic.schema import validator_args


@validator_args
def update_s3_extracted_resources_schema(
    ignore_empty, unicode_safe, package_id_or_name_exists, boolean_validator
):
    return {
        "package_id": [ignore_empty, unicode_safe, package_id_or_name_exists],
        "async": [ignore_empty, boolean_validator]
    }
