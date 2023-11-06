from __future__ import annotations

from typing import Any

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.s3_exporter import cli, views
from ckanext.s3_exporter.logic import action, auth, validators


class S3ExporterPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IBlueprint)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "s3_exporter")

    # IPackageController

    def after_dataset_update(self, context: dict[str, Any], pkg_dict: dict[str, Any]) -> None:
        if context.get("_s3_exported") or not pkg_dict.get("s3_exporter_object_key"):
            return

        toolkit.get_action("update_s3_extracted_resources")(
            context, {"package_id": pkg_dict["id"]}
        )

    def after_dataset_create(self, context: dict[str, Any], pkg_dict: dict[str, Any]) -> None:
        if context.get("_s3_exported") or not pkg_dict.get("s3_exporter_object_key"):
            return

        toolkit.get_action("update_s3_extracted_resources")(
            {"ignore_auth": True}, {"package_id": pkg_dict["id"]}
        )

    # IClick

    def get_commands(self):
        return cli.get_commands()

    # IValidators

    def get_validators(self):
        return validators.get_validators()

    # IActions

    def get_actions(self):
        return action.get_actions()

    # IAuthFuntion

    def get_auth_functions(self):
        return auth.get_auth_functions()

    # IBlueprint

    def get_blueprint(self):
        return views.get_blueprints()
