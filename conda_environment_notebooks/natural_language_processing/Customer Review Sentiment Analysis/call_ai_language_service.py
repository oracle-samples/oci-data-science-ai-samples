"""===============================================================================================
Call AI-Language for Sentiment Analysis
file: call_ai_language_service.py

This class uses the batching capability of OCI Language to efficiently get entities sentiment for all the records.
While it is a bit more complicated than calling the single record API,
it is much more efficient than sending one record at a time, and the operation completes much faster.

The following steps take place in that method.
1) It computes the maximum number of records for each batch, and generates a list of batches
2) It sends the batches to be scored to OCI Language
3) For each record, it writes the information back in the dataframe, in the respecting columns.
==================================================================================================
"""

import oci
from tqdm.notebook import tqdm
from dataenforce import Dataset
from typing import List, Union


class CallAILanguage:
    def __init__(self,
                 df: Union[Dataset["idx", "text", "Aspect_Level", "Sentence_Level", "Document_Level", ...], None],
                 compartment_id: str,
                 ai_client: object,
                 idx: str,
                 text: str,
                 max_batch_chars: int = 20000,
                 max_batch_records: int = 100):
        """Call AI-Language Service in Batch

    This class calls AI-Language Service in appropriate batch size to fill the sentiment for each record detail.
    It takes in a dataframe in which there is a `text` column, and returns a list of batches of texts,
    such that each batch contains at most `max_batch_chars` characters and at most `max_batch_record` records.

        Initialize the class with required parameters
        :param df: Input dataframe consists of two main columns of 'ID' and 'text'.
                The title of these columns are also input arguments as follows.
        :param compartment_id: The ID of the OCI cloud compartment in which AI-Language is set up.
        :param ai_client: An instance of OCI AI-Language service client with user config.
                Default values: ai_client = oci.ai_language.AIServiceLanguageClient(oci.config.from_file())
        :param idx: Placeholder for title of the column representing ID in the df; Chosen by the user.
        :param text: Placeholder for title of the column representing 'text' in the df; Chosen by the user.
        :param max_batch_chars: As a system limitations, the maximum total of characters to process in a batch request.
                Currently, it is up to 20,000 characters.
        :param max_batch_records: As a system limitations, the maximum number of records in a batch.
                Currently, it is up to 100 records.
        """
        self.df = df
        self.compartment_id = compartment_id
        self.ai_client = ai_client
        self.idx = idx
        self.text = text
        self.max_batch_chars = max_batch_chars
        self.max_batch_records = max_batch_records

    def group_records_into_batches(self) -> Union[List[str], None]:
        """This function groups the records into batches that take into consideration batch API limitations

        :return: batches: a list of batches where each batch contains at most `max_batch_chars` characters
                 and at most `max_batch_record` records.
        """
        # List of separate records to detect sentiment for
        documents = []

        # Group the data into batches that take into consideration batch API limitations
        batches = []
        batch_chars_counter = 0

        # Raise an error message when the module (to be used in the next lines) is not in service.
        model = "TextDocument"
        if not hasattr(oci.ai_language.models, model):
            raise ValueError(f" OCI AI-Language '{model}' is not responding. "
                             f"Please contact customer support or try later.")

        for id_ in range(self.df[self.idx].size):
            record = oci.ai_language.models.TextDocument(text=self.df[self.text][id_], key=str(id_), language_code="en")
            record_chars = len(record.text) if record.text is not None else 0

            if len(documents) >= self.max_batch_records or (batch_chars_counter + record_chars) > self.max_batch_chars:
                # time to create a new batch
                batches.append(documents)
                documents = []
                batch_chars_counter = 0
            # write the record to the batch
            documents.append(record)
            batch_chars_counter += record_chars

        # flush the last batch
        if len(documents) > 0:
            batches.append(documents)

        return batches

    def get_sentiment(self) -> None:
        """Call AI-Language Service to Retrieve Sentiments

        This method calls AI-Language Service in appropriate batch size to fill the sentiment for each record detail.
        :return: None. The sentiment output is written back into the input dataframe within the body of the function.
        """
        batches = self.group_records_into_batches()

        # Get sentiment for records in each of the batches
        aspect_list = []

        # Raise an error message when the module (to be used in the next lines) is not in service.
        model = "BatchDetectLanguageSentimentsDetails"
        if not hasattr(oci.ai_language.models, model):
            raise ValueError(f" OCI AI-Language '{model}' is not responding. "
                             f"Please contact customer support or try later.")

        for i in tqdm(range(len(batches))):
            aspect_sentiments_details = oci.ai_language.models. \
                BatchDetectLanguageSentimentsDetails(documents=batches[i], compartment_id=self.compartment_id)
            output = self.ai_client.batch_detect_language_sentiments(aspect_sentiments_details,
                                                                     level=["ASPECT", "SENTENCE"])
            aspect_list += output.data.documents
            print(str(len(aspect_list)) + " records processed so far.")

        # now write the results back to the dataframe
        for i in range(len(aspect_list)):
            # Aspect_Level:
            self.df.iat[int(aspect_list[i].key), self.df.columns.get_loc("Aspect_Level")] = aspect_list[i].aspects

            # Sentence_Level:
            self.df.iat[int(aspect_list[i].key), self.df.columns.get_loc("Sentence_Level")] = aspect_list[i].sentences

            # Document_Level:
            # Create a dictionary to store the results at Document_Level.
            # Unlike Aspect_Level and Sentence_Level, AI-Language service does not have a built-in syntax in the API
            # for generating outputs in a pack at Document_Level.
            self.df.iat[int(aspect_list[i].key), self.df.columns.get_loc("Document_Level")] = \
                [{
                    "scores": aspect_list[i].document_scores,
                    "sentiment": aspect_list[i].document_sentiment
                }]

        return
