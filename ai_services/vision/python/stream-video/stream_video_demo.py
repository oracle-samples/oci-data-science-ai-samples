"""
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive
# License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or
# Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0.
# You may choose either license.

##########################################################################
# analyze_video_demo_cv2.py
#
# @author: Anand Jha (anand.j.jha@oracle.com), Aug 2025
#
# Supports Python 3
##########################################################################
# Info:
usage: stream_video_demo.py [-h] --compartment-id [COMPARTMENT_ID] --camera-url [CAMERA_URL] --namespace [NAMESPACE] 
    --bucket [BUCKET] --prefix [PREFIX] --feature [FEATURE] [-v]

optional arguments:
  -h, --help  show this help message and exit
  -v, --verbose Print logs
  --compartment-id COMPARTMENT_OCID compartment for the resources
  --camera-url CAMERA_URL camera url for the stream
  --namespace NAMESPACE namespace of the Bucket
  --bucket BUCKET_NAME bucket name
  --prefix PREFIX prefix
  --feature FEATURE feature

##################################################################################
"""

import os
import sys
import json
import math
import time
import logging
import argparse
from glob import glob

import oci

class StreamVideo:
    """
        A class to
    """

    def __init__(
            self,
            compartment_id: str,
            camera_url: int,
            namespace: str,
            bucket: str,
            prefix: str,
            feature: str,
            subnet_id: str,
            oci_config: dict,
            service_endpoint: str
    ):
        
        self.compartment_id = compartment_id
        camera_url = camera_url
        namespace = namespace
        bucket = bucket
        prefix = prefix
        feature = feature
        subnet_id = subnet_id
        self.client = oci.ai_vision.AIServiceVisionClient(
            config=oci_config,
            service_endpoint=service_endpoint)
         
        self.create_stream_source_details = oci.ai_vision.models.CreateStreamSourceDetails()
        self.create_stream_job_details = oci.ai_vision.models.CreateStreamJobDetails()
        self.create_stream_group_details = oci.ai_vision.models.CreateStreamGroupDetails()
        self.create_vision_private_endpoint_details = oci.ai_vision.models.CreateVisionPrivateEndpointDetails()
        self.private_stream_network_access_deatils = oci.ai_vision.models.PrivateStreamNetworkAccessDetails()
        self.rtsp_source_details = oci.ai_vision.models.RtspSourceDetails()
        self.update_stream_source_details = oci.ai_vision.models.UpdateStreamSourceDetails()
        self.update_stream_job_details = oci.ai_vision.models.UpdateStreamJobDetails()
        self.update_stream_group_details = oci.ai_vision.models.UpdateStreamGroupDetails()
        self.update_vision_private_endpoint_details = oci.ai_vision.models.UpdateVisionPrivateEndpointDetails()
        self.output_location = oci.ai_vision.models.ObjectStorageOutputLocation()

    
    
    def create_private_endpoint(self, display_name="Vision_Private_Endpoint"):
        """

        :param display_name: Display name for the Vision Private Endpoint
        :return: None
        """

        self.create_vision_private_endpoint_details.display_name = display_name
        self.create_vision_private_endpoint_details.subnet_id = self.subnet_id
        self.create_vision_private_endpoint_details.compartment_id = self.compartment_id
        
        create_private_endpoint_request = self.client.create_vision_private_endpoint(self.create_vision_private_endpoint_details)
        
        while True:
            create_private_endpoint_work_request = self.client.get_work_request(create_private_endpoint_request.headers['opc-work-request-id'])

            if create_private_endpoint_work_request.data.status  == 'SUCCEEDED':
                return create_private_endpoint_request.data.id
            elif create_private_endpoint_work_request.data.status == 'FAILED':
                return None
            time.sleep(30) 
    
    def create_Stream_Source(self, vision_private_endpoint_ocid, display_name="Vision_Stream_Source"):
        
        self.private_stream_network_access_deatils.stream_access_type = "PRIVATE"
        self.private_stream_network_access_deatils.private_endpoint_id = vision_private_endpoint_ocid
        self.rtsp_source_details.camera_url = self.camera_url
        self.rtsp_source_details.stream_network_access_details = self.private_stream_network_access_deatils
        
        self.create_stream_source_details.compartment_id = compartment_id
        self.create_stream_source_details.display_name = display_name
        self.create_stream_source_details.stream_source_details = self.rtsp_source_details
        
        create_stream_source_request = self.client.create_stream_source(self.create_stream_source_details)
        while True:
            create_stream_source_work_request = self.client.get_work_request(create_stream_source_request.headers['opc-work-request-id'])

            if create_stream_source_work_request.data.status  == 'SUCCEEDED':
                return create_stream_source_request.data.id
            elif create_stream_source_work_request.data.status == 'FAILED':
                return None
            time.sleep(30) 
    
    def create_Stream_Job(self, stream_source_ocid, display_name="Vision_Stream_Job"):
        self.create_stream_job_details.stream_source_id = stream_source_ocid
        # For Object Tracker (Only "face" supported as of now) - commend if not required
        self.create_stream_job_details.features = self.feature
        
        self.output_location.namespace_name = self.namespace
        self.output_location.bucket_name = self.bucket
        self.output_location.prefix = self.prefix
        
        # Choose output location in object storage, make sure you have created the bucket
        self.create_stream_job_details.stream_output_location = self.output_location
        
        self.create_stream_job_details.compartment_id = self.compartment_id
        self.create_stream_job_details.display_name = display_name
        
        create_stream_job_request = self.client.create_stream_job(self.create_stream_job_details)
        while True:
            create_stream_job_work_request = self.client.get_work_request(create_stream_job_request.headers['opc-work-request-id'])
            if create_stream_job_work_request.data.status  == 'SUCCEEDED' :
                return create_stream_job_request.data.id
            if create_stream_job_work_request.data.status == 'FAILED':
                return None
            time.sleep(30)

    def start_Stream_Job(self, stream_job_ocid):
        start_stream_job = self.client.start_stream_job(stream_job_ocid)
        while True:
            start_stream_job_work_request = self.client.get_work_request(start_stream_job.headers['opc-work-request-id'])
            print(start_stream_job_work_request.data.status)
            if start_stream_job_work_request.data.status  == 'SUCCEEDED' :
                return True
            if start_stream_job_work_request.data.status == 'FAILED' :
                return False
            time.sleep(30)

    def stop_Stream_Job(self, stream_job_ocid):
        stop_stream_job = self.client.start_stream_job(stream_job_ocid)
        while True:
            stop_stream_job_work_request = self.client.get_work_request(stop_stream_job.headers['opc-work-request-id'])
            if stop_stream_job_work_request.data.status  == 'SUCCEEDED' :
                return True
            if stop_stream_job_work_request.data.status == 'FAILED' :
                return False
            time.sleep(30)

    def delete_Stream_Job(self, stream_job_ocid):
        delete_stream_job = self.client.delete_stream_job(stream_job_ocid)
        while True:
            delete_stream_job_work_request = self.client.get_work_request(delete_stream_job.headers['opc-work-request-id'])
            if delete_stream_job_work_request.data.status  == 'SUCCEEDED' :
                return True
            if delete_stream_job_work_request.data.status == 'FAILED' :
                return False
            time.sleep(30)
    

    def delete_Stream_Source(self, stream_source_ocid):
        delete_stream_source = self.client.delete_stream_job(stream_source_ocid)
        while True:
            delete_stream_source_work_request = self.client.get_work_request(delete_stream_source.headers['opc-work-request-id'])
            if delete_stream_source_work_request.data.status  == 'SUCCEEDED' :
                return True
            if delete_stream_source_work_request.data.status == 'FAILED' :
                return False
            time.sleep(30)
    
    def delete_Vision_Private_Endpoint(self, vision_private_endpoint_ocid):
        delete_Vision_Private_Endpoint_request = self.client.delete_vision_private_endpoint(vision_private_endpoint_ocid)
        while True:
            delete_vision_private_endpoint_work_request = self.client.get_work_request(delete_Vision_Private_Endpoint_request.headers['opc-work-request-id'])
            if delete_vision_private_endpoint_work_request.data.status  == 'SUCCEEDED' :
                return True
            if delete_vision_private_endpoint_work_request.data.status == 'FAILED' :
                return False
            time.sleep(30)
    
if __name__ == '__main__':

    # pylint: disable=R1732
    parser = argparse.ArgumentParser()
    parser.add_argument('--compartment-id', type=str, required=True, help='Compartment')
    parser.add_argument("--camera-url", type=str, help='Camera Url for the Stream Source')
    parser.add_argument("--namespace", type=str, help="Namespace of the Bucket")
    parser.add_argument("--bucket", type=str, help="Bucket name")
    parser.add_argument("--prefix", type=str, help="Prefix")
    parser.add_argument("--feature", type=json, help="Json")
    parser.add_argument("-v", "--verbose", help="Print logs", action='store_true')
    args = parser.parse_args()

    formatter = logging.Formatter(
        '%(asctime)s : {%(pathname)s:%(lineno)d} : %(name)s : %(levelname)s : %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    start_timeit = time.time()

    if args.verbose:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        file_handler = logging.FileHandler(
            'stream_video_demo.log', mode='w')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    compartment_id = args.compartment_id
    camera_url = args.camera_url
    namespace = args.namespace
    bucket = args.bucket
    prefix = args.prefix
    feature = args.feature
    subnet_id = args.subnet_id


    try:
        config = oci.config.from_file(
            '~/.oci/config', profile_name="DEFAULT")
    except oci.exceptions.ConfigFileNotFound as err:
        logger.error(err)
        sys.exit()

    service_endpoint = \
        f"https://vision.aiservice.{config.get('region')}.oci.oraclecloud.com"
    
    stream_videos = StreamVideo(compartment_id=compartment_id, camera_url=camera_url, 
                                namespace=namespace, bucket=bucket, prefix=prefix, feature=feature, 
                                subnet_id=subnet_id, oci_config=config, service_endpoint=service_endpoint)
    
    
    vision_private_endpoint_ocid = StreamVideo.create_private_endpoint()
    if vision_private_endpoint_ocid == None:
        sys.exit("Error: Creation of Vision Private Endpoint Failed.....")
    
    stream_source_ocid = StreamVideo.create_Stream_Source(vision_private_endpoint_ocid)
    if StreamVideo.create_Stream_Source(vision_private_endpoint_ocid) == None:
        sys.exit("Error: Creation of Stream Source Failed.....")

    stream_job_ocid = StreamVideo.create_Stream_Job(stream_source_ocid)
    if stream_job_ocid == None:
        sys.exit("Error: Creation of Stream Job Failed.....")
        
    start_stream_job = StreamVideo.start_Stream_Job(stream_job_ocid)
    if stream_job_ocid == False:
        sys.exit("Error: Start of Stream Job Failed.....")
    
    stop_stream_job = StreamVideo.stop_Stream_Job(stream_job_ocid)
    if stop_stream_job == False:
        sys.exit("Error: Stop of Stream Job Failed.....")
    
    delete_stream_job = StreamVideo.delete_Stream_Job(stream_job_ocid)
    if delete_stream_job == False:
        sys.exit("Error: Deletion of Stream Job Failed.....")

    delete_stream_source = StreamVideo.delete_Stream_Source(stream_source_ocid)
    if delete_stream_source == False:
        sys.exit("Error: Deletion of Stream Source Failed.....")

    delete_Vision_Private_Endpoint = StreamVideo.delete_Vision_Private_Endpoint(vision_private_endpoint_ocid)
    if delete_Vision_Private_Endpoint == False:
        sys.exit("Error: Deletion of Vision Private Endpoint Failed.....")