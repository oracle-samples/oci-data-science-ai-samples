import traceback

import oci
import json
import argparse

from datetime import datetime

from example_code.content_delivery import ContentDeliveryFactory, ObjectStorageHelper
from example_code.remove_unnecessary_columns import remove_unnecessary_columns
from example_code.column_rename import column_rename
from example_code.string_transformations import string_transformation
from example_code.format_timestamp import format_timestamp
from example_code.temporal_differencing import temporal_differencing
from example_code.normalization import normalize_data
from example_code.fixed_window_batching import windowing
from example_code.sliding_window_aggregation import aggregation
from example_code.one_hot_encoding import one_hot_encoding
from example_code.pivoting import spark_pivoting
from example_code.sharding import sharding

from example_code.time_series_merge import time_series_merge
from example_code.time_series_join import time_series_join

from example_code.ad_utils import AdUtils
from example_code.dataflow_utils import DataflowSession, get_spark_context, get_authenticated_client


signer = oci.auth.signers.get_resource_principals_signer()
dataflow_session = DataflowSession(app_name="DataFlow")
data_flow_client = oci.data_flow.DataFlowClient(config={}, signer=signer)
object_storage_client = \
    oci.object_storage.ObjectStorageClient(config={}, signer=signer)
SINGLE_DATAFRAME_PROCESSING = "singleDataFrameProcessing"
COMBINE_DATAFRAMES = "combineDataFrames"
JOIN = "join"
MERGE = "merge"
RESERVED_METADATA = ['distinct_categories', 'distinct_column_values']
TRAINING = "applyAndFinalize"
INFERENCING = "apply"


def get_object(object_storage_client, namespace, bucket, file):
    get_resp = object_storage_client.get_object(namespace, bucket, file)
    assert get_resp.status in [
        200,
        201,
    ], f"Unable to get object from {bucket}@{namespace}! Response: {get_resp.text}"
    return get_resp.data.text


def parse_and_process_data_preprocessing_config(object_storage_client, spark, contents, phase, event_data=None):
    """
    Data Preprocessing Operation
    Args:
        object_storage_client: the object storage client for communicating with object storage
        spark: entry point for spark application
        contents: the parsed response from config json
        phase: the phase info referring training or inferencing
        event_data: Information of the event that triggered the run
    """
    dfs = dict()
    try:
        '''
        Deal with input sources
        '''
        input_sources = contents["inputSources"]
        event_driven_input_sources = \
            [1 for source in input_sources if 'isEventDriven' in source and source['isEventDriven']]
        assert len(event_driven_input_sources) <= 1, \
            f"At-most 1 event driven input-source is supported! But {len(event_driven_input_sources)} are provided."

        # build dictionary: df name: df
        for source in input_sources:
            if 'isEventDriven' in source and source['isEventDriven']:
                content_delivery_client = ContentDeliveryFactory.get(source["type"], dataflow_session)
                dfs[source['dataframeName']] = content_delivery_client.get_df(content_details=event_data,
                                                                              content_validation=source)
            else:
                content_delivery_client = ContentDeliveryFactory.get(source["type"], dataflow_session)
                dfs[source["dataframeName"]] = content_delivery_client.get_df(source)

        '''
        Check the phase
        train: hold on until the end of processing steps, saving reserved global variables to metadata
        inference: load the metadata into global variables
        '''
        metadata = dict()
        sharding_dict = list()
        phaseInfo = contents["phaseInfo"]
        # appending the staging folder with timestamp to differentiate between different requests.
        contents["stagingDestination"]["folder"] += datetime.now().strftime("_%d_%m_%Y_%H_%M_%S")
        staging_namespace = contents["stagingDestination"]["namespace"]
        staging_bucket = contents["stagingDestination"]["bucket"]
        staging_folder = contents["stagingDestination"]["folder"]
        staging_path = f'oci://{staging_bucket}@{staging_namespace}/{staging_folder}'

        if phase == INFERENCING:
            metadata_dependent_raw = get_object(object_storage_client,
                                                phaseInfo["connector"]["namespace"],
                                                phaseInfo["connector"]["bucket"],
                                                phaseInfo["connector"]["objectName"])
            metadata_dependent = json.loads(metadata_dependent_raw)
            for global_variable in RESERVED_METADATA:
                if global_variable in metadata_dependent:
                    metadata[global_variable] = metadata_dependent[global_variable]
        elif phase != TRAINING:
            raise Exception("phaseInfo is not correct")

        # conducting processing steps
        processing_steps = contents["processingSteps"]
        for step_config in processing_steps:
            if step_config["stepType"] == SINGLE_DATAFRAME_PROCESSING:
                for step in step_config["configurations"]["steps"]:
                    func_name = step["stepName"]
                    # one_hot_encoding and sharding are specific because it is data dependent transformation
                    # Usually one_hot_encoding will be conducted after merge and joining if multiple datasets involves
                    # TODO: for both cases, we need to add UNKNOWN category if it doesn't exist in training data
                    if func_name == "one_hot_encoding":
                        # if it's training, we will put all the distinct categories of the specific column
                        # to metadata for later usage
                        if phase == TRAINING:
                            distinct_categories, dfs[step_config["configurations"]["dataframeName"]] = \
                                eval(func_name)(dfs[step_config["configurations"]["dataframeName"]], **step["args"])
                            if 'distinct_categories' not in metadata:
                                metadata["distinct_categories"] = dict()
                            metadata["distinct_categories"][step["args"]["category"]] = distinct_categories
                        elif phase == INFERENCING:
                            step["args"]["distinct_categories"] = metadata["distinct_categories"][step["args"]["category"]]
                            _, dfs[step_config["configurations"]["dataframeName"]] = \
                                eval(func_name)(dfs[step_config["configurations"]["dataframeName"]], **step["args"])
                    # sharding also needs to be specially treated. We need:
                    # 1. Check whether it's the last one of the processing_steps
                    # 2. Saving multiple dataframes
                    elif func_name == "sharding":
                        step_config_len = len(step_config["configurations"]["steps"]) - 1
                        if (step_config["configurations"]["steps"]).index(step) != step_config_len:
                            raise Exception("Sharding must be the last of processing steps")
                        sharding_dfs = eval(func_name)(dfs[step_config["configurations"]["dataframeName"]], **step["args"])
                        sharding_dict = list(sharding_dfs.keys())
                        dfs.update(sharding_dfs)
                    # Pivoting also needs specific treatment since it's also a data dependent processing
                    # Usually pivoting will be conducted after merge and joining if multiple datasets involves
                    # If training, we should pick out the distinct item of assigned column and store it inside metadata
                    # If inferencing, we should read pre-stored distinct_column_values
                    # from metadata pass it for pivoting function
                    elif func_name == "spark_pivoting":
                        if phase == TRAINING:
                            distinct_column_values, dfs[step_config["configurations"]["dataframeName"]] = \
                                eval(func_name)(dfs[step_config["configurations"]["dataframeName"]], **step["args"])
                            flat_distinct_column_values = [item for sublist in distinct_column_values for item in sublist]
                            metadata['distinct_column_values'] = flat_distinct_column_values
                        elif phase == INFERENCING:
                            step['args']['distinct_column_values'] = metadata['distinct_column_values']
                            _, dfs[step_config['configurations']['dataframeName']] = \
                                eval(func_name)(dfs[step_config["configurations"]["dataframeName"]], **step["args"])
                    else:
                        dfs[step_config["configurations"]["dataframeName"]] = \
                            eval(func_name)(dfs[step_config["configurations"]["dataframeName"]], **step["args"])
            elif step_config["stepType"] == COMBINE_DATAFRAMES:
                if step_config["configurations"]["type"] == JOIN:
                    left = dfs[step_config["configurations"]["joinConfiguration"]["left"]]
                    right = dfs[step_config["configurations"]["joinConfiguration"]["right"]]
                    dfs[step_config["configurations"]["dataframeName"]] = time_series_join([left, right])
                elif step_config["configurations"]["type"] == MERGE:
                    left = dfs[step_config["configurations"]["mergeConfiguration"]["left"]]
                    right = \
                        dfs[step_config["configurations"]["mergeConfiguration"]["right"]]
                    dfs[step_config["configurations"]["dataframeName"]] = \
                        time_series_merge(left, right)

        # prepare the staging file path
        preprocessed_data_prefix_to_column = dict()

        # writing it to output destination
        if len(sharding_dict) == 0:
            final_df = dfs[contents["stagingDestination"]["combinedResult"]]
            final_df.coalesce(1).write.csv(staging_path, header=True)
            preprocessed_data_prefix_to_column[staging_folder] = final_df.columns
        else:
            # Sharded dfs
            idx = 0
            for df in sharding_dict:
                final_df = dfs[df]
                final_df.coalesce(1).write.csv(
                    staging_path + str(idx), header=True)
                preprocessed_data_prefix_to_column[
                    staging_folder + str(idx)] = final_df.columns
                idx += 1

        output_processed_data_info = list()
        preprocessed_data_details = {
            'namespace': staging_namespace,
            'bucket': staging_bucket,
            'prefix': staging_folder
            }

        list_objects_response = object_storage_client.list_objects(
            namespace_name=preprocessed_data_details['namespace'],
            bucket_name=preprocessed_data_details['bucket'],
            prefix=preprocessed_data_details['prefix'])
        assert list_objects_response.status == 200, \
            f'Error listing objects: {list_objects_response.text}'
        objects_details = list_objects_response.data

        data_asset_detail = preprocessed_data_details
        data_asset_detail.pop('prefix')
        for object_details in objects_details.objects:
            if object_details.name.endswith('.csv'):
                prefix = object_details.name.split('/')[0]
                if prefix not in preprocessed_data_prefix_to_column:
                    continue
                columns = preprocessed_data_prefix_to_column[prefix]
                data_asset_detail['object'] = object_details.name
                output_processed_data_info.append({
                    "object": object_details.name,
                    "namespace": staging_namespace,
                    "bucket": staging_bucket,
                    "columns": columns
                })
        print(output_processed_data_info)
        # writing metadata to metadata bucket during train
        if phase == TRAINING:
            object_storage_client.put_object(
                phaseInfo["connector"]["namespace"],
                phaseInfo["connector"]["bucket"],
                phaseInfo["connector"]["objectName"],
                json.dumps(metadata))
        return output_processed_data_info
    except Exception as e:
        raise Exception(e)


def ctx_event_data(value):
    try:
        value = json.loads(value)
        return value if len(value) > 0 else None
    except Exception as exception:
        print(exception)
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--event_data", required=False, type=ctx_event_data)
    parser.add_argument("--response", required=True)
    parser.add_argument("--phase", required=True)
    args = parser.parse_args()

    spark = get_spark_context(dataflow_session=dataflow_session)

    object_storage_client = get_authenticated_client(
        client=oci.object_storage.ObjectStorageClient,
        dataflow_session=dataflow_session)
    config = json.loads(args.response)
    staging_info = parse_and_process_data_preprocessing_config(
        object_storage_client, spark, config, args.phase)

    model_ids = []
    api_configuration = \
        config["serviceApiConfiguration"]["anomalyDetection"]
    ad_utils = AdUtils(dataflow_session,
                       api_configuration['profileName'],
                       api_configuration['serviceEndpoint'])
    outputInfo = config["outputDestination"]
    if args.phase == "applyAndFinalize":
        result = {}
        for data_asset_detail in staging_info:
            try:
                model_id = ad_utils.train(
                    api_configuration['projectId'],
                    api_configuration['compartmentId'],
                    data_asset_detail)
                model_ids.append({
                    "model_id": model_id,
                    "columns": data_asset_detail["columns"]})
            except AssertionError as e:
                print(e)
        result['model_ids'] = model_ids
        object_storage_client.put_object(
            outputInfo["namespace"],
            outputInfo["bucket"],
            outputInfo["folder"],
            json.dumps(result, default=lambda o: o.__dict__, indent=4))
    elif args.phase == "apply":
        model_ids_serialized = get_object(object_storage_client,
                               outputInfo["namespace"],
                               outputInfo["bucket"],
                               outputInfo["folder"])
        model_ids = json.loads(model_ids_serialized)
        ad_utils.infer(compartment_id=api_configuration["compartmentId"],
                       model_ids=model_ids,
                       staging_details=staging_info,
                       output_path=outputInfo["bucket"])
