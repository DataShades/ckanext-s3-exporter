from __future__ import annotations

import logging
import uuid
from typing import Any

import ckan.plugins.toolkit as tk
from ckan.logic import validate

from ckanext.s3_exporter.utils import run_s3_export
import ckanext.s3_exporter.logic.schema as s3e_schema

logger = logging.getLogger(__name__)
NS = uuid.uuid3(uuid.NAMESPACE_DNS, "s3_exporter")


@validate(s3e_schema.update_s3_extracted_resources_schema)
def update_s3_extracted_resources(context, data_dict):
    """Update/create resources from the s3 bucket for a specific package"""
    tk.check_access("update_s3_extracted_resources", context, data_dict)

    pkg_dict = tk.get_action("package_show")(context, {"id": data_dict["package_id"]})

    if data_dict.get("async", True):
        return _enqueue_export_job(pkg_dict)

    return run_s3_export(pkg_dict)


def _enqueue_export_job(pkg_dict: dict[str, Any]) -> None:
    enqueue_args = {
        "fn": run_s3_export,
        "title": f"s3_exporter - package_id: {pkg_dict['id']}",
        "kwargs": {"pkg_dict": pkg_dict},
    }

    ttl = 3600  # 1 hour ttl.
    rq_kwargs = {"ttl": ttl, "failure_ttl": ttl}
    enqueue_args["rq_kwargs"] = rq_kwargs

    # Optional variable, if not set, default queue is used
    queue: str | None = tk.config.get("ckanext.s3_exporter.queue_name")

    if queue:
        enqueue_args["queue"] = queue

    tk.enqueue_job(run_s3_export, [pkg_dict])


def get_actions():
    return {"update_s3_extracted_resources": update_s3_extracted_resources}
