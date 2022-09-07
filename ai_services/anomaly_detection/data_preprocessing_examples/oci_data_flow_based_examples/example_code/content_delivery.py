from abc import abstractmethod
from pyspark.sql import functions as F

from example_code.dataflow_utils import DataflowSession, get_spark_context


class ContentDeliveryFactory:
    """
    ContentDeliveryFactory returns database specific ContentDeliveryHelper.
    """

    def __init__(self, dataflow_session: DataflowSession):
        self.dataflow_session = dataflow_session

    @staticmethod
    def get(source, dataflow_session: DataflowSession):
        source = ''.join(source.split('-')).lower()  # Remove any minus from string and convert to lower-case
        if source == ObjectStorageHelper.SOURCE.lower():
            return ObjectStorageHelper(dataflow_session)
        if source == AutonomousDatabaseHelper.SOURCE.lower():
            return AutonomousDatabaseHelper(dataflow_session)
        raise NotImplementedError(f"{source} is not supported!")


class ContentDeliveryHelper:
    """
    ContentDeliveryHelper is a base helper that contains abstract methods for getting and putting dataframes.
    """

    def __init__(self, dataflow_session: DataflowSession):
        print("Initialized base content-delivery helper")
        self.dataflow_session = dataflow_session

    @abstractmethod
    def get_df(self, content_details: dict, content_validation: dict = None):
        pass


class ObjectStorageHelper(ContentDeliveryHelper):
    """
    ObjectStorageHelper is an Object-Storage specific helper that contains methods for getting and putting dataframes.
    """
    SOURCE = "ObjectStorage"

    def __init__(self, dataflow_session: DataflowSession):
        super().__init__(dataflow_session)
        print("Initialized content-delivery ObjectStorageHelper class")

    @staticmethod
    def get_content_url(content_details: dict):
        return f"oci://{content_details['bucket']}@{content_details['namespace']}/{content_details['objectName']}"

    def get_df(self, content_details: dict, content_validation: dict = None):
        if 'eventType' in content_details:
            print("Loading dataframe triggered by events!")
            try:
                assert content_validation['isEventDriven'], \
                    "Attempting to get input-source from event without enabling event in driver config!"
                assert content_details['data']['additionalDetails']['namespace'] == content_validation['namespace'], \
                    f"Triggered event has namespace other than the expected one."
                assert content_details['data']['additionalDetails']['bucket'] == content_validation['bucket'], \
                    f"Triggered event has bucket other than the expected one."

                object_prefix = content_validation['objectName'].split('*')[0]
                assert content_details['data']['resourceName'].startswith(object_prefix), \
                    f"Triggered event has objectName not matching the regex."

                content_details = {
                    'namespace': content_details['data']['additionalDetails']['namespace'],
                    'bucket': content_details['data']['additionalDetails']['bucket'],
                    'objectName': content_details['data']['resourceName'],
                }
            except Exception as e:
                print(f"Unable to load object from event information: {e}")
                raise e

        options = {'header': 'True'}
        spark_context = get_spark_context(dataflow_session=self.dataflow_session)
        content_url = self.get_content_url(content_details)

        if content_details['objectName'].endswith(".csv"):
            df = spark_context.read.options(**options).csv(content_url)
        elif content_details['objectName'].endswith(".parquet"):
            df = spark_context.read.options(**options).parquet(content_url)
        else:
            raise Exception(f"Attempting to load {content_details['objectName']}. "
                            f"Only csv and parquet files can be read from {self.SOURCE} at this time!")
        return df.select([F.col(x).alias(x.lower()) for x in df.columns])


class AutonomousDatabaseHelper(ContentDeliveryHelper):
    """
    AutonomousDatabaseHelper is an ATP/ADW specific helper that contains methods for getting and putting dataframes.
    """
    SOURCE = "Oracle"
    ALLOWED_CONTENT_DETAILS_KEYS = {"adbId", "dbtable", "connectionId", "user", "password"}

    def __init__(self, dataflow_session: DataflowSession):
        super().__init__(dataflow_session)
        print("Initialized content-delivery AutonomousDatabaseHelper class")

    def get_df(self, content_details: dict, content_validation: dict = None):
        assert 'eventType' not in content_details and content_validation is None, \
            "Events/table-patterns is not yet supported for Oracle Autonomous Database!"

        options = {key: content_details[key] for key in self.ALLOWED_CONTENT_DETAILS_KEYS}
        spark_context = get_spark_context(dataflow_session=self.dataflow_session)
        df = spark_context.read.format("oracle").options(**options).load()
        return df.select([F.col(x).alias(x.lower()) for x in df.columns])
