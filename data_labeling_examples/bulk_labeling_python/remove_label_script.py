import oci
import os
from config import *
from oci.data_labeling_service_dataplane.data_labeling_client import DataLabelingClient
from oci.data_labeling_service_dataplane.models import GenericEntity, Entity, Annotation, AnnotationCollection, AnnotationSummary, UpdateAnnotationDetails
import time
import logging
import json
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from concurrent.futures import wait

def init_dls_dp_client(config, service_endpoint):
    dls_client = DataLabelingClient(config=config, service_endpoint=service_endpoint)
    return dls_client


config_file = oci.config.from_file(CONFIG_FILE_PATH, CONFIG_PROFILE)
retry_strategy = oci.retry.DEFAULT_RETRY_STRATEGY
dls_dp_client = init_dls_dp_client(config_file, SERVICE_ENDPOINT_DP)
labels_to_remove = []

def process_annotation_and_remove_label(logger, annotation_id):
    try:
        response = dls_dp_client.get_annotation(annotation_id=annotation_id)
    except Exception as error:
            global failure_count
            failure_count+=1
            response = error
    if response.status == 200:
        entities = response.data.entities

        if len(entities) > 1:
            print("Single/Multi label annotation can have only one annotation entity")
            return

        for e in entities:
            entity_type = e.entity_type
            extended_metadata = e.extended_metadata
            entityLabel = e.labels

        newLabelList = []

        for label in entityLabel:
            if not label.label in labels_to_remove:
                newLabelList.append(label)

        if not newLabelList:
            delete_annotation(annotation_id)
        elif newLabelList == entityLabel:
            print("Nothing to update")
        else :
            new_entity = [GenericEntity(entity_type=entity_type, extended_metadata=extended_metadata, labels=newLabelList)]
            update_annotation(response.data, new_entity)

def delete_annotation(annotation_id):
    try:
        response = dls_dp_client.delete_annotation(annotation_id=annotation_id)
        global success_count
        success_count+=1
    except Exception as error:
        print(error)
        global failure_count
        failure_count+=1

def update_annotation(annotation, entity):
    update_annotation_details_obj = UpdateAnnotationDetails(defined_tags=annotation.defined_tags ,entities=entity, freeform_tags=annotation.freeform_tags)
    try:
        response = dls_dp_client.update_annotation(annotation_id=annotation.id, update_annotation_details=update_annotation_details_obj)
        global success_count
        success_count+=1
    except Exception as error:
        print(error)
        global failure_count
        failure_count+=1

def main():

    logging.basicConfig(filename="debug.log",
                            format='%(asctime)s %(message)s',
                            filemode='w')

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.info("...........starting to remove labels.............")
    start = time.perf_counter()
    try:
        response = dls_dp_client.get_dataset(dataset_id=DATASET_ID)
        logger.info("Fetching Dataset")
    except Exception as error:
        response = error
    if response.status == 200:
        logger.info("Fetching Dataset Successful")
        compartment_id = response.data.compartment_id
        # manage the json
        data = json.loads(str(response.data.label_set))
        dataset_labels = [labels["name"] for labels in data["items"]]
        print("Dataset Labels : ")
        print(dataset_labels)
        for label in dataset_labels:
            if label.startswith(REMOVE_LABEL_PRIFIX):
                labels_to_remove.append(label)

        if not labels_to_remove:
            print(f"No Label found with prefix " + REMOVE_LABEL_PRIFIX)
            return
        print("Labels to be removed : ")
        print(labels_to_remove)
        global success_count
        global failure_count
        success_count=0
        failure_count=0
        page = None

        while True:
            annotation_response = dls_dp_client.list_annotations(compartment_id=compartment_id, dataset_id=DATASET_ID, lifecycle_state="ACTIVE",page=page)
            annotation_data = json.loads(str(annotation_response.data))
            annotation_ids = [annotation["id"] for annotation in annotation_data["items"]]

            with ThreadPoolExecutor(NO_OF_PROCESSORS) as executor:
                futures = [executor.submit(process_annotation_and_remove_label, logger, annotation_id) for annotation_id in annotation_ids]
            wait(futures)
            if annotation_response.has_next_page :
                page = annotation_response.next_page
            else:
                break

    end = time.perf_counter()
    print(f'Total annotations to process : {(success_count + failure_count)}\n'
          f'Successfully processed {success_count}\n'
          f'Failed to process {failure_count}\n'
          f'Finished in {round(end - start, 2)} second(s)')

if __name__ == "__main__":
    main()