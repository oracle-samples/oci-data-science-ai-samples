import pandas as pd
import os, io
import ads
from ads import set_auth
from ads.common.auth import default_signer

DATAFILE_FILENAME_PREFIX = "pipeline_data_"
DATAFILE_ENV_NAME = "DATA_LOCATION"
DATAFILE_FILENAME_EXT = ".csv"
PIPELINE_RUN_OCID_ENV_NAME = "PIPELINE_RUN_OCID"

class MLPipelineDataHelper:       
    """
    Helper functions for passing data between pipeline steps
    The functions use a temporary file on OCI object storage to set/get data between steps in the pipeline.
    The functions expect the presence of the environment variable DATA_LOCATION with the value of the OCI object storage location to be used. Here is an example of how this could looks like (don't forget the slash / at the end!):
    os.environ["DATA_LOCATION"] = "oci://{bucket_name}@{namespace}/"

    The functions use the PIPELINE_RUN_OCID environment variable in the temporary file name to make it unique to the pipeline.
    
    Dependencies:
    ocifs: pip install ocifs    
    """
    
    def set_pipeline_param(param_name, param_value):
        """
        Set a parameter. param_name is the key, and param_value is the value.
        for simple small data, like strings, numbers, and even small sets/dataframes/dictionaries, you can use the value as is (pass by value).
        For larger data srtuctures, write the data to a file and use the param_value as a reference for the file.
        """
        
        datafile_loc = os.environ[DATAFILE_ENV_NAME]
        ads.set_auth(auth="resource_principal")
        if (datafile_loc is not None):
            datafile_fullpath = datafile_loc + DATAFILE_FILENAME_PREFIX + os.environ[PIPELINE_RUN_OCID_ENV_NAME] + DATAFILE_FILENAME_EXT
            try:
                ref_data_dfrm = pd.read_csv(datafile_fullpath, header=None, storage_options=default_signer())
                ref_data_dict = dict(ref_data_dfrm.to_dict('split')['data'])
            except FileNotFoundError:
                print("pipeline data file not found. Creating " + datafile_fullpath)
                ref_data_dict = dict()

            ref_data_dict[param_name] = param_value
            output_df = pd.DataFrame.from_dict(ref_data_dict, orient='index')
            output_df.to_csv(datafile_fullpath, header=False, storage_options=default_signer())
            print("Added " + param_name + " = " + ref_data_dict[param_name])
            return

        print("Error: DATA_LOCATION environment variable is not defined")
        return

    def get_pipeline_param(param_name):
        """
        Retrieve a previously set parameter by its name.
        """
        
        datafile_loc = os.environ[DATAFILE_ENV_NAME]
        ads.set_auth(auth="resource_principal")
        if (datafile_loc is not None):
            datafile_fullpath = datafile_loc + DATAFILE_FILENAME_PREFIX + os.environ[PIPELINE_RUN_OCID_ENV_NAME] + DATAFILE_FILENAME_EXT
            try:
                ref_data_dfrm = pd.read_csv(datafile_fullpath, header=None, storage_options=default_signer())
                ref_data_dict = dict(ref_data_dfrm.to_dict('split')['data'])
                return ref_data_dict[param_name]
            except FileNotFoundError:
                print("pipeline data file not found")
                return None

        print("Error: DATA_LOCATION environment variable is not defined")
        return None

    def cleanup_pipeline_params():
        """
        Delete the temporary file from the object storage. Call this function before the end of your pipeline.
        """
        
        import ocifs
        fs = ocifs.OCIFileSystem()
        try:
            datafile_loc = os.environ[DATAFILE_ENV_NAME]
            if (datafile_loc is not None):
                datafile_fullpath = datafile_loc + DATAFILE_FILENAME_PREFIX + os.environ[PIPELINE_RUN_OCID_ENV_NAME] + DATAFILE_FILENAME_EXT
                fs.rm(datafile_fullpath)
                print("Cleanup completed")
        except:
            print("Nothing to cleanup")