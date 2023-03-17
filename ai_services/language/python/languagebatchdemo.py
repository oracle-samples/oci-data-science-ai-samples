# This script reads a CSV file with reviews (inputfilename), and
# generates another CSV file (outputfilename)  that has aspect based level sentiment information.
# The generated document has a record per aspect, whereas the input document has a record per review.
# It is very likely that many aspects will be produced from a single review.
# the review_id column is contained in the generated file and can be used as a key to merge both files if needed.
#
#  This is a good example of batch processing using OCI Language.

import oci
import pandas as pd
import datetime

print(oci.__version__)

# Update these based on the file you want to analyze
# inputfilename = '1-hotel-reviews.csv'
# column_name_review_id = 'review_id'
# column_name_review = 'review'
# column_name_review_date = 'review_date'

inputfilename = '1-hotel-reviews.csv'
column_name_review_id = 'review_id'
column_type_review_id = "int"  # change to "string" if the id is a string
column_name_review = 'review'
column_name_review_date = 'review_date'


outputfilename = 'aspects.csv'


# Fills the Aspects column with an array of aspect level sentiment information for each row
def fill_aspect_sentiment(Data):
    documents = []

    # Group the data into batches that take into consideration batch API limitations
    batches = []
    counter = 0
    char_counter = 0
    max_batch_chars = 20000
    max_batch_record = 100

    for idx in range(Data[column_name_review].size):
        record = oci.ai_language.models.TextDocument(text=Data.iat[idx, Data.columns.get_loc(column_name_review)][0:1000],
                                                           key=str(Data.index[idx]),
                                                           language_code="en")
        record_chars = len(record.text)

        if len(documents) >= max_batch_record or (char_counter + record_chars) > max_batch_chars:
            # time to create a new batch
            batches.append(documents)
            documents = []
            char_counter = 0
            # write the record to the batch
        documents.append(record)
        char_counter = char_counter + record_chars
        counter = counter + 1

    # flush the last batch
    if len(documents) > 0:
        batches.append(documents)

    # get sentiment for each of the batches
    aspect_list = []

    for i in range(len(batches)):
        aspect_sentiments_details = oci.ai_language.models.BatchDetectLanguageSentimentsDetails(documents=batches[i])
        output = ai_client.batch_detect_language_sentiments(aspect_sentiments_details)
        aspect_list = aspect_list + output.data.documents
        print(str(len(aspect_list)) + " records processed so far.")

    # now write the aspects back to the data-frame
    for i in range(len(aspect_list)):
        if (column_type_review_id == "string"):
            Data.loc[str(aspect_list[i].key)]["Aspects"] = aspect_list[i].aspects
        else:
            Data.loc[int(aspect_list[i].key)]["Aspects"] = aspect_list[i].aspects
    return

## MAIN PROGRAM

ai_client = oci.ai_language.AIServiceLanguageClient(oci.config.from_file())

# Read a CSV file with several records
AllData = pd.read_csv(inputfilename)

# Select a subset of the columns, and set the index to the review id
Data = AllData[[column_name_review_id, column_name_review, column_name_review_date]].set_index(column_name_review_id)

# Add an aspects column where we will store the aspect for each review
Data["Aspects"] = ""

now = datetime.datetime.now()
print ("Started task : ")
print (now.strftime("%Y-%m-%d %H:%M:%S"))

fill_aspect_sentiment(Data)

now = datetime.datetime.now()
print ("Completed task : ")
print (now.strftime("%Y-%m-%d %H:%M:%S"))

# Expand the table to generate a table where each aspect has its own row.
no_of_records = len(Data)
aspects = []

for index, row in Data.iterrows():
    for i in row['Aspects']:
        temp_aspects = (index, i.text, i.sentiment, row[column_name_review_date])
        aspects.append(temp_aspects)


aspects_frame = pd.DataFrame(aspects,
                             columns=[column_name_review_id, 'Aspect', 'Sentiment', column_name_review_date])

# Write the results to a CSV
aspects_frame.to_csv(outputfilename, index=False)