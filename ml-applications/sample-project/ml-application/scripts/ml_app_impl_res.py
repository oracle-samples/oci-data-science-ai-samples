import json
from typing import List

import oci
from oci.data_science import DataScienceClient
from oci.data_science.models import MlApplicationImplementation, MlApplicationImplementationSummary
from oci.response import Response

import mlappcommon
from work_request import WorkRequestResource


class MlApplicationImplResource:
    _ds_client: DataScienceClient

    def __init__(self, ds_client: DataScienceClient, impl_id: str):
        self._ds_client = ds_client
        self._id = impl_id

    @staticmethod
    def create_or_update(ds_client, **impl) -> 'MlApplicationImplResource':
        print(f"Searching for ML Application Implementation with name: '{impl['name']}' "
              f"for ML Application: '{impl['ml_application_id']}' "
              f"in compartment: '{impl['compartment_id']}'")
        list_impl_response = ds_client.list_ml_application_implementations(
            compartment_id=impl["compartment_id"],
            ml_application_id=impl["ml_application_id"],
            name=impl["name"]
        )
        print(list_impl_response.data)
        mlappcommon.add_hash_tag(impl)
        impl_id = None
        if len(list_impl_response.data.items) == 1:
            # check whether existing implementation has same version
            current_impl_summary: MlApplicationImplementationSummary = list_impl_response.data.items[0]
            impl_id = current_impl_summary.id
            if current_impl_summary.freeform_tags.get('hash') == impl.get('freeform_tags')['hash']:
                return MlApplicationImplResource(ds_client, impl_id)

            # ML Application Implementation already exists with different version -> update it
            allowed_nonactive_states = [
                oci.data_science.models.MlApplicationImplementation.LIFECYCLE_STATE_NEEDS_ATTENTION,
                oci.data_science.models.MlApplicationImplementation.LIFECYCLE_STATE_CREATING]
            if list_impl_response.data.items[0].lifecycle_state in allowed_nonactive_states:
                return MlApplicationImplResource(ds_client, impl_id)
            elif (list_impl_response.data.items[0].lifecycle_state !=
                  oci.data_science.models.MlApplicationImplementation.LIFECYCLE_STATE_ACTIVE):
                raise RuntimeError(
                    f"Cannot update ML Application Implementation in state '{list_impl_response.data.items[0].lifecycle_state}'")

            # TODO no update needed if no changes should are needed
            impl_response = ds_client.get_ml_application_implementation(impl_id)
            etag = impl_response.headers["etag"]
            update_impl_details = oci.data_science.models.UpdateMlApplicationImplementationDetails(
                freeform_tags=impl.get('freeform_tags'),
                defined_tags=impl.get('defined_tags')
            )
            print(f"Updating ML Application Implementation with name='{impl['name']}', ID={impl_id}")
            update_impl_response = ds_client.update_ml_application_implementation(
                ml_application_implementation_id=impl_id,
                update_ml_application_implementation_details=update_impl_details,
                if_match=etag)
            print(f"Successfully updated ML Application Implementation: {update_impl_response.data}")
        elif len(list_impl_response.data.items) == 0:
            # ML Application already exists -> create it
            create_impl_details = oci.data_science.models.CreateMlApplicationImplementationDetails(**impl)
            print(f"Creating ML Application Implementation with name='{impl['name']}'")
            create_impl_response = ds_client.create_ml_application_implementation(
                create_ml_application_implementation_details=create_impl_details
            )
            impl_id = create_impl_response.data.id
            print(f"Successful created ML Application Implementation: {create_impl_response.data}")
        else:
            raise RuntimeError(f"Multiple ML Application Implementation with same name '{impl['name']}' found. "
                               f"This should not happen as name is unique in tenancy.")
        return MlApplicationImplResource(ds_client, impl_id)

    @staticmethod
    def find(ds_client: DataScienceClient, impl_name: str, compartment_id: str) -> 'MlApplicationImplResource':
        print(
            f"Searching for ML Application Implementation with name: '{impl_name}' in compartment: '{compartment_id}'")
        list_impl_response = ds_client.list_ml_application_implementations(compartment_id=compartment_id,
                                                                           name=impl_name)
        print(f"Result:\n{list_impl_response.data}")
        if len(list_impl_response.data.items) == 1:
            # ML Application already exists -> update it
            current_impl_summary: oci.data_science.models.MlApplicationImplementationSummary = \
                list_impl_response.data.items[0]
            return MlApplicationImplResource(ds_client, current_impl_summary.id)
        elif len(list_impl_response.data.items) == 0:
            raise ImplNotFoundError(f"No ML Application Implementation with name {impl_name} found", impl_name)
        else:
            raise RuntimeError(f"Multiple ML Application Implementation with same name '{impl_name}' found. "
                               f"This should not happen as name is unique in tenancy.")

    @staticmethod
    def list_in_compartment(ds_client: DataScienceClient, app_id: str, compartment_id: str) -> List[
        'MlApplicationImplResource']:
        print(f"Searching for Implementations of ML Application : '{app_id}' in compartment: '{compartment_id}'")
        list_impl_response = ds_client.list_ml_application_implementations(compartment_id=compartment_id,
                                                                           ml_application_id=app_id)
        result = []
        for impl in list_impl_response.data:
            impl_res = MlApplicationImplResource(ds_client, impl.id)
            result.append(impl_res)
        return result

    def get_details(self) -> MlApplicationImplementation:
        response: Response = self._ds_client.get_ml_application_implementation(self._id)
        return response.data

    @property
    def id(self) -> str:
        return self._id

    def upload_package(self, impl_package_path: str, package_args: dict) -> None:
        package_args_json = json.dumps(package_args)
        print(f"Uploading package '{impl_package_path}' with package arguments '{package_args_json}'")
        work_request_id = None
        with open(impl_package_path, 'rb') as package_content:
            upload_package_response = self._ds_client.put_ml_application_package(
                ml_application_implementation_id=self.id,
                put_ml_application_package=package_content,
                opc_ml_app_package_args=package_args_json
            )
            work_request_id = upload_package_response.headers['opc-work-request-id']
            request_id = upload_package_response.headers['opc-request-id']
            print(f"Package accepted (opc-request-id='{request_id}') ... ")
            work_request: WorkRequestResource = WorkRequestResource(self._ds_client, work_request_id)
            work_request.poll_work_request_and_print_logs()

    def delete(self, idempotent=False) -> None:
        impl_response = self._ds_client.delete_ml_application_implementation(
            ml_application_implementation_id=self.id)
        work_request_id = impl_response.headers['opc-work-request-id']
        work_request: WorkRequestResource = WorkRequestResource(self._ds_client, work_request_id)
        work_request.poll_work_request_and_print_logs()

    def print(self):
        mlappcommon.print_blue_message("-------------------------------------")
        mlappcommon.print_blue_message("Implementation")
        mlappcommon.print_blue_message("-------------------------------------")
        details: MlApplicationImplementation = self.get_details()
        mlappcommon.print_blue_message(details)


class ImplNotFoundError(Exception):

    def __init__(self, msg: str, name: str = None):
        super().__init__(msg)
        self._name = name

    @property
    def name(self):
        return self._name
