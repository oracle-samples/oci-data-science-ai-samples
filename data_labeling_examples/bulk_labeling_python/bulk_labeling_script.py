import json
import oci
from config import *
from oci.data_labeling_service_dataplane.data_labeling_client import DataLabelingClient
from oci.data_labeling_service_dataplane.models import GenericEntity
from oci.data_labeling_service_dataplane.models import Label
from oci.data_labeling_service_dataplane.models import CreateAnnotationDetails
import datetime
import sys
import re
import time
from itertools import repeat

sys.path.append("..")


def init_dls_dp_client(config, service_endpoint, retry_strategy):
    dls_client = DataLabelingClient(config=config, service_endpoint=service_endpoint, retry_strategy=retry_strategy)
    return dls_client


def dls_list_records():
    config_file = oci.config.from_file(CONFIG_FILE_PATH, CONFIG_PROFILE)
    retry_strategy = oci.retry.DEFAULT_RETRY_STRATEGY

    dls_dp_client = init_dls_dp_client(config_file, SERVICE_ENDPOINT_DP, retry_strategy)

    try:
        # limit parameter has an implicit value of 10 if not included
        anno_response = dls_dp_client.list_records(compartment_id=COMPARTMENT_ID, dataset_id=DATASET_ID,
                                                   is_labeled=False, limit=LIST_RECORDS_LIMIT)
    except Exception as error:
        anno_response = error
        print(anno_response)

    # manage the json
    data = json.loads(str(anno_response.data))
    # record's full display name
    names = [dls_dataset_record["name"] for dls_dataset_record in data["items"]]

    # ocid of each record
    ids = [dls_dataset_record["id"] for dls_dataset_record in data["items"]]
    return names, ids, len(ids)


def dls_create_annotation(label, record_id):
    config_file = oci.config.from_file(CONFIG_FILE_PATH, CONFIG_PROFILE)
    retry_strategy = oci.retry.DEFAULT_RETRY_STRATEGY

    dls_dp_client = init_dls_dp_client(config_file, SERVICE_ENDPOINT_DP, retry_strategy)
    label_lst = []
    if isinstance(label, str):
        label_lst.append(label)
    elif isinstance(label, list):
        label_lst = label

    # payload
    labels_obj = []
    for l in label_lst:
        labels_obj.append(Label(label=l))
    entity_type = "GENERIC"
    entity_obj = [GenericEntity(entity_type=entity_type, labels=labels_obj)]

    create_annotation_details_obj = CreateAnnotationDetails(record_id=record_id, compartment_id=COMPARTMENT_ID,
                                                            entities=entity_obj)

    # api call
    print(create_annotation_details_obj)
    try:
        anno_response = dls_dp_client.create_annotation(create_annotation_details=create_annotation_details_obj)
    except Exception as error:
        anno_response = error
        print(anno_response)
    return anno_response.data


def letter_to_label(letter):
    for l in LABELS:
        if letter == l[0] or letter.lower() == l[0]:
            return l


def first_letter(name, record_id):
    label = letter_to_label(letter=name[0])
    if label:
        dls_create_annotation(label=label, record_id=record_id)
    else:
        print("current time: " + str(datetime.datetime.now()))
        print("No label match for record " + str(name))
        print("with id: " + str(record_id))
        print()


def match_to_label(name):
    regex = re.compile(FIRST_MATCH_REGEX_PATTERN)
    for l in LABELS:
        match = regex.match(name).groups()[0]
        if l == match:
            return l


def first_match(name, record_id):
    label = match_to_label(name=name)
    if label:
        dls_create_annotation(label=label, record_id=record_id)
    else:
        print("current time: " + str(datetime.datetime.now()))
        print("No label match for record " + str(name))
        print("with id: " + str(record_id))
        print()


def custom_label_match(name, record_id):
    regex_lst = list(LABEL_MAP.keys())
    label_var = ""
    for regex_exp in regex_lst:
        if name.startswith(regex_exp):
            label_var = regex_exp
            break
    if label_var != "":
        label_lst = LABEL_MAP[label_var]
        dls_create_annotation(label=label_lst, record_id=record_id)


def label_record(name, id, labeling_algorithm):
    if labeling_algorithm == "FIRST_REGEX_MATCH":
        first_match(name=name, record_id=id)
    elif labeling_algorithm == "FIRST_LETTER_MATCH":
        first_letter(name=name, record_id=id)
    elif labeling_algorithm == "CUSTOM_LABELS_MATCH":
        custom_label_match(name=name, record_id=id)


def main():
    if __name__ == '__main__':
        start = time.perf_counter()
        num_records = LIST_RECORDS_LIMIT
        pool = NO_OF_PROCESSORS
        while num_records == LIST_RECORDS_LIMIT:
            names, ids, num_records = dls_list_records()
            pool.starmap(label_record, zip(names, ids, repeat(LABELING_ALGORITHM)))
        pool.close()
        end = time.perf_counter()
        print(f'Finished in {round(end - start, 2)} second(s)')


main()
