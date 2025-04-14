import fnmatch
import os
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from os.path import isdir, isfile
from typing import List

import yaml
from oci.data_science.data_science_client import DataScienceClient

import mlappcommon
from ml_app_impl_res import MlApplicationImplResource, ImplNotFoundError
from ml_app_instance_res import MlApplicationInstanceResource
from ml_app_res import MlApplicationResource


def validate_directory(purpose: str, directory: str):
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"{purpose} directory '{directory}' does not exist.")


def validate_file(purpose: str, file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"{purpose} file '{file_path}' does not exist.")


def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def validate_yaml_properties(data: dict, mandatory_props: List[str], parent_element: str = None):
    if not all(key in data for key in mandatory_props):
        raise ValueError(f"'{parent_element}' must contain: {', '.join(mandatory_props)}")


def find_files(directory, pattern):
    matched_files = []
    for file_name in os.listdir(directory):
        if fnmatch.fnmatch(file_name, pattern):
            matched_files.append(os.path.join(directory, file_name))
    return matched_files


def unpack_zip(zip_file, destination_dir):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(destination_dir)


def read_impl_version(deployed_artifacts_dir):
    impl_version = None
    with open(os.path.join(deployed_artifacts_dir, "VERSION"), 'r', encoding='utf-8') as file:
        impl_version = file.read()
    if impl_version is None:
        print("Cannot read version from VERSION file")
        sys.exit(1)
    return impl_version


DEFAULT_ENV_FILE_NAME = "default_env"
FULL_PACKAGE_PATTERN = "*-full-package-*.zip"


def get_git_commit_hash():
    # Check for uncommitted changes
    status_output = subprocess.check_output(
        ['git', 'status', '--porcelain', 'package', 'application-def.yaml'])
    if status_output:
        raise ValueError("Cannot build release version of ML Application because of uncommitted changes detected in "
                         "'ml-application/package' directory or"
                         "'ml-application/application-def.yaml'.")

    # Get the current commit revision
    commit_revision = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
    return commit_revision


class MlApplicationProject:
    _env_dir_path: str
    _project_root: str
    _env_config: dict
    _package_args: dict
    _env_name: str
    _ds_client: DataScienceClient = None
    _app_def_env_specific: dict = None

    def __init__(self, project_root: str = None, env_name: str = None, region: str = None, build_only: bool = False):
        if project_root is None:
            project_root = os.getcwd()
            print(f"Application project root not provided. Using working directory: ${project_root}")
        validate_directory("Project root", project_root)
        self._project_root = project_root
        self._env_name = env_name

        if not build_only:
            self._init_environment(env_name, region)

    def _init_environment(self, env_name: str, region: str = None):
        if env_name == "":
            raise ValueError("Provided empty string as environment. To use default environment do not provide "
                             "environment or provide existing environment")
        if env_name is None:
            default_env_config_path = f"{self._project_root}/{DEFAULT_ENV_FILE_NAME}"
            print(
                f"Environment not provided. Trying to find default environment configuration in file {default_env_config_path}")
            try:
                with open(default_env_config_path, 'r', encoding='utf-8') as file:
                    self._env_name = file.read()
                print(f"Found environment '{self._env_name}' in default environment configuration in file")
            except FileNotFoundError:
                raise ValueError("Environment not specified and default configuration file not found")
            self._env_name = self._env_name.strip()
            if self._env_name is None or self._env_name == "":
                raise ValueError("Environment not specified and default configuration file is empty")

        self._env_dir_path = os.path.join(self._project_root, "environments", self._env_name)
        print(f"Environment name used: '{self._env_name}' with path: '{self._env_dir_path}'")
        if not isdir(self._env_dir_path):
            raise ValueError(f"Environment configuration directory '{self._env_dir_path}' is not a directory")

        # Validate required files in environment configuration directory
        required_files = ['arguments.yaml', 'env-config.yaml']
        for file_name in required_files:
            file_path = os.path.join(self._env_dir_path, file_name)
            if not isfile(file_path):
                raise ValueError(f"Error: {file_name} not found in environment configuration directory.")

        # Read environment specific YAML files into variables
        package_args_yaml_path = os.path.join(self._env_dir_path, 'arguments.yaml')
        env_config_yaml_path = os.path.join(self._env_dir_path, 'env-config.yaml')
        self._package_args = mlappcommon.read_yaml(package_args_yaml_path)
        self._env_config = mlappcommon.read_yaml(env_config_yaml_path)
        if region is not None:  # use explicitly configured region if provided
            self._env_config['region'] = region

    @property
    def project_root(self) -> str:
        return self._project_root

    @property
    def env_config(self) -> dict:
        return self._env_config

    @property
    def env_dir_path(self) -> str:
        return self._env_dir_path

    @property
    def env_name(self) -> str:
        return self._env_name

    def get_ds_client(self) -> DataScienceClient:
        if self._ds_client is None:
            self._ds_client = mlappcommon.init_data_science_client(self._env_config)
        return self._ds_client

    def build(self, release: bool):
        package_directory = os.path.join(self._project_root, 'package')
        version_templates_file = os.path.join(self._project_root, 'version_templates.yaml')
        validate_directory("Package", package_directory)

        # load application-def.yaml
        app_def = self.read_application_def()
        app_yaml_data = app_def['application']
        impl_yaml_data = app_def['implementation']

        # Generate ML Application package version
        validate_file("Version template", version_templates_file)
        version_templates = read_yaml_file(version_templates_file)
        validate_yaml_properties(version_templates, ['local', 'release'])
        impl_version = version_templates['release'] if release else version_templates['local']
        if '{git_hash}' in impl_version:
            impl_version = impl_version.replace("{git_hash}", get_git_commit_hash())
        impl_version = impl_version.replace("{timestamp}", datetime.utcnow().strftime("%y%m%d%H%M%S"))

        app_name = app_yaml_data['name']
        impl_name = impl_yaml_data['name']

        target_directory = os.path.join(self._project_root, 'target')
        if os.path.exists(target_directory):
            print("Removing old 'target' directory")
            shutil.rmtree(target_directory)
            print("Old 'target' directory removed successfully")

        target_package_directory = os.path.join(target_directory, 'versioned-impl-package')
        shutil.copytree(package_directory, target_package_directory)

        print(f"Filling version '{impl_version}' in package descriptor file")
        descriptor_file = os.path.join(target_package_directory, 'descriptor.yaml')
        with open(descriptor_file, 'r+') as file:
            descriptor_content = file.read()
            descriptor_content = descriptor_content.replace("{generated-version}", impl_version)
            file.seek(0)
            file.write(descriptor_content)
            file.truncate()

        print(f"Building ML Application Implementation package with version {impl_version} ...")
        zip_file_name = os.path.join(target_directory, mlappcommon.impl_package_file_name(impl_name, impl_version))
        with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(target_package_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, target_package_directory))
        print(f"Successfully built ML Application Implementation package: {zip_file_name}")

        print(f"Building ML Application full package ...")
        full_package_directory = os.path.join(target_directory, 'versioned-full-package')
        os.makedirs(full_package_directory)

        print("   Coping ML Application Implementation package to full package ...")
        shutil.copy(zip_file_name, full_package_directory)
        print("   Coping application-def.yaml to full package ...")
        shutil.copy(os.path.join(self._project_root, 'application-def.yaml'), full_package_directory)
        print("   Creating VERSION file in full package ...")
        with open(os.path.join(full_package_directory, "VERSION"), 'w', encoding='utf-8') as file:
            file.write(impl_version)

        full_zip_file_name = os.path.join(target_directory, mlappcommon.full_package_file_name(app_name, impl_version))
        with zipfile.ZipFile(full_zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(full_package_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, full_package_directory))

        print(f"Successfully built ML Application full package: {full_zip_file_name}")

    def read_application_def(self, app_def_path: str = None) -> dict:
        if app_def_path is None:
            app_def_path = os.path.join(self._project_root, 'application-def.yaml')
        validate_file("application-def.yaml", app_def_path)
        app_def_yaml_data = read_yaml_file(app_def_path)
        validate_yaml_properties(app_def_yaml_data, ['application', 'implementation'], "<root>")
        validate_yaml_properties(app_def_yaml_data['application'], ['name', 'description'], 'application')
        validate_yaml_properties(app_def_yaml_data['implementation'], ['name'], "implementation")
        return app_def_yaml_data

    def get_application_def_project_environment_specific(self) -> dict:
        if self._app_def_env_specific is None:
            app_def = self.read_application_def()
            self._make_app_def_environment_specific(app_def)
            self._app_def_env_specific = app_def
        return self._app_def_env_specific

    def get_application_name_env_specific(self) -> str:
        return self.get_application_def_project_environment_specific()['application']['name']

    def get_implementation_name_env_specific(self) -> str:
        return self.get_application_def_project_environment_specific()['implementation']['name']

    def get_compartment_id_env_specific(self) -> str:
        return self.env_config['environment_compartment_id']

    def _make_app_def_environment_specific(self, app_def_yaml_data: dict) -> None:
        app = app_def_yaml_data['application']
        app["compartment_id"] = self.get_compartment_id_env_specific()
        app['name'] = mlappcommon.append_naming_suffix(app['name'], self._env_config)
        impl = app_def_yaml_data['implementation']
        impl["compartment_id"] = self._env_config["environment_compartment_id"]
        impl['name'] = mlappcommon.append_naming_suffix(impl['name'], self._env_config)

    def deploy(self, full_package_path: str = None):
        if full_package_path is None:
            full_package_path = f"{self._project_root}/target"
            files = find_files(full_package_path, "*-full-package-*.zip")
            count = len(files)
            if count == 0:
                raise ValueError(f"No full package found in {full_package_path}")
            elif count > 1:
                raise ValueError(
                    f"Found multiple full packages: {files}. Please provide full package path to one of them "
                    f"ensure there is only one full package in 'target' directory")
            full_package_path = files[0]
            print(f"Found full package {full_package_path}")

        # Clean up directory for unpacking full application package
        deployment_artifacts_dir = os.path.join(os.path.dirname(full_package_path), 'deployment_artifacts')
        if os.path.exists(deployment_artifacts_dir):
            print("Removing old 'deployment_artifacts' directory")
            shutil.rmtree(deployment_artifacts_dir)
            print("Old 'deployment_artifacts' directory removed successfully")
        os.makedirs(deployment_artifacts_dir, exist_ok=False)

        # Unpack full package
        unpack_zip(full_package_path, deployment_artifacts_dir)
        print(f"Full application package to deploy {full_package_path}")
        print(f"Full application package successfully unpacked into {deployment_artifacts_dir}")

        # Read application and implementation (definition) YAML files into variables
        app_def_yaml_path = os.path.join(deployment_artifacts_dir, "application-def.yaml")

        app_def = self.read_application_def(app_def_yaml_path)
        app = app_def['application']
        impl = app_def['implementation']
        raw_impl_name = impl['name']
        self._make_app_def_environment_specific(app_def)

        impl_version = read_impl_version(deployment_artifacts_dir)
        impl_package_path = os.path.join(deployment_artifacts_dir,
                                         mlappcommon.impl_package_file_name(raw_impl_name, impl_version))
        validate_file("Package version", impl_package_path)

        data_science = self.get_ds_client()

        # Create/Update ML Application
        app_res: MlApplicationResource = MlApplicationResource.create_or_update(data_science, **app)

        # Create/Update ML Application Implementation
        impl['ml_application_id'] = app_res.id
        impl_res: MlApplicationImplResource = MlApplicationImplResource.create_or_update(data_science, **impl)

        # Upload ML Application package
        impl_res.upload_package(impl_package_path, self._package_args)

        print(f"ML Application '{app['name']}' OCID: {app_res.id}")
        print(f"ML Application Implementation '{impl['name']}' OCID: {impl_res.id}")
        print(f"ML Application package version: '{impl_version}'")

    def undeploy(self, remove_instances: bool):
        compartment_id = self.get_compartment_id_env_specific()
        app_name = self.get_application_name_env_specific()
        impl_name = self.get_implementation_name_env_specific()

        print(f"Undeploying ML Application '{app_name}' (with its Implementation '{impl_name}') "
              f"from environment {self._env_name} ...")

        app: MlApplicationResource = MlApplicationResource.find(self.get_ds_client(), app_name, compartment_id)
        try:
            impl: MlApplicationImplResource = MlApplicationImplResource.find(self.get_ds_client(),
                                                                             impl_name,
                                                                             compartment_id)

            if remove_instances:
                instances: List[MlApplicationInstanceResource] = MlApplicationInstanceResource.list_in_compartment(
                    self.get_ds_client(), app.id, compartment_id)
                print(f"Deleting {len(instances)} instance(s) ...")
                for instance in instances:
                    if instance.get_details().lifecycle_state == 'DELETED':
                        continue
                    # TODO this could be done parallel but we would not have logs - we could write logs to file
                    print(f"Deleting instance {instance.id}")
                    instance.delete()
                    print(f"Instance {instance.id} deleted successfully")

            print(f"Deleting implementation '{impl_name}' ({impl.id}) ...")
            impl.delete(idempotent=True)
            print(f"Implementation '{impl_name}' deleted successfully")
        except ImplNotFoundError as e:
            print(e.args[0])

        print(f"Deleting application '{app_name}' ({app.id}) ...")
        app.delete(idempotent=True)
        print(f"Application '{app_name}' deleted successfully")
