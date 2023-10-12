import boto3
import ckan.plugins.toolkit as tk
from flask import Blueprint

from ckanext.s3_exporter.utils import get_exported_resources
from ckanext.s3_exporter.const import S3E_DOWNLOAD

s3_exporter = Blueprint("s3_exporter", __name__)


@s3_exporter.route(f"/dataset/<package_id>/resource/<resource_id>/{S3E_DOWNLOAD}")
def download(package_id, resource_id):
    resources = get_exported_resources(package_id)

    if resource_id not in resources:
        tk.h.flash_error(tk._("Error. The resource is not exported from s3"))
        return tk.redirect_to(
            "dataset_resource.read", id=package_id, resource_id=resource_id
        )

    data = resources[resource_id]

    session = boto3.Session(
        aws_access_key_id=tk.config["ckanext.s3_exporter.access_key"],
        aws_secret_access_key=tk.config["ckanext.s3_exporter.secret_key"],
    )

    url = session.client("s3").generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": tk.config["ckanext.s3_exporter.bucket_name"],
            "Key": data["key"],
        },
    )

    return tk.redirect_to(url)


def get_blueprints():
    return [s3_exporter]
