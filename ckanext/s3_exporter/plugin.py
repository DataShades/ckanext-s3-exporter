from __future__ import annotations

from typing import Any

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.types import Context


@toolkit.blanket.cli
@toolkit.blanket.config_declarations
@toolkit.blanket.blueprints
@toolkit.blanket.validators
@toolkit.blanket.auth_functions
@toolkit.blanket.actions
class S3ExporterPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "s3_exporter")

    # IPackageController

    def after_dataset_update(self, context: Context, pkg_dict: dict[str, Any]) -> None:
        if context.get("_s3_exported"):
            return

        toolkit.get_action("update_s3_extracted_resources")(
            context, {"package_id": pkg_dict["id"]}
        )

    def after_dataset_create(self, context: Context, pkg_dict: dict[str, Any]) -> None:
        if context.get("_s3_exported"):
            return

        toolkit.get_action("update_s3_extracted_resources")(
            {"ignore_auth": True}, {"package_id": pkg_dict["id"]}
        )
