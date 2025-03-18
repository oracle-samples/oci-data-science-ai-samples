from typing import Dict, List

import oci
from oci.data_science import DataScienceClient
from oci.data_science.models import MlApplication
from ml_app_impl_res import MlApplicationImplResource
from oci.response import Response
from ml_app_instance_res import MlApplicationInstanceResource
import mlappcommon


# TODO implement parent for these resources
class MlApplicationResource:
    _ds_client: DataScienceClient

    def __init__(self, ds_client: DataScienceClient, app_id: str):
        self._ds_client = ds_client
        self._id = app_id

    @staticmethod
    def create_or_update(ds_client: DataScienceClient, **app) -> 'MlApplicationResource':
        print(f"Searching for ML Application with name: '{app['name']}' in compartment: '{app['compartment_id']}'")
        list_app_response = ds_client.list_ml_applications(compartment_id=app["compartment_id"], name=app["name"])
        print(list_app_response.data)
        mlappcommon.add_hash_tag(app)
        app_id = None
        if len(list_app_response.data.items) == 1:
            # ML Application already exists -> update it
            current_app_summary: oci.data_science.models.MlApplicationSummary = list_app_response.data.items[0]
            app_id = current_app_summary.id
            if current_app_summary.freeform_tags.get('hash') == app.get('freeform_tags')['hash']:
                return MlApplicationResource(ds_client, app_id)
            # TODO no update needed if no changes are needed (if description is not changed update does not make sense)
            app_response = ds_client.get_ml_application(app_id)
            etag = app_response.headers["etag"]
            update_app_details = oci.data_science.models.UpdateMlApplicationDetails(
                description=app["description"],
                freeform_tags=app.get('freeform_tags'),
                defined_tags=app.get('defined_tags')
            )
            print(f"Updating ML Application with name='{app['name']}', ID={app_id}")
            update_app_response = ds_client.update_ml_application(
                ml_application_id=app_id,
                update_ml_application_details=update_app_details,
                if_match=etag)
            print(f"Successfully updated ML Application: {update_app_response.data}")
        elif len(list_app_response.data.items) == 0:
            # ML Application doesn't exist -> create it
            create_app_details = oci.data_science.models.CreateMlApplicationDetails(**app)
            print(f"Creating ML Application with name='{app['name']}'")
            create_app_response = ds_client.create_ml_application(create_ml_application_details=create_app_details)
            print(f"Successful created ML Application: {create_app_response.data}")
            app_id = create_app_response.data.id
        else:
            raise RuntimeError(f"Multiple ML Application with same name '{app['name']}' found. "
                               f"This should not happen as name is unique in tenancy.")
        return MlApplicationResource(ds_client, app_id)

    @staticmethod
    def find(ds_client: DataScienceClient, app_name: str, compartment_id: str) -> 'MlApplicationResource':
        print(f"Searching for ML Application with name: '{app_name}' in compartment: '{compartment_id}'")
        list_app_response = ds_client.list_ml_applications(compartment_id=compartment_id, name=app_name)
        print(f"Result:\n{list_app_response.data}")
        if len(list_app_response.data.items) == 1:
            # ML Application already exists -> update it
            current_app_summary: oci.data_science.models.MlApplicationSummary = list_app_response.data.items[0]
            return MlApplicationResource(ds_client, current_app_summary.id)
        elif len(list_app_response.data.items) == 0:
            raise RuntimeError(f"Cannot find ML Application with name {app_name}")
        else:
            raise RuntimeError(f"Multiple ML Application with same name '{app_name}' found. "
                               f"This should not happen as name is unique in tenancy.")

    def get_details(self) -> MlApplication:
        response: Response = self._ds_client.get_ml_application(self._id)
        return response.data

    @property
    def id(self) -> str:
        return self._id

    def delete(self, idempotent=False) -> None:
        response: Response = self._ds_client.delete_ml_application(ml_application_id=self.id)

    def delete_cascade_from_compartment(self, compartment_id: str = None) -> None:
        """
        Delete ML Application with all its children like ML Application Implementation and ML Application Instances
        if they are in the same compartment ML Application is located.
        """
        if compartment_id is None:
            compartment_id = self.get_details().compartment_id

        impls: List[MlApplicationImplResource] = MlApplicationImplResource.list_in_compartment(self._ds_client,
                                                                                               self.id,
                                                                                               compartment_id)
        instances: List[MlApplicationInstanceResource] = MlApplicationInstanceResource.list_in_compartment(
            self._ds_client,
            self.id,
            compartment_id)

        # synchronous deletion of instances
        for instance in instances:
            instance.delete()

        # synchronous deletion of implementations
        for impl in impls:
            impl.delete()

        # delete application
        self.delete()

    def print(self):
        mlappcommon.print_blue_message("-------------------------------------")
        mlappcommon.print_blue_message("Application")
        mlappcommon.print_blue_message("-------------------------------------")
        details: MlApplication = self.get_details()
        mlappcommon.print_blue_message(details)