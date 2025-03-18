import re
import time
from typing import List

import oci
from oci import Response
from oci.data_science import DataScienceClient
from oci.data_science.models import WorkRequest, WorkRequestLogEntry, WorkRequestSummary

import mlappcommon


class WorkRequestResource:
    _ds_client: DataScienceClient
    _work_request_cache: WorkRequest

    def __init__(self, ds_client: DataScienceClient, work_request_id: str):
        self._ds_client = ds_client
        self._work_request_id = work_request_id
        self._work_request_cache = None

    def get_details(self) -> WorkRequest:
        response: Response = self._ds_client.get_work_request(self._work_request_id)
        self._work_request_cache = response.data
        return response.data

    def _get_work_request_cache(self) -> WorkRequest:
        if self._work_request_cache is None:
            self.get_details()
        return self._work_request_cache

    def get_resources(self):
        return self._get_work_request_cache().resources

    def get_compartment_id(self):
        return self._get_work_request_cache().resources

    def poll_work_request_and_print_logs(self, timeout=3600):
        print("-----------------------------------------------------------")
        print(f"Polling status for WorkRequest {self._work_request_id}")
        delays = [5, 5, 5, 5, 5, 5, 5, 5, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
                  20]  # Backoff delays
        last_log_index = None
        start_time = time.time()
        delay_index = 0

        while True:
            # Check if timeout has been reached
            if time.time() - start_time >= timeout:
                print(f"Timeout {timeout} sec reached. Polling stopped.")
                return

            # Poll WorkRequest status
            work_request: WorkRequest = self.get_details()
            print(f"Polling WorkRequest status = {work_request.status} (ID = {self._work_request_id})")
            # Get and print new logs
            last_log_index = self.print_new_logs(last_log_index)
            if work_request.status in ['IN_PROGRESS', 'ACCEPTED', 'CANCELING']:
                # Print next polling time
                delay = delays[delay_index] if delay_index < len(delays) else delays[-1]
                target_time = time.time() + delay
                print(f"Next polling in {delay} seconds "
                      f"(i.e. at '{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(target_time))}') ...")

                time.sleep(delay)

                # Increment delay index if not at the last value
                if delay_index < len(delays) - 1:
                    delay_index += 1
            elif work_request.status in ['SUCCEEDED', 'FAILED', 'CANCELED']:
                print(f"WorkRequest reached final state '{work_request.status}'. Polling stopped")
                if work_request.status != 'SUCCEEDED':
                    raise ValueError(f"WorkRequest not succeeded:\n{work_request}")
                print("-----------------------------------------------------------")
                return work_request
            else:
                print(f"WorkRequest in unexpected state: {work_request.status}. Polling stopped", work_request.status)
                print("-----------------------------------------------------------")
                return work_request

    def print_new_logs(self, last_log_index):
        log_entries: List[WorkRequestLogEntry] = []
        page = None
        while True:
            log_entries_response = self._list_logs(page)

            if not log_entries_response.data:
                break

            log_entries.extend(log_entries_response.data)
            if log_entries_response.next_page is None:
                break
            page = log_entries_response.next_page

        start_index = 0 if last_log_index is None else last_log_index + 1
        for i in range(start_index, len(log_entries)):
            log = log_entries[i]

            print(WorkRequestResource._add_prefix_to_lines(
                log.message,
                mlappcommon.BLUE + f"    WR LOG: {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}") + mlappcommon.ENDC)

        if log_entries:
            last_log_index = len(log_entries) - 1
        return last_log_index

    def get_first_log_page(self) -> List[str]:
        logs: List[WorkRequestLogEntry] = self._list_logs(page=None).data
        return [log.message for log in logs]

    def _list_logs(self, page) -> Response:
        if page is None:
            log_entries_response = self._ds_client.list_work_request_logs(self._work_request_id)
        else:
            log_entries_response = self._ds_client.list_work_request_logs(self._work_request_id, page=page)
        return log_entries_response

    @staticmethod
    def _add_prefix_to_lines(multiline_string, prefix):
        lines = multiline_string.split('\n')
        prefixed_lines = [prefix + line for line in lines]
        return '\n'.join(prefixed_lines)

    @staticmethod
    def find_last_for_model_deployment(ds_client: DataScienceClient, md_id: str,
                                       operation_type: str) -> 'WorkRequestResource':
        md: oci.data_science.models.ModelDeployment = ds_client.get_model_deployment(md_id).data
        compartment_id = md.compartment_id
        # TODO go through all pages
        wr_list: List[WorkRequestSummary] = ds_client.list_work_requests(compartment_id=compartment_id,
                                                                         operation_type=operation_type,
                                                                         limit=100).data

        if md_id is not None:
            wr_list = [wr for wr in wr_list if any(w.identifier == md_id for w in wr.resources)]

        if len(wr_list) == 0:
            raise ValueError(
                f"No WorkRequest with operation type '{operation_type}' found in compartment_id '{compartment_id}'")

        return WorkRequestResource(ds_client, wr_list[0].id)

    @staticmethod
    def find_last_for_provider_trigger(ds_client: DataScienceClient,
                                       trigger_name: str,
                                       instance_id: str,
                                       compartment_id: str) -> 'WorkRequestResource':
        # TODO go through all pages
        wr_list: List[WorkRequestSummary] = ds_client.list_work_requests(compartment_id=compartment_id,
                                                                         operation_type="ML_APPLICATION_TRIGGER_START",
                                                                         sort_order='DESC',
                                                                         sort_by='timeAccepted',
                                                                         limit=100).data
        instance_id = mlappcommon.to_instance_view_ocid(instance_id)
        wr_list = [wr for wr in wr_list if any(w.identifier == instance_id for w in wr.resources)]

        if len(wr_list) == 0:
            raise ValueError(
                f"No WorkRequest with operation type 'ML_APPLICATION_TRIGGER_START' found for instance ID {instance_id} in compartment_id '{compartment_id}'")
        for wr in wr_list:
            # TODO (This is hacky fragile solution) we need to allow check which trigger name this WR is related to (taking it from logs is very fragile)
            wr_resource: WorkRequestResource = WorkRequestResource(ds_client, wr.id)
            logs = []
            start_time = time.time()
            while len(logs) < 2 and round(time.time() - start_time) < 30:
                logs = wr_resource.get_first_log_page()
                time.sleep(5)

            for log in logs:
                match = re.search(r"Trigger name: (.+)", log)

                if not match:
                    continue

                found_trigger_name = match.group(1)
                print(f"Found trigger name for WorkRequest {wr.id}: {found_trigger_name}")
                if found_trigger_name == trigger_name:
                    return WorkRequestResource(ds_client, wr.id)

        raise RuntimeError(f"Cannot find WorkRequest for trigger {trigger_name} for instance ID {instance_id}")

    # @staticmethod
    # def _find_last(ds_client: DataScienceClient,
    #                compartment_id: str,
    #                operation_type: str,
    #                resource_id: str=None,) -> 'WorkRequestResource':
    #     # TODO go through all pages
    #     wr_list: List[WorkRequestSummary] = ds_client.list_work_requests(compartment_id=compartment_id,
    #                                                                      operation_type=operation_type,
    #                                                                      sort_order='DESC',
    #                                                                      sort_by='timeAccepted',
    #                                                                      limit=100).data
    #     if resource_id is not None:
    #         wr_list = [wr for wr in wr_list if any(w.identifier == resource_id for w in wr.resources)]
    #
    #     if len(wr_list) == 0:
    #         raise ValueError(
    #             f"No WorkRequest with operation type '{operation_type}' found in compartment_id '{compartment_id}'")
    #
    #     return WorkRequestResource(ds_client, wr_list[0].id)
