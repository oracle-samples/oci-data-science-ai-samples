import json
import oci
from config import *
from bounding_box_config import *
from classification_config import *
from oci.data_labeling_service_dataplane.data_labeling_client import DataLabelingClient
from oci.data_labeling_service_dataplane.models import GenericEntity, Label, CreateAnnotationDetails, NormalizedVertex, \
    BoundingPolygon, ImageObjectSelectionEntity
import datetime
import sys
import re
import time
from itertools import repeat
import pandas as pd
import ast
import logging

sys.path.append("..")


def init_dls_dp_client(config, service_endpoint, retry_strategy):
    dls_client = DataLabelingClient(config=config, service_endpoint=service_endpoint, retry_strategy=retry_strategy)
    return dls_client


config_file = oci.config.from_file(CONFIG_FILE_PATH, CONFIG_PROFILE)
retry_strategy = oci.retry.DEFAULT_RETRY_STRATEGY
dls_dp_client = init_dls_dp_client(config_file, SERVICE_ENDPOINT_DP, retry_strategy)


def dls_list_records(compartment_id,page):
    """ The function is used to list all the records in the dataset

    :param compartment_id: the ocid of compartment in which dataset is present
    :return: a list of name and ocid of records in the dataset
    """
    try:
        # limit parameter has an implicit value of 10 if not included
        anno_response = dls_dp_client.list_records(compartment_id=compartment_id, dataset_id=DATASET_ID,
                                                   is_labeled=False, limit=LIST_RECORDS_LIMIT, page=page)
    except Exception as error:
        anno_response = error
        print(anno_response)

    # manage the json
    data = json.loads(str(anno_response.data))
    # record's full display name
    names = [dls_dataset_record["name"] for dls_dataset_record in data["items"]]

    # ocid of each record
    ids = [dls_dataset_record["id"] for dls_dataset_record in data["items"]]
    if anno_response.has_next_page:
        page = anno_response.next_page
    else:
        page = None
    return names, ids, len(ids), page


def dls_create_annotation(label, record_id, compartment_id):
    """ This function is used to annotate the particular record

    :param label: annotation to be applied on record
    :param record_id: the ocid of the record to be annotated
    :param compartment_id: the ocid of compartment in which dataset is present
    :return: the response of create annotation API call containing all the information about the annotation
    """
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

    create_annotation_details_obj = CreateAnnotationDetails(record_id=record_id, compartment_id=compartment_id,
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
    """ Algorithm to label the record by matching first letter of name of record and label string

    :param letter: first letter of name of record
    :return: The label matching the first letter of record name
    """
    for l in LABELS:
        if letter == l[0] or letter.lower() == l[0]:
            return l


def first_letter(name, record_id, compartment_id, logger):
    """ The function is used to annotate the record with the input label

    :param name: name of the record to be annotated
    :param record_id: the ocid of the record to be annotated
    :param compartment_id: the ocid of compartment in which dataset is present
    :return: None
    """
    label = letter_to_label(letter=name[0])
    if label:
        logger.info("labeling record id: " + str(record_id) + "of name " + str(name) + " with label " + str(label))
        dls_create_annotation(label=label, record_id=record_id, compartment_id=compartment_id)
    else:
        logger.info("No label match for record " + str(name) + " with id: " + str(record_id))
        print("current time: " + str(datetime.datetime.now()))
        print("No label match for record " + str(name))
        print("with id: " + str(record_id))
        print()


def match_to_label(name):
    """ Algorithm to label the record by matching regex of  name of record with label string

    :param name: name of the record to be annotated
    :return: the label to be used to annotate the record
    """
    regex = re.compile(FIRST_MATCH_REGEX_PATTERN)
    for l in LABELS:
        match = regex.match(name).groups()[0]
        if l == match:
            return l


def first_match(name, record_id, compartment_id, logger):
    """ The function is used to annotate the record with the input label

    :param name: name of the record to be annotated
    :param record_id: the ocid of the record to be annotated
    :param compartment_id: the ocid of compartment in which dataset is present
    :return: None
    """
    label = match_to_label(name=name)
    if label:
        logger.info("labeling record id: " + str(record_id) + "of name " + str(name) + " with label " + str(label))
        dls_create_annotation(label=label, record_id=record_id, compartment_id=compartment_id)
    else:
        logger.info("No label match for record " + str(name) + " with id: " + str(record_id))
        print("current time: " + str(datetime.datetime.now()))
        print("No label match for record " + str(name))
        print("with id: " + str(record_id))
        print()


def custom_label_match(name, record_id, compartment_id, logger):
    """ The function is used to annotate the record with the input label

    :param name: name of the record to be annotated
    :param record_id: the ocid of the record to be annotated
    :param compartment_id: the ocid of compartment in which dataset is present
    :return: None
    """
    regex_lst = list(LABEL_MAP.keys())
    label_var = ""
    for regex_exp in regex_lst:
        if name.startswith(regex_exp):
            label_var = regex_exp
            break
    if label_var != "":
        label_lst = LABEL_MAP[label_var]
        logger.info("labeling record id: " + str(record_id) + "of name " + str(name) + " with label " + str(label_lst))
        dls_create_annotation(label=label_lst, record_id=record_id, compartment_id=compartment_id)
    else:
        logger.info("No label match for record " + str(name) + " with id: " + str(record_id))


def label_record(name, id, labeling_algorithm, compartment_id, logger):
    """ The function chooses the annotates the record by choosing the label corresponding to input labeling algorithm

    :param logger: save logs
    :param name: name of the record to be annotated
    :param id: the ocid of the record to be annotated
    :param labeling_algorithm: the algorithm that will be used to assign labels to DLS Dataset records
           Possible values for labeling algorithm "FIRST_LETTER_MATCH", "FIRST_REGEX_MATCH", "CUSTOM_LABELS_MATCH"
    :param compartment_id: the ocid of compartment in which dataset is present
    :return: the annotated record
    """
    if labeling_algorithm == "FIRST_REGEX_MATCH":
        logger.info("labeling algorithm FIRST_REGEX_MATCH for record_id: " + str(id))
        first_match(name=name, record_id=id, compartment_id=compartment_id, logger=logger)
    elif labeling_algorithm == "FIRST_LETTER_MATCH":
        logger.info("labeling algorithm FIRST_LETTER_MATCH for record_id: " + str(id))
        first_letter(name=name, record_id=id, compartment_id=compartment_id, logger=logger)
    elif labeling_algorithm == "CUSTOM_LABELS_MATCH":
        logger.info("labeling algorithm CUSTOM_LABELS_MATCH for record_id: " + str(id))
        custom_label_match(name=name, record_id=id, compartment_id=compartment_id, logger=logger)


def bounding_box_annotation(row, compartment_id, logger):
    """ This Function is used to annotate records of type object detection

    :param row: row of the input csv grouped by record_id
    :param compartment_id: the ocid of compartment in which dataset is present
    return: the annotated record
    """

    record_id = row[0][0]

    entity_type = "IMAGEOBJECTSELECTION"
    entity_obj = []

    for row_ent in row:
        label = row_ent[9]
        label_lst = []
        if isinstance(label, str):
            label_lst.append(label)
        elif isinstance(label, list):
            label_lst = label

        # payload
        labels_obj = []
        for l in label_lst:
            labels_obj.append(Label(label=l))

        normalized_vector_obj_lst = []
        for i in range(4):
            normalized_vector_obj = NormalizedVertex(x=row_ent[i + 1], y=row_ent[i + 5])
            normalized_vector_obj_lst.append(normalized_vector_obj)

        bounding_polygon_obj = BoundingPolygon(normalized_vertices=normalized_vector_obj_lst)

        entity_obj.append(ImageObjectSelectionEntity(entity_type=entity_type, labels=labels_obj,
                                                     bounding_polygon=bounding_polygon_obj))

    create_annotation_details_obj = CreateAnnotationDetails(record_id=record_id, compartment_id=compartment_id,
                                                            entities=entity_obj)
    print(create_annotation_details_obj)
    try:
        logger.info("Creating annotation for record id: " + str(record_id))
        anno_response = dls_dp_client.create_annotation(create_annotation_details=create_annotation_details_obj)
        logger.info("Successfully annotated record id: " + str(record_id))
    except Exception as error:
        logger.info("Failed to annotate for record id: " + str(record_id))
        anno_response = error
    return anno_response


def main():

    logging.basicConfig(filename="debug.log",
                        format='%(asctime)s %(message)s',
                        filemode='w')

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.info("...........starting.............")
    try:
        response = dls_dp_client.get_dataset(dataset_id=DATASET_ID)
        logger.info("Fetching Dataset")
    except Exception as error:
        response = error
    if response.status == 200:
        logger.info("Fetching Dataset Successful")
        compartment_id = response.data.compartment_id
        page = None
        start = time.perf_counter()
        num_records = LIST_RECORDS_LIMIT
        pool = mp.Pool(NO_OF_PROCESSORS)
        if ANNOTATION_TYPE == "BOUNDING_BOX":
            logger.info("Annotation type: Bounding Box")
            df = pd.read_csv(PATH)
            df['label'] = df['label'].apply(lambda x: ast.literal_eval(x))
            rows = df.groupby('record_id').apply(lambda x: x.values.tolist()).tolist()[:]
            pool.starmap(bounding_box_annotation, zip(rows, repeat(compartment_id), repeat(logger)))
            pool.close()
            end = time.perf_counter()
            print(f'Finished in {round(end - start, 2)} second(s)')
        elif ANNOTATION_TYPE == "CLASSIFICATION":
            while True:
                names, ids, num_records,page = dls_list_records(compartment_id=compartment_id,page=page)
                pool.starmap(label_record, zip(names, ids, repeat(LABELING_ALGORITHM), repeat(compartment_id), repeat(logger)))
                if not page:
                    break
            pool.close()
            end = time.perf_counter()
            print(f'Finished in {round(end - start, 2)} second(s)')
        else:
            print("Please provide the correct value for ANNOTATION_TYPE")
    else:
        print(response)


if __name__ == "__main__":
    main()
