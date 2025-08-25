"""
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive
# License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or
# Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0.
# You may choose either license.

##########################################################################
# staream_video_demo_cv2.py
#
# @author: Anand Jha (anand.j.jha@oracle.com), Aug 2025
#
# Supports Python 3
##########################################################################
# Info:
usage: stream_video_demo.py [-h] --compartment-id [COMPARTMENT_ID] --subnet-id [SUBNET_ID] --camera-url [CAMERA_URL] --namespace [NAMESPACE] --bucket [BUCKET] [--prefix PREFIX] [-v]

arguments:
-h, --help Show this help message and exit
-v, --verbose Print logs
--compartment-id COMPARTMENT_OCID Compartment OCID for the resources
--subnet-id SUBNET_ID Subnet for the private endpoint
--camera-url CAMERA_URL Camera URL for the stream
--namespace NAMESPACE Namespace of the bucket
--bucket BUCKET_NAME Bucket name
optional arguments:
--prefix PREFIX Prefix
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
    Class to use all functionalities of Streaming Service
    """

    def __init__(self,compartment_id: str,subnet_id: str,camera_url: str, namespace: str,bucket: str,prefix: str, oci_config: dict, service_endpoint: str):
        self.compartment_id = compartment_id
        self.camera_url = camera_url
        self.namespace = namespace
        self.bucket = bucket
        self.prefix = prefix
        self.subnet_id = subnet_id
        token_file = oci_config['security_token_file']
        with open(token_file, 'r') as f:
             token = f.read()
        private_key = oci.signer.load_private_key_from_file(config['key_file'])
        signer = oci.auth.signers.SecurityTokenSigner(token, private_key)
        self.client = oci.ai_vision.AIServiceVisionClient(
            config=oci_config, signer=signer,
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
        self.create_stream_group_details = oci.ai_vision.models.CreateStreamGroupDetails() 
    
    def create_private_endpoint(self, display_name="Vision_Private_Endpoint"):
        """

        :param display_name: Display name for the Vision Private Endpoint
        :return: None
        """

        if self.subnet_id is None or self.subnet_id == "":
            logger.error("subnet id not found")
            sys.exit()
            # return 0

        if self.compartment_id is None or self.compartment_id == "":
            logger.error("compartment id not found")
            sys.exit()
            # return 0

        logger.info("Starting Vision Private Endpoint Creation....")
        
        self.create_vision_private_endpoint_details.display_name = display_name
        self.create_vision_private_endpoint_details.subnet_id = self.subnet_id
        self.create_vision_private_endpoint_details.compartment_id = self.compartment_id

        logger.info("create private endpoint details %s", self.create_vision_private_endpoint_details)
        create_private_endpoint_response = self.client.create_vision_private_endpoint(self.create_vision_private_endpoint_details)
        logger.info("checking Private Endpoint Creation work request id %s",create_private_endpoint_response.headers['opc-work-request-id'])
        timeout_seconds = 300  # 5 minutes
        start_time = time.time()
        while True:
            create_private_endpoint_work_request = self.client.get_work_request(create_private_endpoint_response.headers['opc-work-request-id'])
            status = create_private_endpoint_work_request.data.status
            logger.info("get current status of work request id %s for Private Endpoint Creation %s", create_private_endpoint_response.headers['opc-work-request-id'], create_private_endpoint_work_request.data.status)
            if status == 'SUCCEEDED':
                return create_private_endpoint_response.data.id
            elif status == 'FAILED':
                logger.error("creation of private endpoint failed %s",create_private_endpoint_response.headers)
                sys.exit()
            elif time.time() - start_time > timeout_seconds:
                raise TimeoutError("Operation timed out after 5 minutes.")
            time.sleep(120)
    
    def create_Stream_Source(self, vision_private_endpoint_ocid, display_name="Vision_Stream_Source"):
        """

        :param vision_private_endpoint_ocid: Vision Private Endpoint OCID
        :return: None
        """

        if self.camera_url is None or self.camera_url == "":
            logger.error("camera url not found")
            sys.exit()
            # return 0

        if vision_private_endpoint_ocid is None or vision_private_endpoint_ocid == "":
            logger.error("vision private endpoint id is not found")
            sys.exit()
            # return 0

        logger.info("Starting Stream Source Creation....")
        
        self.private_stream_network_access_deatils.stream_access_type = "PRIVATE"
        self.private_stream_network_access_deatils.private_endpoint_id = vision_private_endpoint_ocid
        self.rtsp_source_details.camera_url = self.camera_url
        self.rtsp_source_details.stream_network_access_details = self.private_stream_network_access_deatils
        
        self.create_stream_source_details.compartment_id = compartment_id
        self.create_stream_source_details.display_name = display_name
        self.create_stream_source_details.stream_source_details = self.rtsp_source_details

        logger.info("create stream source details %s", self.create_stream_source_details)
        create_stream_source_response = self.client.create_stream_source(self.create_stream_source_details)
        logger.info("checking Stream Source Creation work request id %s",create_stream_source_response.headers['opc-work-request-id'])
        timeout_seconds = 120  # 2 minutes
        start_time = time.time()

        while True:
            create_stream_source_work_request = self.client.get_work_request(create_stream_source_response.headers['opc-work-request-id'])
            logger.info("get current status of work request id %s for Stream Source Creation %s",create_stream_source_response.headers['opc-work-request-id'], create_stream_source_work_request.data.status)

            if create_stream_source_work_request.data.status  == 'SUCCEEDED':
                return create_stream_source_response.data.id
            elif create_stream_source_work_request.data.status == 'FAILED':
                logger.error("creation of stream source failed %s",create_stream_source_response.headers)
                sys.exit()
            elif time.time() - start_time > timeout_seconds:
                raise TimeoutError("Operation timed out after 2 minutes.")
            time.sleep(60)
    

    def create_Stream_Job(self, stream_source_ocid, display_name="Vision_Stream_Job"):
        """

        :param stream_source_ocid: Stream Source OCID
        :return: None
        """

        # For Object Tracker (Only "face" supported as of now) - commend if not required
        FEATURES = [
            {
                "featureType": "OBJECT_TRACKING",
                "trackingTypes":[
                    {
                        "objects": ["face"],
                        "maxResults": 5,
                        "shouldReturnLandmarks": True,
                    }
                ]
            }
        ]

        if self.namespace is None or self.namespace == "":
            logger.error("namespace not found")
            sys.exit()
            # return 0

        if self.bucket is None or self.bucket == "":
            logger.error("bucket not found")
            sys.exit()
            # return 0
        
        if self.bucket is None or self.bucket == "":
            self.prefix = "Testing" 
        
        
        logger.info("Starting Stream Job Creation....")

        # Choose output location in object storage, make sure you have created the bucket
        self.output_location.namespace_name = self.namespace
        self.output_location.bucket_name = self.bucket
        self.output_location.prefix = self.prefix
        
        self.create_stream_job_details.stream_source_id = stream_source_ocid
        self.create_stream_job_details.compartment_id = self.compartment_id
        self.create_stream_job_details.display_name = display_name
        self.create_stream_job_details.stream_output_location = self.output_location
        self.create_stream_job_details.features = FEATURES
        
        logger.info("create stream job details %s", self.create_stream_job_details)
        create_stream_job_response = self.client.create_stream_job(self.create_stream_job_details)
        logger.info("checking stream job creation work request id %s", create_stream_job_response.headers['opc-work-request-id'])
        timeout_seconds = 120  # 2 minutes
        start_time = time.time()

        while True:
            create_stream_job_work_request = self.client.get_work_request(create_stream_job_response.headers['opc-work-request-id'])
            logger.info("get current status of work request id %s for Stream job Creation %s", create_stream_job_response.headers['opc-work-request-id'], create_stream_job_work_request.data.status)

            if create_stream_job_work_request.data.status  == 'SUCCEEDED' :
                return create_stream_job_response.data.id
            elif create_stream_job_work_request.data.status == 'FAILED':
                logger.error("creation of stream job failed %s",create_stream_job_response.headers)
                sys.exit()
            elif time.time() - start_time > timeout_seconds:
                raise TimeoutError("Operation timed out after 2 minutes.")
            time.sleep(60)


    def create_Stream_Group(self, stream_source_ocid, display_name="Vision_Stream_Group"):
        streamOverlap = [stream_source_ocid]
        self.create_stream_group_details.compartment_id = self.compartment_id
        self.create_stream_group_details.display_name = display_name
        self.create_stream_group_details.is_enabled = True
        self.create_stream_group_details._stream_source_ids = streamOverlap

        logger.info("Create Stream Group Details %s", self.create_stream_group_details)
        create_stream_group_response = self.client.create_stream_group(self.create_stream_group_details)
        logger.info("checking stream group creation work request id  %s", create_stream_group_response.headers['opc-work-request-id'])
        timeout_seconds = 120  # 2 minutes
        start_time = time.time()

        while True:
            create_stream_group_work_request = self.client.get_work_request(create_stream_group_response.headers['opc-work-request-id'])
            logger.info("get current status of work request id %s for stream group Creation %s",create_stream_group_response.headers['opc-work-request-id'], create_stream_group_work_request.data.status)

            if create_stream_group_work_request.data.status  == 'SUCCEEDED' :
                return create_stream_group_response.data.id
            elif create_stream_group_work_request.data.status == 'FAILED':
                logger.error("creation of stream job failed %s",create_stream_group_response.headers)
                sys.exit()
            elif time.time() - start_time > timeout_seconds:
                raise TimeoutError("Operation timed out after 2 minutes.")
            time.sleep(60)

    def start_Stream_Job(self, stream_job_ocid):
        """

        :param stream_job_ocid: Stream Job OCID
        :return: None
        """

        logger.info("start stream job id %s",stream_job_ocid)
        start_stream_job_response = self.client.start_stream_job(stream_job_ocid)
        logger.info("checking starting stream job work request id %s", start_stream_job_response.headers['opc-work-request-id'])
        timeout_seconds = 600  # 10 minutes
        start_time = time.time()

        while True:
            start_stream_job_work_request = self.client.get_work_request(start_stream_job_response.headers['opc-work-request-id'])
            logger.info("get current status of work request id %s for starting stream job %s", start_stream_job_response.headers['opc-work-request-id'], start_stream_job_work_request.data.status)
            
            if start_stream_job_work_request.data.status  == 'SUCCEEDED' :
                return stream_job_ocid
            elif start_stream_job_work_request.data.status == 'FAILED':
                logger.error("starting of stream job failed %s",start_stream_job_response.headers)
                sys.exit()
            elif time.time() - start_time > timeout_seconds:
                raise TimeoutError("Operation timed out after 10 minutes.")
            time.sleep(60)

    def stop_Stream_Job(self, stream_job_ocid):
        """

        :param stream_job_ocid: Stream Job OCID
        :return: None
        """

        logger.info("stop stream job id %s",stream_job_ocid)
        stop_stream_job_response = self.client.stop_stream_job(stream_job_ocid)
        logger.info("checking stopping stream job work request id %s", stop_stream_job_response.headers['opc-work-request-id'])
        timeout_seconds = 120  # 2 minutes
        start_time = time.time()

        while True:
            stop_stream_job_work_request = self.client.get_work_request(stop_stream_job_response.headers['opc-work-request-id'])
            logger.info("get current status of work request id %s for stopping Stream job %s", stop_stream_job_response.headers['opc-work-request-id'],  stop_stream_job_work_request.data.status)

            if stop_stream_job_work_request.data.status  == 'SUCCEEDED' :
                return stream_job_ocid
            elif stop_stream_job_work_request.data.status == 'FAILED':
                logger.error("stopping of stream job failed %s",stop_stream_job_response.headers)
                sys.exit()
            elif time.time() - start_time > timeout_seconds:
                raise TimeoutError("Operation timed out after 2 minutes.")
            time.sleep(60)
            
    def delete_Stream_Job(self, stream_job_ocid):
        """

        :param stream_job_ocid: Stream Job OCID
        :return: None
        """

        logger.info("Delete stream job id %s",stream_job_ocid)
        delete_stream_job_response = self.client.delete_stream_job(stream_job_ocid)
        logger.info("checking deleting stream job work request id %s", delete_stream_job_response.headers['opc-work-request-id'])
        timeout_seconds = 120  # 2 minutes
        start_time = time.time()

        while True:
            delete_stream_job_work_request = self.client.get_work_request(delete_stream_job_response.headers['opc-work-request-id'])
            logger.info("get current status of work request id %s for delete stream job %s",delete_stream_job_response.headers['opc-work-request-id'], delete_stream_job_work_request.data.status)

            if delete_stream_job_work_request.data.status  == 'SUCCEEDED' :
                return stream_job_ocid
            elif delete_stream_job_work_request.data.status == 'FAILED':
                logger.error("Deletion of stream job failed %s",delete_stream_job_response.headers)
                sys.exit()
            elif time.time() - start_time > timeout_seconds:
                raise TimeoutError("Operation timed out after 2 minutes.")
            time.sleep(60)
            
    def delete_Stream_Group(self, stream_group_ocid):
        """

        :param stream_group_ocid: Stream Group OCID
        :return: None
        """

        logger.info("Delete stream group id %s",stream_group_ocid)
        delete_stream_group_response = self.client.delete_stream_group(stream_group_ocid)
        logger.info("checking deleting stream group work request id %s", delete_stream_group_response.headers['opc-work-request-id'])
        timeout_seconds = 120  # 2 minutes
        start_time = time.time()

        while True:
            delete_stream_group_work_request = self.client.get_work_request(delete_stream_group_response.headers['opc-work-request-id'])
            logger.info("get current status of work request id %s for delete stream group %s", delete_stream_group_response.headers['opc-work-request-id'], delete_stream_group_work_request.data.status)
            if delete_stream_group_work_request.data.status  == 'SUCCEEDED' :
                return stream_group_ocid
            elif delete_stream_group_work_request.data.status == 'FAILED':
                logger.error("Deletion of stream group failed %s",delete_stream_group_response.headers)
                sys.exit()
            elif time.time() - start_time > timeout_seconds:
                raise TimeoutError("Operation timed out after 2 minutes.")
            time.sleep(60)
    
    def delete_Stream_Source(self, stream_source_ocid):
        """

        :param stream_source_ocid: Stream Source OCID
        :return: None
        """

        logger.info("Delete stream source id %s",stream_source_ocid)
        delete_stream_source_response = self.client.delete_stream_source(stream_source_ocid)
        logger.info("checking deleting stream source work request id %s", delete_stream_source_response.headers['opc-work-request-id'])
        timeout_seconds = 120  # 2 minutes
        start_time = time.time()

        while True:
            delete_stream_source_work_request = self.client.get_work_request(delete_stream_source_response.headers['opc-work-request-id'])
            logger.info("get current status of work request id %s for delete stream source %s",delete_stream_source_response.headers['opc-work-request-id'], delete_stream_source_work_request.data.status)
            if delete_stream_source_work_request.data.status  == 'SUCCEEDED' :
                return stream_source_ocid
            elif delete_stream_source_work_request.data.status == 'FAILED':
                logger.error("Deletion of stream source failed %s",delete_stream_source_response.headers)
                sys.exit()
            elif time.time() - start_time > timeout_seconds:
                raise TimeoutError("Operation timed out after 2 minutes.")
            time.sleep(60)
    
    def delete_Vision_Private_Endpoint(self, vision_private_endpoint_ocid):
        """

        :param vision_private_endpoint_ocid: Vision Private Endpoint OCID
        :return: None
        """
        
        logger.info("Delete Vision Private Endpoint %s",vision_private_endpoint_ocid)
        delete_Vision_Private_Endpoint_response = self.client.delete_vision_private_endpoint(vision_private_endpoint_ocid)
        logger.info("checking deleting Vision Private Endpoint work request id %s", delete_Vision_Private_Endpoint_response.headers['opc-work-request-id'])
        timeout_seconds = 300  # 5 minutes
        start_time = time.time()

        while True:
            delete_vision_private_endpoint_work_request = self.client.get_work_request(delete_Vision_Private_Endpoint_response.headers['opc-work-request-id'])
            logger.info("get current status of work request id %s for delete private endpoint %s", delete_Vision_Private_Endpoint_response.headers['opc-work-request-id'],  delete_vision_private_endpoint_work_request.data.status)

            if delete_vision_private_endpoint_work_request.data.status == 'SUCCEEDED' :
                return vision_private_endpoint_ocid
            elif delete_vision_private_endpoint_work_request.data.status == 'FAILED':
                logger.error("Deletion of stream job failed %s",delete_vision_private_endpoint_work_request.headers)
                sys.exit()
            elif time.time() - start_time > timeout_seconds:
                raise TimeoutError("Operation timed out after 5 minutes.")
            time.sleep(60)
    
if __name__ == '__main__':

    # pylint: disable=R1732
    parser = argparse.ArgumentParser()
    parser.add_argument('--compartment-id', type=str, required=True, help='Compartment')
    parser.add_argument("--subnet-id", type=str, help="Subnet")
    parser.add_argument("--camera-url", type=str, help='Camera Url for the Stream Source')
    parser.add_argument("--namespace", type=str, help="Namespace of the Bucket")
    parser.add_argument("--bucket", type=str, help="Bucket name")
    parser.add_argument("--prefix", type=str, help="Prefix")
    parser.add_argument("-v", "--verbose", help="Print logs", action='store_true')
    args = parser.parse_args()
    formatter = logging.Formatter(
        '%(asctime)s : {%(pathname)s:%(lineno)d} : %(name)s : %(levelname)s : %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

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
    subnet_id = args.subnet_id
    camera_url = args.camera_url
    namespace = args.namespace
    bucket = args.bucket
    prefix = args.prefix
    

    try:
        config = oci.config.from_file(
            '~/.oci/config', profile_name="DEFAULT")
    except oci.exceptions.ConfigFileNotFound as err:
        logger.error(err)
        sys.exit()
    
    service_endpoint = \
        f"https://vision.aiservice.{config.get('region')}.oci.oraclecloud.com"
    
    stream_videos = StreamVideo(compartment_id=compartment_id, subnet_id=subnet_id, camera_url=camera_url, 
                                namespace=namespace, bucket=bucket, prefix=prefix,  oci_config=config, service_endpoint=service_endpoint)
    
    
    vision_private_endpoint_ocid = stream_videos.create_private_endpoint()
    logger.info("Private Endpoint created successfully %s", vision_private_endpoint_ocid)
    
    stream_source_ocid = stream_videos.create_Stream_Source(vision_private_endpoint_ocid)
    logger.info("Stream Source created successfully %s", stream_source_ocid)

    stream_job_ocid = stream_videos.create_Stream_Job(stream_source_ocid)
    logger.info("Stream Job created successfully %s", stream_job_ocid)

    stream_group_ocid = stream_videos.create_Stream_Group(stream_source_ocid)
    logger.info("Stream Group created successfully %s", stream_group_ocid)

    start_stream_job = stream_videos.start_Stream_Job(stream_job_ocid)
    logger.info("Started Stream Job successfully %s", stream_job_ocid)

    time.sleep(60)

    stop_stream_job = stream_videos.stop_Stream_Job(stream_job_ocid)
    logger.info("Stopped Stream Job successfully %s", stream_job_ocid)

    time.sleep(60)

    delete_stream_job = stream_videos.delete_Stream_Job(stream_job_ocid)
    logger.info("Stream Job deleted successfully %s", stream_job_ocid)
    
    delete_stream_group = stream_videos.delete_Stream_Group(stream_group_ocid)
    logger.info("Stream Group deleted successfully %s", stream_group_ocid)

    delete_stream_source = stream_videos.delete_Stream_Source(stream_source_ocid)
    logger.info("Stream Source deleted successfully %s", stream_source_ocid)

    delete_Vision_Private_Endpoint = stream_videos.delete_Vision_Private_Endpoint(vision_private_endpoint_ocid)
    logger.info("Vision Private Endpoint deleted successfully %s", vision_private_endpoint_ocid)
