import datetime
import json
import time
from typing import List

import oci
import requests
from oci.data_science import DataScienceClient
from oci.data_science.models import CreateMlApplicationInstanceDetails, MlApplicationInstance, \
    TriggerMlApplicationInstanceViewFlowDetails, MlApplicationInstanceView, PredictionEndpointDetails, PredictionUri
from oci.response import Response

import mlappcommon
from mlappcommon import deserialize_oci_sdk_model_from_json
from work_request import WorkRequestResource


class MlApplicationInstanceResource:
    _ds_client: DataScienceClient

    def __init__(self, ds_client: DataScienceClient, app_instance_id: str):
        self._ds_client = ds_client
        self._id = mlappcommon.to_instance_ocid(app_instance_id)

    @staticmethod
    def list_in_compartment(ds_client: DataScienceClient, app_id: str, compartment_id: str) -> List[
        'MlApplicationInstanceResource']:
        print(
            f"Searching for all ML Application Instances for ML Application '{app_id}' in compartment '{compartment_id}'")
        list_response = ds_client.list_ml_application_instances(compartment_id=compartment_id,
                                                                ml_application_id=app_id)
        return [MlApplicationInstanceResource(ds_client, instance.id) for instance in list_response.data.items]

    @staticmethod
    def list_views(ds_client: DataScienceClient, display_name: str, compartment_id: str,
                   impl_id: str) -> List['MlApplicationInstanceResource']:
        print(
            f"Searching for ML Application Instance View with name: '{display_name}' in compartment: '{compartment_id}'")
        list_response = ds_client.list_ml_application_instance_views(compartment_id=compartment_id,
                                                                     display_name=display_name,
                                                                     ml_application_implementation_id=impl_id,
                                                                     limit=100)
        return [MlApplicationInstanceResource(ds_client, instance.id) for instance in list_response.data.items]
        # to
        # item.id]
        # if len(list_response.data.items) == 1:
        #     # ML Application Instance already exists -> update it
        #     current_summary: oci.data_science.models.MlApplicationInstanceSummary = list_response.data.items[0]
        #     return [MlApplicationInstanceResource(ds_client, mlappcommon.to_instance_ocid(current_summary.id))]
        # elif len(list_response.data.items) == 0:
        #     raise ValueError(
        #         f"No ML Application Instance View with displayName {display_name} and ML Application Impl ID "
        #         f"'{impl_id}' found in compartment {compartment_id}")
        # else:
        #     # TODO we should support this and let user to select which instance he/she want to work with
        #     raise ValueError(
        #         f"Multiple ML Application Instance Views with same name '{display_name}' found in compartment {compartment_id}. "
        #         f"This should not happen as name is unique in tenancy.")

    @staticmethod
    def find(ds_client: DataScienceClient, display_name: str, compartment_id: str,
             ml_app_id: str) -> 'MlApplicationResource':
        print(f"Searching for ML Application Instance with name: '{display_name}' in compartment: '{compartment_id}'")
        list_response = ds_client.list_ml_application_instances(compartment_id=compartment_id,
                                                                display_name=display_name,
                                                                ml_application_id=ml_app_id)
        if len(list_response.data.items) == 1:
            # ML Application Instance already exists -> update it
            current_summary: oci.data_science.models.MlApplicationInstanceSummary = list_response.data.items[0]
            return MlApplicationInstanceResource(ds_client, current_summary.id)
        elif len(list_response.data.items) == 0:
            raise ValueError(
                f"No ML Application Instance with displayName {display_name} and ML Application ID '{ml_app_id}' found in compartment {compartment_id}")
        else:
            raise ValueError(
                f"Multiple ML Application Instances with same name '{display_name}' found in compartment {compartment_id}. "
                f"This should not happen as name is unique in tenancy.")

    @staticmethod
    def create_from_file(ds_client: DataScienceClient, instance_json_path,
                         parameters={}) -> 'MlApplicationInstanceResource':
        create_details: CreateMlApplicationInstanceDetails
        with open(instance_json_path, 'r') as json_file:
            data = json.load(json_file)
            # TODO this deserves improvement
            for key, value in parameters:
                data = data.replace(f"{key}", value)
            create_details = deserialize_oci_sdk_model_from_json(data, CreateMlApplicationInstanceDetails)
            return MlApplicationInstanceResource.create(ds_client, create_details)

    @staticmethod
    def create_from_json_dict(ds_client: DataScienceClient, data: dict) -> 'MlApplicationInstanceResource':
        create_details = deserialize_oci_sdk_model_from_json(data, CreateMlApplicationInstanceDetails)
        return MlApplicationInstanceResource.create(ds_client, create_details)

    @staticmethod
    def create(ds_client: DataScienceClient,
               create_details: CreateMlApplicationInstanceDetails) -> 'MlApplicationInstanceResource':
        print(f"Creating ML Application Instance with following properties:\n {create_details}")
        response: Response = ds_client.create_ml_application_instance(create_details)
        work_request_id = response.headers['opc-work-request-id']
        print(f"Response: opc-work-request-id={work_request_id}")
        instance_work_request: WorkRequestResource = WorkRequestResource(ds_client, work_request_id)

        work_request: WorkRequestResource = MlApplicationInstanceResource._to_instance_view_work_request(ds_client,
                                                                                                         instance_work_request=instance_work_request,
                                                                                                         operation_type="ML_APPLICATION_INSTANCE_VIEW_CREATE")
        work_request.poll_work_request_and_print_logs()
        work_request_details = work_request.get_details()
        if work_request_details.status == 'SUCCEEDED':
            instance_id = work_request_details.resources[0].identifier
            return MlApplicationInstanceResource(ds_client, instance_id)
        else:
            raise RuntimeError("Creation of ML Application Instance failed")

    @staticmethod
    def _to_instance_view_work_request(ds_client: DataScienceClient,
                                       instance_work_request: WorkRequestResource,
                                       operation_type: str) -> WorkRequestResource:
        instance_id = instance_work_request.get_resources()[0].identifier
        time_accepted: datetime = instance_work_request.get_details().time_accepted
        instance = MlApplicationInstanceResource(ds_client, instance_id)
        instance_view_details = None
        for attempt in range(1, 20):
            try:
                instance_view_details = instance.get_view_details()
                break
            except oci.exceptions.ServiceError as e:
                if e.status != 404:
                    raise e
            print(f"Waiting for ML Application Instance View is created")
            time.sleep(5)

        compartment_id: str = instance_view_details.compartment_id
        instance_view_id = instance_view_details.id

        # TODO we should iterate here over other pages
        target_work_request = None
        for retry in range(20):
            print(f"Trying to find WorkRequest for ML Application Instance View with OCID: {instance_view_id}")
            view_work_requests: list = ds_client.list_work_requests(sort_by="timeAccepted",
                                                                    sort_order="DESC",
                                                                    operation_type=operation_type,
                                                                    compartment_id=compartment_id,
                                                                    limit=100).data
            target_work_request = next(
                (wr for wr in view_work_requests if
                 wr.resources[0].identifier == instance_view_id and wr.time_accepted >= time_accepted),
                None)
            if target_work_request is not None:
                print(f"WorkRequest found. OCID: {target_work_request.id}")
                return WorkRequestResource(ds_client, target_work_request.id)
            print("Waiting for WorkRequest to be available ...")
            time.sleep(5)

        raise RuntimeError(f"Cannot find WorkRequest for Instance View ID={instance_view_id}")

    def get_details(self) -> MlApplicationInstance:
        response: Response = self._ds_client.get_ml_application_instance(self._id)
        return response.data

    def get_view_details(self) -> MlApplicationInstanceView:
        view_id = mlappcommon.to_instance_view_ocid(self._id)
        response: Response = self._ds_client.get_ml_application_instance_view(view_id)
        return response.data

    def delete(self) -> None:
        response: Response = self._ds_client.delete_ml_application_instance(self._id)
        work_request_id = response.headers['opc-work-request-id']
        request_id = response.headers['opc-request-id']
        print(f"Delete instance request accepted (opc-request-id='{request_id}') ... ")
        work_request: WorkRequestResource = MlApplicationInstanceResource._to_instance_view_work_request(
            self._ds_client,
            instance_work_request=WorkRequestResource(self._ds_client, work_request_id),
            operation_type="ML_APPLICATION_INSTANCE_VIEW_DELETE")
        work_request.poll_work_request_and_print_logs()

    def delete_async(self) -> WorkRequestResource:
        response: Response = self._ds_client.delete_ml_application_instance(self._id)
        return WorkRequestResource(self._ds_client, response.headers['opc-work-request-id'])

    @property
    def id(self) -> str:
        return self._id

    def trigger_by_provider(self, trigger_name, md_name_to_wait_for=None) -> None:
        work_request: WorkRequestResource
        try:
            response: Response = self._ds_client.trigger_ml_application_instance_view_flow(
                TriggerMlApplicationInstanceViewFlowDetails(trigger_name=trigger_name),
                mlappcommon.to_instance_view_ocid(self._id))
            work_request_id = response.headers['opc-work-request-id']
            work_request: WorkRequestResource = WorkRequestResource(self._ds_client, work_request_id)
        except oci.exceptions.ServiceError as e:
            if e.code == 409 and e.operation_name == 'trigger_ml_application_instance_view_flow':
                print(e)
                # TODO check whether trigger is not disabled (in such case 409 is returned as well)
                work_request = WorkRequestResource.find_last_for_provider_trigger(self._ds_client, trigger_name,
                                                                                  self._id,
                                                                                  self.get_details().compartment_id)
                print("****** Trigger invocation conflict (trigger has been already invoked before this invocation)"
                      " ******")
                print("Polling existing WorkRequest")
            else:
                raise e

        work_request.poll_work_request_and_print_logs()

        if md_name_to_wait_for is None:
            return
        # wait until last Model Deployment Update WorkRequest is finished
        view: MlApplicationInstanceView = self.get_view_details()
        md_id: str = None
        for instance_component in view.instance_components:
            if (isinstance(instance_component, oci.data_science.models.DataScienceModelDeploymentInstanceComponent)
                    and instance_component.name == md_name_to_wait_for):
                md_id = instance_component.model_deployment_id
                break
        if md_id is None:
            raise ValueError(f"No Model Deployment with name {md_name_to_wait_for} found")

        # if non-production env for ML App is used, we need to use different Data Science Client (without override)
        prod_ds_client = self._ds_client if self._ds_client.base_client.endpoint.startswith(
            "https://datascience.") else oci.data_science.DataScienceClient(
            {"region": self._ds_client.base_client.config['region']},
            signer=self._ds_client.base_client.signer)
        md_wr: WorkRequestResource = WorkRequestResource.find_last_for_model_deployment(prod_ds_client, md_id,
                                                                                        'MODEL_DEPLOYMENT_UPDATE')
        print(f"Waiting for Model Deployment update to finish (Model Deployment ID: {md_id}")
        md_wr.poll_work_request_and_print_logs()

    def get_prediction_use_cases(self) -> List[PredictionUri]:
        instance_view_details: MlApplicationInstanceView = self.get_view_details()
        prediction_endpoint_details: PredictionEndpointDetails = instance_view_details.prediction_endpoint_details
        return prediction_endpoint_details.prediction_uris

    def predict(self, prediction_use_case: str, prediction_payload: str) -> str:
        instance_view_details: MlApplicationInstanceView = self.get_view_details()
        prediction_endpoint_details: PredictionEndpointDetails = instance_view_details.prediction_endpoint_details
        uris: List[PredictionUri] = prediction_endpoint_details.prediction_uris
        if uris is None:
            raise ValueError("No prediction use cases found for given ML Application Instance View")

        prediction_uri = None
        for uri in uris:
            if uri.use_case == prediction_use_case:
                prediction_uri = uri.uri
                break

        if prediction_uri is None:
            raise ValueError(f"Cannot find prediction use case '{prediction_use_case}'. "
                             f"Use one of existing prediction use cases: \n{uris}")

        auth = self._ds_client.base_client.signer
        response = requests.post(url=prediction_uri, data=prediction_payload, auth=auth)
        response.raise_for_status()
        return response.json()

    def print(self):
        mlappcommon.print_blue_message("-------------------------------------")
        mlappcommon.print_blue_message("Instance View")
        mlappcommon.print_blue_message("-------------------------------------")
        details: MlApplicationInstanceView = self.get_view_details()
        mlappcommon.print_blue_message(details)
