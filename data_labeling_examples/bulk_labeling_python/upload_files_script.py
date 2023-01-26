import oci
import os
from config import *
import mimetypes
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from concurrent.futures import wait
import logging


def init_object_storage_client():
    config=oci.config.from_file(CONFIG_FILE_PATH, CONFIG_PROFILE)
    object_storage_client = oci.object_storage.ObjectStorageClient(config=config, service_endpoint=SERVICE_ENDPOINT_OBJECT_STORAGE, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
    return object_storage_client

object_storage_client = init_object_storage_client()

def put_object(logger, file):
    """ The function is used to upload file to the object storage bucket

    :param file: Name of the file to be uploaded
    :return: Boolean
    """
    print(f'Uploading file : {file}')
    file_path = os.path.join(DATASET_DIRECTORY_PATH, file)
    mimetype, encoding = mimetypes.guess_type(file_path)
    if os.path.isfile(file_path):
            try:
                with open(file_path, "rb") as f:
                    file_bytes = f.read()
            except IOError as e:
                print(f'Could not read file : {file}')
                logger.error("Exception while reading %s, %s", file, e)
                return False
            logger.info("Uploading "+ str(file) + "to object storage")
            put_object_response = object_storage_client.put_object(
                namespace_name=OBJECT_STORAGE_NAMESPACE,
                bucket_name=OBJECT_STORAGE_BUCKET_NAME,
                content_type=mimetype,
                object_name=file,
                put_object_body=file_bytes)
            if put_object_response.status == 200:
                print(f'Successfully uploaded file : {file}')
                return True
            print(f'Failed to upload file : {file}')
            logger.info(f'Failed to upload {file}, Response header : {put_object_response.headers}')
            return False

def main():
    logging.basicConfig(filename="debug.log",
                        format='%(asctime)s %(message)s',
                        filemode='w')

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.info("...........starting to upload files to object storage.............")
    start = time.perf_counter()
    with ThreadPoolExecutor(NO_OF_PROCESSORS) as executor:
        futures = [executor.submit(put_object, logger, file) for file in os.listdir(DATASET_DIRECTORY_PATH)]
    wait(futures)
    success_count=0
    failure_count=0
    for future in as_completed(futures):
        if future.result():
            success_count+=1
        else:
            failure_count+=1
    end = time.perf_counter()
    print(f'Total files present in the given directory : {(success_count + failure_count)}\n'
          f'Successfully uploaded {success_count} file(s)\n'
          f'Failed to upload {failure_count} file(s)\n'
          f'Finished in {round(end - start, 2)} second(s)')

if __name__ == "__main__":
    main()