from __future__ import annotations

import logging

import boto3
import ckan.plugins.toolkit as tk
import click


logger = logging.getLogger(__name__)

__all__ = ["s3_exporter"]


@click.group()
def s3_exporter():
    pass


@s3_exporter.command()
@click.argument("package_id", required=False)
def update(package_id: str):
    """Update resources from the s3 bucket"""

    result = tk.get_action("package_search")(
        {"ignore_auth": True},
        {
            "fq": f"s3_exporter_object_key:* id:{package_id or '*'}",
            "include_private": True,
        },
    )

    if not result["count"]:
        return click.secho("No datasets")

    for package_dict in result["results"]:
        tk.get_action("update_s3_extracted_resources")(
            {"ignore_auth": True}, {"package_id": package_dict["id"]}
        )


@s3_exporter.command()
def create_mock_data():
    session = boto3.Session(
        aws_access_key_id=tk.config["ckanext.s3_exporter.access_key"],
        aws_secret_access_key=tk.config["ckanext.s3_exporter.secret_key"],
    )

    s3 = session.client("s3")
    folder_key = "test_folder/nested/"
    bucket_name = tk.config["ckanext.s3_exporter.bucket_name"]

    s3.put_object(
        Bucket=bucket_name,
        Key=folder_key,
        Body="",
    )

    # List of mock file names
    file_names = ["file3.csv"]

    for file_name in file_names:
        s3.put_object(
            Bucket=bucket_name,
            Key=folder_key + file_name,
            Body=f"This is the content of {file_name}",
        )


@s3_exporter.command()
@click.argument("file_path", required=True)
def remove_file(file_path: str):
    session = boto3.Session(
        aws_access_key_id=tk.config["ckanext.s3_exporter.access_key"],
        aws_secret_access_key=tk.config["ckanext.s3_exporter.secret_key"],
    )

    session.client("s3").delete_object(
        Bucket=tk.config["ckanext.s3_exporter.bucket_name"], Key=file_path
    )
