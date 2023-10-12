from __future__ import annotations

import logging
import uuid
from typing import Any, cast

import boto3
import ckan.plugins.toolkit as tk
from ckan import types

from ckanext.s3_exporter.const import FLAKE_EXPORTED, S3E_DOWNLOAD

logger = logging.getLogger(__name__)
NS = uuid.uuid3(uuid.NAMESPACE_DNS, "s3_exporter")


def run_s3_export(pkg_dict: dict[str, Any]):
    """Run an export of resources from s3 bucket and add them into the specific
    package"""
    logger.info(f"Starting s3 re-export for package: {pkg_dict['id']}")

    context = cast(types.Context, {"ignore_auth": True, "_s3_exported": True})
    s3_folder = pkg_dict["s3_exporter_object_key"]
    package_id = pkg_dict["id"]

    resources = list_objects_in_folder(
        "" if s3_folder == "/" else s3_folder, package_id
    )
    grouped_resources = {resource["id"]: resource for resource in resources}
    existing_resources = pkg_dict.get("resources", [])

    store_exported_resources(grouped_resources, package_id)

    logger.info(f"Found {len(resources)} resource(s) for package: {pkg_dict['id']}")

    for resource in resources:
        resource["package_id"] = package_id
        existing_resource = _get_existing_resource(resource["id"], existing_resources)

        # there's no real reason to update resource, because we are not storing
        # the real data. So if the resource has changed on bucket, it should
        # have updated metadata_modified.
        if (
            existing_resource
            and resource["metadata_modified"] != existing_resource["metadata_modified"]
        ):
            tk.get_action("resource_update")(context, resource)
        else:
            tk.get_action("resource_create")(context, resource)

    for resource in existing_resources:
        if (
            resource["id"] not in grouped_resources
            # exported from bucket resource has this in URL
            # do not touch resources that user has created manually
            and S3E_DOWNLOAD in resource["url"]
        ):
            logger.info(
                f"Removing exported resource '{resource['name']}' for package "
                f"{pkg_dict['id']} as it's not under {s3_folder} object key"
            )
            tk.get_action("resource_delete")(context, {"id": resource["id"]})

    logger.info(f"Finished s3 re-export for package: {pkg_dict['id']}")

    return resources


def _get_existing_resource(
    resource_id: str, existing_resources: list[dict[str, Any]]
) -> dict[str, Any] | None:
    for resource in existing_resources:
        if resource["id"] == resource_id:
            return resource


def list_objects_in_folder(prefix, package_id: str):
    session = boto3.Session(
        aws_access_key_id=tk.config["ckanext.s3_exporter.access_key"],
        aws_secret_access_key=tk.config["ckanext.s3_exporter.secret_key"],
    )

    bucket = tk.config["ckanext.s3_exporter.bucket_name"]
    s3 = session.client("s3")

    paginator = s3.get_paginator("list_objects_v2")

    resources = []

    for result in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for object in result.get("Contents", []):
            if object["Key"] == prefix:
                continue

            # If the object key ends with a '/', it's a "folder," so recursively
            # traverse objects in it.
            if object["Key"].endswith("/"):
                list_objects_in_folder(object["Key"], package_id)
            else:
                resources.append(_fetch_resource_metadata(object, package_id))

    return resources


def _fetch_resource_metadata(object: dict[str, Any], package_id: str) -> dict[str, Any]:
    resource_id = str(uuid.uuid3(NS, package_id + object["Key"]))

    return {
        "id": resource_id,
        "name": object["Key"].split("/")[-1],
        "size": object["Size"],
        "metadata_modified": object["LastModified"].strftime("%Y-%m-%d %H:%M:%S"),
        "key": object["Key"],
        "format": _parse_format_from_resource_name(object["Key"]),
        "url": tk.url_for(
            "s3_exporter.download",
            package_id=package_id,
            resource_id=resource_id,
            _external=True,
        ),
    }


def _parse_format_from_resource_name(resource_name: str) -> str:
    parts = resource_name.split(".")

    return parts[-1] if len(parts) >= 2 else "data"


def store_exported_resources(
    data: dict[str, dict[str, Any]], package_id: str
) -> dict[str, Any]:
    return tk.get_action("flakes_flake_override")(
        {"ignore_auth": True},
        {
            "author_id": None,
            "name": FLAKE_EXPORTED.format(package_id),
            "data": data,
        },
    )


def get_exported_resources(package_id: str) -> dict[str, dict[str, Any]]:
    try:
        return tk.get_action("flakes_flake_lookup")(
            {"ignore_auth": True},
            {"author_id": None, "name": FLAKE_EXPORTED.format(package_id)},
        )["data"]
    except tk.ObjectNotFound:
        return tk.get_action("flakes_flake_create")(
            {"ignore_auth": True},
            {
                "author_id": None,
                "name": FLAKE_EXPORTED.format(package_id),
                "data": {},
            },
        )["data"]
