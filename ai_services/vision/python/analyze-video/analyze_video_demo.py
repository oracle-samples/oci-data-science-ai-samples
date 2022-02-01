"""
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive
# License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or
# Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0.
# You may choose either license.

##########################################################################
# analyze_video_demo_cv2.py
#
# @author: Arunjeyan TVSV (arunjeyan.tvsv@oracle.com), Shivam Singala (shivam.singla@oracle.com), Jan 2022
#
# Supports Python 3
##########################################################################
# Info:
# Analyze object present in video using OCI AI Vision service.
usage: analyze_video_demo.py [-h] --video-file VIDEO_FILE [--model-id MODEL_ID] 
    [--output-frame-rate OUTPUT_FRAME_RATE] [--confidence-threshold CONFIDENCE_THRESHOLD] [-v]

optional arguments:
  -h, --help            show this help message and exit
  --video-file VIDEO_FILE
                        video input file path
  --model-id MODEL_ID   custom trained model id for inference
  --output-frame-rate OUTPUT_FRAME_RATE
                        output frames per second
  --confidence-threshold CONFIDENCE_THRESHOLD
                        confidence threshold values are added
  -v, --verbose         Print logs
##################################################################################
"""

import os
import sys
import json
import math
import time
import base64
import shutil
import logging
import argparse
from glob import glob
from pathlib import Path
from urllib import response

import oci

import cv2
from joblib import delayed, Parallel
from moviepy.editor import VideoFileClip


N_POOL = 1
MAX_RESULTS = 10

# pylint: disable=R0902
class AnalyzeVideo:
    """
        A class to analyse video frame by frame
    """

    def __init__(
            self,
            video_file: str,
            input_frame_rate: int,
            custom_model_id: str,
            oci_config: dict,
            service_endpoint: str
    ):
        self.results_directory = Path("results")
        self.video_file = video_file
        self.output_frame_rate = input_frame_rate
        self.custom_model_id = custom_model_id
        self.client = oci.vision_service.AIServiceVisionClient(
            config=oci_config,
            service_endpoint=service_endpoint)
        self.inline_image_details = oci.vision_service.models.InlineImageDetails()
        self.analyze_image_details = oci.vision_service.models.AnalyzeImageDetails()
        self.image_object_detection_feature = oci.vision_service.models.ImageObjectDetectionFeature()
        self.image_object_detection_feature.max_results = MAX_RESULTS

        if self.custom_model_id is not None:
            self.image_object_detection_feature.model_id = self.custom_model_id
        else:
            logger.info("fallback onto the pretrained model")

    # pylint: disable=E1101
    def run(self, results_directory="results"):
        """

        :param results_directory: directory where all frames results will be stored
        :return: None
        """

        self.results_directory = Path(results_directory)
        logger.info("entered processing video")
        input_args = []

        if not os.path.exists(self.video_file):
            logger.error("video file not found")
            sys.exit()
            # return 0

        video_file_clip = VideoFileClip(self.video_file)
        video_duration = video_file_clip.reader.duration
        in_fps = video_file_clip.reader.fps
        if out_frame_rate > in_fps:
            logger.error(
                "output frame rate : %s cannot be greater than video frame rate: %s ",
                str(out_frame_rate), str(in_fps)
            )
            sys.exit()
        width_ = video_file_clip.w
        height_ = video_file_clip.h
        logger.info("video in fps : %s", str(in_fps))
        logger.info("video total duration : %s seconds", str(video_duration))
        logger.info("video total frames: %s", str(video_file_clip.reader.nframes))

        if not self.results_directory.exists():
            os.makedirs(self.results_directory.name)
        
        with Parallel(n_jobs=N_POOL, prefer="threads") as parallel:
            for i, frame in enumerate(video_file_clip.iter_frames(fps=self.output_frame_rate)):
                logger.info("Fetching Frame Number: %s", str(i))

                _, buffer = cv2.imencode('.jpg', frame)

                encoded_string = base64.b64encode(buffer)
                input_args.append([encoded_string, i])

                input_args_length = len(input_args)
                if i != 0 and (i + 1) % N_POOL == 0:
                    logger.info("Started analysing frames from : %s to %s",
                                str((i + 1)-N_POOL), str(i))
                    self.fetch_results_n_save_responses(input_args, input_args_length, parallel)
                    logger.info("Analysed frames from %s to %s",
                                str((i + 1)-N_POOL), str(i))
                    input_args = []
            input_args_length = len(input_args)
            if 0 < input_args_length <= 5:
                logger.info("Started analysing for %s frames ", str(input_args_length))
                self.fetch_results_n_save_responses(input_args, input_args_length, parallel)
                logger.info("Analysed frames for %s frames",
                            str(input_args_length))

        video_file_clip.close()
        logger.info("processing video completed")
        return video_duration, in_fps, height_, width_

    def fetch_results_n_save_responses(self, input_args, input_args_length, parallel):
        """
        :param input_args: input arguments
        :param input_args_length: input argument length
        :param parallel: joblib parallel object
        """
        results = parallel(delayed(self.fetch_results)(
            encoded_string=input_args[j][0],
            frame_number=input_args[j][1])
                           for j in range(input_args_length))
        parallel(delayed(self.save_responses)(
            response=results[k],
            frame_number=input_args[k][1])
                 for k in range(input_args_length))

    def save_responses(self, response, frame_number):
        """
        :param encoded_string: image in encoded string format
        :param frame_number: frame number count
        :param input_frame_rate: frame per second to detect
        :return: None
        """
        logger.info("Fetched results for frame number : %s", frame_number)

        if frame_number == 0:
            second = 0
        else:
            second = math.floor(frame_number / self.output_frame_rate)

        if response is not None:
            od_frame_res = {
                "od_response": response,
                "frame": str(frame_number),
                "seconds": second
            }

            with open(
                    self.results_directory / f"frame_{str(frame_number).zfill(6)}.json",
                    "w", encoding="utf-8") as filewriter:
                to_save = {"od_frame_res": od_frame_res}
                json.dump(to_save, filewriter)


    def fetch_results(self, encoded_string, frame_number):
        """
        :param encoded_string: image in encoded string format
        :return: response from object detection API
        """

        features = [self.image_object_detection_feature]
        self.inline_image_details.data = encoded_string.decode("utf-8")

        self.analyze_image_details.image = self.inline_image_details
        self.analyze_image_details.features = features

        response = None
        try:
            response = self.client.analyze_image(analyze_image_details=self.analyze_image_details)
        except oci.exceptions.ServiceError as error:
            logger.error("could not fetch results for frame number :: %s "
                         "and its exception : %s", str(frame_number), str(error))
            # sys.exit()
        return self.clean_output(json.loads(repr(response.data)))

    # pylint: disable=R0913
    def combine_results(
            self, video_duration, input_frame_rate, output_frame_rate, hgt, wdt):
        """
        :return: combine all results from results directory
        """
        logger.info("combining all results from %s", str(self.results_directory))
        od_responses = []

        for jsonfile in sorted(glob(str(self.results_directory / "*.json"))):
            with open(jsonfile, "r", encoding="utf-8") as filereader:
                data = json.load(filereader)
                od_responses.append(data['od_frame_res'])

        results = {"responses": od_responses, "video-info": {}}
        results["video-info"]["duration_in_seconds"] = video_duration
        results["video-info"]["in_fps"] = input_frame_rate
        results["video-info"]["height"] = hgt
        results["video-info"]["width"] = wdt
        results["video-info"]["out_fps"] = output_frame_rate

        return results

    def remove_temp_results(self):
        """
        : remove temporary results directory
        """
        try:
            shutil.rmtree(str(self.results_directory))
        except OSError:
            logger.info("problem in deleting directory: %s", str(self.results_directory))

    def clean_output(self, res):
        """
        Recursively removes all None values from the input json and return the res
        """
        if isinstance(res, list):
            return [self.clean_output(x) for x in res if x is not None]
        elif isinstance(res, dict):
            return {
                key: self.clean_output(val)
                for key, val in res.items()
                if val is not None and val != []
            }
        else:
            return res

    def filter_ontology(self, ontology_list, valid_child_classes, output_names):
        """
        :param ontology_list: responses to be filtered
        :param valid_child_classes: set of valid classes
        """
        final_output = []
        valid_parent_classes = set()
        for ontology in ontology_list:
            if ontology['name'] in valid_child_classes and ontology['name'] not in output_names:
                final_output.append(ontology)
                output_names.add(ontology['name'])
                valid_parent_classes.update(ontology.get('parent_names', []))
        # Recursively call this method on valid_parent_classes
        if valid_parent_classes:
            final_output.extend(self.filter_ontology(ontology_list, valid_parent_classes, output_names))
        return final_output

    def filter_by_threshold(self, responses, threshold):
        """
        :param responses: responses to be filtered
        :param threshold: confidence threshold
        """
        filter_responses = []
        for idx, response in enumerate(responses):
            # Cleaning Objects
            image_objects = response['od_response'].get('image_objects', [])
            image_objects = [img_obj for img_obj in image_objects if img_obj.get("confidence") >= threshold]
            response['od_response']['image_objects'] = image_objects

            # Cleaning Ontology
            valid_child_ontology_classes = {img_obj['name'] for img_obj in image_objects}
            output_names = set()
            filtered_ontologies = self.filter_ontology(response['od_response'].get('ontology_classes', []), 
                                                        valid_child_ontology_classes, output_names)
            response['od_response']['ontology_classes'] = filtered_ontologies

            filter_responses.append(response)

        return filter_responses
                 

if __name__ == '__main__':

    # pylint: disable=R1732
    parser = argparse.ArgumentParser()
    parser.add_argument('--video-file', type=str, required=True, help='video input file path')
    parser.add_argument("--model-id", type=str, help='custom trained model id for inference', default=None)
    parser.add_argument("--output-frame-rate", type=int, help="output frames per second", default=1)
    parser.add_argument(
        "--confidence-threshold", type=float,
        help="remove prediction lower than confidence-threshold, 0 to 1", default=0.3
    )

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
            'analyze_video_demo.log', mode='w')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    video_filename = args.video_file
    model_id = args.model_id
    out_frame_rate = args.output_frame_rate
    conf_thres = args.confidence_threshold

    try:
        config = oci.config.from_file(
            '~/.oci/config', profile_name="DEFAULT")
    except oci.exceptions.ConfigFileNotFound as err:
        logger.error(err)
        sys.exit()

    service_endpoint = \
        f"https://vision.aiservice.{config.get('region')}.oci.oraclecloud.com"

    analyze_video = AnalyzeVideo(
        video_file=video_filename, input_frame_rate=out_frame_rate,
        custom_model_id=model_id, oci_config=config,
        service_endpoint=service_endpoint
    )

    total_video_duration, in_frame_rate, height, width = analyze_video.run()
    responses = analyze_video.combine_results(
        total_video_duration, in_frame_rate, out_frame_rate, height, width)

    responses["responses"] = analyze_video.filter_by_threshold(responses["responses"], conf_thres)

    analyze_video.remove_temp_results()
    json_name_ = os.path.basename(video_filename).split(".")[0] + "_fps" + "_" + str(out_frame_rate)
    with open(os.path.join(json_name_ + "_responses.json"), "w", encoding="utf-8") as f:
        json.dump(
            responses, f
        )
        