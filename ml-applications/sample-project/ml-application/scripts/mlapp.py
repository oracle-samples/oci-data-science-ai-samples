import argparse
import fnmatch
import json
import os.path
import sys
import time
from abc import abstractmethod
from os.path import isfile
from typing import List

import oci
from oci.data_science import DataScienceClient
from oci.data_science.models import MlApplicationInstanceView, PredictionUri

import mlappcommon
from ml_app_impl_res import MlApplicationImplResource
from ml_app_instance_res import MlApplicationInstanceResource
from ml_app_project import MlApplicationProject
from ml_app_res import MlApplicationResource

TEST_DATA_INSTANCE_FILE_NAME = "testdata-instance.json"
TEST_DATA_PREDICTION_FILE_NAME = "testdata-prediction.json"

DEFAULT_ENV_FILE_NAME = "default_env"
FULL_PACKAGE_PATTERN = "*-full-package-*.zip"


class CliCommand:
    _error_handler: callable
    _project: MlApplicationProject

    def __init__(self, error_handler: callable, args, project_root: str = None):
        self._args = args
        self._init_app_project(project_root)
        self._error_handler = error_handler

    def _init_app_project(self, project_root: str = None):
        self._project = MlApplicationProject(project_root=project_root,
                                             env_name=self._args.environment,
                                             region=self._args.region)


class BuildCommand(CliCommand):
    _release: bool

    def __init__(self, error_handler: callable, args):
        super().__init__(error_handler, args, args.app_project_root)
        self._release = args.release

    def _init_app_project(self, project_root: str = None):
        self._project = MlApplicationProject(project_root=project_root, build_only=True)

    def execute(self):
        print("Building application project at:", self._project.project_root)
        print("Release build:", self._release)
        self._project.build(self._release)


class DeployCommand(CliCommand):
    _full_package_path: str

    def __init__(self, error_handler: callable, args):
        super().__init__(error_handler, args)
        self._full_package_path = args.full_package_path

    def execute(self):
        print(f"Deploying application package to environment '{self._project.env_name}'")
        self._project.deploy(self._full_package_path)


class UndeployCommand(DeployCommand):
    _cascade: bool
    _force: bool

    def __init__(self, error_handler: callable, args):
        super().__init__(error_handler, args)
        self._cascade = args.cascade_delete
        self._force = args.force

    def execute(self):
        if not self._force:
            self.prompt_to_confirm_undeploy()
        self._project.undeploy(self._cascade)
        print(f"Application undeployed successfully")

    def prompt_to_confirm_undeploy(self):
        try:
            app_name = self._project.get_application_name_env_specific()
            impl_name = self._project.get_implementation_name_env_specific()
            if not mlappcommon.prompt_to_confirm(
                    f"Do you want to proceed with removal of application '{app_name}' and implementation '{impl_name}'?"):
                return
            if self._cascade and not mlappcommon.prompt_to_confirm(f"Do you want to proceed with removal of all the "
                                                                   f"instances as well?"):
                print("Undeploy canceled")
                return
        except FileNotFoundError as e:
            self._error_handler(e)
            return


class CommonTestCommand(CliCommand):
    _app: MlApplicationResource
    _impl: MlApplicationImplResource

    def __init__(self, error_handler: callable, args):
        super().__init__(error_handler, args)
        self._init_test_data()

    def _load_test_data(self, test_data_path) -> dict:
        # parameter is either file name located env directory or file loaded from working directory or absolute path
        if test_data_path is None:
            # set default
            test_data_path = os.path.join(TEST_DATA_INSTANCE_FILE_NAME)

        if os.path.sep not in test_data_path and isfile(os.path.join(self._project.env_dir_path, test_data_path)):
            # file in env config directory
            test_data_path = os.path.join(self._project.env_dir_path, test_data_path)
        elif not isfile(test_data_path):
            self._error_handler("No test data provided")

        with open(test_data_path, 'r') as json_file:
            data: dict = json.load(json_file)
            return data

    def _init_test_data(self):
        # Read application and implementation (definition) YAML files into variables
        app_name = self._project.get_application_name_env_specific()
        impl_name = self._project.get_implementation_name_env_specific()
        compartment_id = self._project.get_compartment_id_env_specific()
        self._app = MlApplicationResource.find(ds_client=self._project.get_ds_client(),
                                               app_name=app_name,
                                               compartment_id=compartment_id)

        self._impl = MlApplicationImplResource.find(ds_client=self._project.get_ds_client(),
                                                    impl_name=impl_name,
                                                    compartment_id=compartment_id)

    def _get_instance_test_data(self):
        instance_test_data = self._load_test_data(self._args.instance_test_data)
        # enrich test data if missing
        mlappcommon.copy_missing_items(source_dict=self._project.env_config,
                                       target_dict=instance_test_data,
                                       key_mapping={"environment_compartment_id": "compartmentId"})
        instance_test_data["mlApplicationId"] = self._app.id
        instance_test_data["mlApplicationImplementationId"] = self._impl.id
        return instance_test_data


class InstantiateCommand(CommonTestCommand):
    def __init__(self, error_handler: callable, args):
        super().__init__(error_handler, args)
        self._test_data_instance = self._get_instance_test_data()

    def execute(self):
        print("Creating ML Application Instance: ")
        print(self._test_data_instance)
        instance: MlApplicationInstanceResource = MlApplicationInstanceResource.create_from_json_dict(
            self._project.get_ds_client(),
            self._test_data_instance)


# Expects instance/instanceView Id XOR displayName (compartmentId taken from impl)
class AdvanceCommonTest(CommonTestCommand):
    _instance_id: str
    _display_name: str
    _compartment_id: str

    def __init__(self, error_handler: callable, args):
        super().__init__(error_handler, args)
        if args.id is not None:
            self._instance_id = mlappcommon.to_instance_ocid(args.id)
        else:
            self._instance_id = None
            test_data_instance = self._get_instance_test_data()
            if args.display_name is not None:
                self._display_name = args.display_name
            else:
                self._display_name = test_data_instance["displayName"]
            if self._display_name is None:
                self._error_handler("Instance ID xor instance displayName (as argument or as part of test data) must "
                                    "be provided.")
            self._compartment_id = test_data_instance["compartmentId"]

    def execute(self):
        instances: List[MlApplicationInstanceResource] = []
        if self._instance_id is not None:
            instances.append(MlApplicationInstanceResource(self._project.get_ds_client(), self._instance_id))
        else:
            instances: List[MlApplicationInstanceResource] = MlApplicationInstanceResource.list_views(
                self._project.get_ds_client(),
                display_name=self._display_name,
                compartment_id=self._compartment_id,
                impl_id=self._impl.id)

        if len(instances) == 0:
            print("No instances found")
            return
        elif len(instances) > 1:
            print("Found multiple instances:")
            for instance in instances:
                print(f"  {instance.id}")
            # TODO should let user to pick which instance should be used

        # TODO we could support parameter --parallel
        for instance in instances:
            print(f"Performing command for instance '{instance.id}'")
            self.execute_test(instance)

    @abstractmethod
    def execute_test(self, instance: MlApplicationInstanceResource):
        raise RuntimeError("Unimplemented abstract method")


class ShowCommand(CommonTestCommand):

    def execute(self):
        self._app.print()
        self._impl.print()
        instances: List[MlApplicationInstanceResource] = MlApplicationInstanceResource.list_views(self._project.get_ds_client(),
                                                                                                  None,
                                                                                                  self._impl.get_details().compartment_id,
                                                                                                  self._impl.id)
        for instance in instances:
            instance.print()


class UninstantiateCommand(AdvanceCommonTest):

    def __init__(self, error_handler: callable, args):
        super().__init__(error_handler, args)

    def execute_test(self, instance: MlApplicationInstanceResource):
        print(f"Deleting ML Application Instance OCID: {instance.id}")
        instance.delete()


class TriggerCommand(AdvanceCommonTest):
    _md_name_to_wait: str
    _trigger_name: str

    def __init__(self, error_handler: callable, args):
        super().__init__(error_handler, args)
        self._test_data_instance = self._get_instance_test_data()
        self._trigger_name = args.trigger_name
        self._md_name_to_wait: str = args.md_name_to_wait


    def execute_test(self, instance: MlApplicationInstanceResource):
        if self._trigger_name is None:
            print("Trigger name not specified. Trying to find trigger name...")
            instance_view: MlApplicationInstanceView = instance.get_view_details()
            print(instance_view.instance_components)
            triggers: List[str] = []
            for instance_component in instance_view.instance_components:
                if isinstance(instance_component, oci.data_science.models.MlApplicationInstanceInternalTrigger):
                    triggers.append(instance_component.name)
            if len(triggers) == 0:
                self._error_handler("No trigger found.")
                sys.exit(1)
            elif len(triggers) > 1:
                self._error_handler(f"Multiple triggers found. Please specify one of {triggers}")
                sys.exit(1)
            self._trigger_name = triggers[0]
        print(f"Calling trigger '{self._trigger_name}' for "
              f"instance view {mlappcommon.to_instance_view_ocid(instance.id)}")
        if self._md_name_to_wait is not None:
            print(f"After trigger finish, this operation will be waiting for update of Model Deployment with name '{self._md_name_to_wait}'")
        try:
            instance.trigger_by_provider(self._trigger_name, self._md_name_to_wait)
        except ValueError as e:
            mlappcommon.print_error(e.args[0], 1)



class PredictCommand(AdvanceCommonTest):
    _prediction_use_case: str
    _prediction_payload: str

    def __init__(self, error_handler: callable, args):
        super().__init__(error_handler, args)
        # TODO allow clever default
        test_data_path = os.path.join(TEST_DATA_PREDICTION_FILE_NAME)
        self._prediction_use_case = args.use_case_name
        if os.path.sep not in test_data_path and isfile(os.path.join(self._project.env_dir_path, test_data_path)):
            # file in env config directory
            test_data_path = os.path.join(self._project.env_dir_path, test_data_path)
        elif not isfile(test_data_path):
            self._error_handler("No test data provided")
        with open(test_data_path, 'r') as file:
            self._prediction_payload = file.read()

    def execute_test(self, instance: MlApplicationInstanceResource):
        if self._prediction_use_case is None:
            uris: List[PredictionUri] = instance.get_prediction_use_cases()
            if uris is None or len(uris) == 0:
                raise ValueError("No prediction use cases found for given ML Application Instance View")
            if len(uris) == 1:
                self._prediction_use_case = uris[0].use_case
            else:
                raise ValueError(f"Prediction use case name must be provided if ML Application has multiple "
                                 f"prediction use cases. Select one of existing use cases: {uris}")
        print(
            f"Calling prediction endpoint for use case '{self._prediction_use_case}' for instance view {mlappcommon.to_instance_view_ocid(instance.id)}")

        response = instance.predict(self._prediction_use_case, self._prediction_payload)
        mlappcommon.print_green_message(f"Prediction response:")
        mlappcommon.print_green_message(f"----------------------------------------------------------------------------")
        mlappcommon.print_green_message(response)
        mlappcommon.print_green_message(f"----------------------------------------------------------------------------")


def main():
    parser = argparse.ArgumentParser(
        description="Command line interface for ML Applications allowing simple building, deployment, testing, supporting multiple deployment environments.")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate command
    # generate_parser = subparsers.add_parser("generate", help="Generate configurations.")
    # generate_subparsers = generate_parser.add_subparsers(dest="subcommand", required=True, help="Generate subcommands")
    # # 'generate environment' subcommand
    # gen_env_parser = generate_subparsers.add_parser("environment", help="Generate environment configuration.")
    # gen_env_parser.add_argument("environment", type=str, help="The environment name to generate.")
    # # 'generate infra_environment' subcommand
    # gen_infra_env_parser = generate_subparsers.add_parser("infra_environment",
    #                                                       help="Generate infrastructure configuration.")
    # gen_infra_env_parser.add_argument("from_environment", type=str,
    #                                   help="The source environment for infra configuration.")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build the application")
    build_parser.add_argument("app_project_root", nargs="?", default=None, help="Application project root (optional)")
    build_parser.add_argument("--release", action="store_true", help="Release build")

    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy the application")
    deploy_parser.add_argument("full_package_path", nargs="?", default=None, help="Path to full application package")

    # Undeploy command
    undeploy_parser = subparsers.add_parser("undeploy", help="Undeploy the application")
    undeploy_parser.add_argument("full_package_path", nargs="?", default=None, help="Path to full application package")
    undeploy_parser.add_argument("--cascade-delete", action="store_true",
                                 help="Turn on cascade delete i.e. it removes all "
                                      "instances then all implementation and then application")
    undeploy_parser.add_argument("--force", action="store_true", help="During force undeployment process "
                                                                      "additional approvals are not required")

    # Trigger command
    trigger_parser = subparsers.add_parser("trigger", help="Trigger ML Application flow")
    trigger_parser.add_argument("trigger_name", nargs="?", default=None, help="Name of trigger")
    trigger_parser.add_argument("--instance-test-data", default=None, help="Test data file name in "
                                                                           "environment configuration directory or path to test data file. "
                                                                           "If not provided testdata-instance.json from environment configuration directory is used.")
    trigger_parser.add_argument("--display-name", default=None,
                                help="ML Application Instance View display name (used only if ID is not provided). It uses compartment of ML Application Implementation.")
    trigger_parser.add_argument("-i", "--id", help="Instance View ID")
    trigger_parser.add_argument("-wmd", "--md-name-to-wait", default=None,
                                help="Display name of Model Deployment for whose successful update finish this command should wait for.")

    # Predict command
    predict_parser = subparsers.add_parser("predict", help="Send prediction request")
    predict_parser.add_argument("use_case_name", nargs="?", default=None, help="Prediction use case name")
    predict_parser.add_argument("--instance-test-data", default=None, help="Test data file name in "
                                                                           "environment configuration directory or path to test data file. "
                                                                           "If not provided testdata-instance.json from environment configuration directory is used.")
    predict_parser.add_argument("--display-name", default=None,
                                help="ML Application Instance View display name (used only if ID is not provided). It uses compartment of ML Application Implementation.")
    predict_parser.add_argument("-i", "--id", help="Instance View ID")

    # Instantiate command
    instantiate_parser = subparsers.add_parser("instantiate",
                                               help="Instantiate ML Application i.e. create ML Application Instance")
    instantiate_parser.add_argument("--instance-test-data", default=None, help="Test data file name in "
                                                                               "environment configuration directory or path to test data file. "
                                                                               "If not provided testdata-instance.json from environment configuration directory is used.")

    # Uninstantiate command
    uninstantiate_parser = subparsers.add_parser("uninstantiate",
                                                 help="Uninstantiate ML Application i.e. delete ML Application Instance")
    uninstantiate_parser.add_argument("--instance-test-data", default=None, help="Test data file name in "
                                                                                 "environment configuration directory or path to test data file. "
                                                                                 "If not provided testdata-instance.json from environment configuration directory is used.")
    uninstantiate_parser.add_argument("--display-name", default=None,
                                      help="ML Application Instance View display name (used only if ID is not provided). It uses compartment of ML Application Implementation.")
    uninstantiate_parser.add_argument("--id", default=None,
                                      help="ID of ML Application Instance or ML Application Instance View")

    # Test command
    # test_parser = subparsers.add_parser("test", help="Test the application")
    # test_parser.add_argument("--test-data", help="Path to test data file")

    # Show command
    show_parser = subparsers.add_parser("show", help="Show details of application, implementation, including instance views")


    for subparser in [deploy_parser, undeploy_parser, trigger_parser, instantiate_parser, uninstantiate_parser,
                      predict_parser, show_parser
                      # test_parser,
                      ]:
        subparser_group = subparser.add_argument_group('common arguments')
        subparser_group.add_argument("-e", "--environment", required=False, default=None, help="Name of environment")
        subparser_group.add_argument("-r", "--region", required=False, default=None, help="Region code")

    args = parser.parse_args()

    def error_handler(msg: str):
        parser.error(msg)
        sys.exit(1)

    try:
        execute_command(error_handler, args)
    except oci.exceptions.ServiceError as e:
        if e.status == 401:
            mlappcommon.print_error(
                "-------------------------------------------------------------------------------------------------------")
            mlappcommon.print_error("  Authentication Error")
            mlappcommon.print_error(
                "-------------------------------------------------------------------------------------------------------")
            mlappcommon.print_error("Possible Issues:")
            mlappcommon.print_error("  - Expired OCI session token: get new session token, example command "
                  "'oci session authenticate --tenancy-name <tenancy> --profile-name <oci_config_profile>'")
            mlappcommon.print_error("  - Invalid API key: check your API key in profile defined in env-config.yaml")
            mlappcommon.print_error(
                "-------------------------------------------------------------------------------------------------------")
            sys.exit(1)
        else:
            raise e


def execute_command(error_handler, args):
    if args.command == "build":
        BuildCommand(error_handler, args).execute()
    elif args.command == "deploy":
        DeployCommand(error_handler, args).execute()
    elif args.command == "undeploy":
        UndeployCommand(error_handler, args).execute()
    elif args.command == "trigger":
        TriggerCommand(error_handler, args).execute()
    elif args.command == "predict":
        PredictCommand(error_handler, args).execute()
    elif args.command == "instantiate":
        InstantiateCommand(error_handler, args).execute()
    elif args.command == "uninstantiate":
        UninstantiateCommand(error_handler, args).execute()
    elif args.command == "show":
        ShowCommand(error_handler, args).execute()
    # elif args.command == "test":
    #     error_handler("Command not supported yet")
        return


if __name__ == "__main__":
    start_time = time.time()

    main()

    total_seconds = round(time.time() - start_time)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    print(f"Command took {hours} hours, {minutes} minutes, and {seconds} seconds")
