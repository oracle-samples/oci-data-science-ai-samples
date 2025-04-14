import json
import oci
import requests

from langchain_community.llms import OCIModelDeploymentVLLM
import ads
from oracle_vector_db import oracle_query, oracle_query
from ads.model.generic_model import GenericModel
import ads
from oracle_vector_db import oracle_query, oracle_query
from langchain.chains import RetrievalQA
from typing import List
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from oracle_vector_db import oracle_query, oracle_query
from config import COMMAND_MD_ENDPOINT, EMBEDDING_MD_ENDPOINT, RERANKER_MD_ENDPOINT, TOP_K
from pprint import pprint

nl2sql_prompt_template = """ Given an input Question, create a syntactically correct Oracle SQL query to run. 
Pay attention to using only the column names that you can see in the schema description.
Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
Please double check that the SQL query you generate is valid for Oracle Database.
DO NOT use alias in the SELECT clauses.
Only use the tables listed below.

create table Partner(ID NUMBER NOT NULL,
NAME VARCHAR2(100) NOT NULL,
Region VARCHAR2(100) NOT NULL,
Category VARCHAR2(100) NOT NULL,
Partner_since DATE NOT NULL,
Last_renewal DATE NOT NULL,
Licensed  DATE NOT NULL,
Oracle_Products VARCHAR2(100) NOT NULL,
Nominated VARCHAR2(100) NOT NULL,
Nomination_date DATE NOT NULL,
Past_Awards_years_comma_seperated_list VARCHAR2(100) NOT NULL,
Customer_satisfaction_rating NUMBER NOT NULL,
Number_of_customers NUMBER NOT NULL,
Oracle_contact_email VARCHAR2(100) NOT NULL,
PRIMARY KEY (ID)
);
 
### Context:
{context}
 
### In-Context Examples:
Question: list or view partners who renewal last year
Oracle SQL: SELECT * FROM Partner WHERE   EXTRACT(YEAR FROM Last_renewal) = EXTRACT(YEAR FROM SYSDATE – INTERVAL ‘1’ YEAR)
             
Instructions:
- Do not use JOIN since the Schema only includes 1 table, unless striclt required.
- Do not use UNION since the Schema only includes 1 table.
- If all columns are required, give the (*) notation.
- Make sure to include all WHERE filtering conditions even there are more conditions than in-context examples.
- Use the best query description which matches the query.
- You should NEVER generate SQL queries with JOIN, since the Schema only includes 1 table.
- Use Context section to get additional details while bulding the query
- Do not return multiple queries in response. Just respond with single SQL query and nothing else
- Return only single query and append response between backtick character
- For date column use TO_DATE function in where clause. e.g. Nomination_date > TO_DATE('2001-01-01', 'YYYY-MM-DD');

Question: {question}
Oracle SQL: """

relational_data_summary_prompt_template = """In the context section, we provide a question and its corresponding answer. The answer contains a list of rows fetched from a database, where the first row is the column headers, and the subsequent rows are the data.
Your task is to summarize the answer in a single, human-understandable sentence. If there is data in the context section, assume it is correct and summarize it directly without evaluating its content.
Do not assume there is only one result unless specified.

### Context:
Question: {question}
Ans:
{context_data}

Can you please summarize the answer based on the data provided in the context? Your summary should be a single, concise sentence.

Summary:
"""

import json
import oci
import requests

from langchain_community.llms import OCIModelDeploymentVLLM
import ads
from oracle_vector_db import oracle_query, oracle_query
from ads.model.generic_model import GenericModel
import ads
from oracle_vector_db import oracle_query, oracle_query
from langchain.chains import RetrievalQA
from typing import List
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from oracle_vector_db import oracle_query, oracle_query
from config import COMMAND_MD_ENDPOINT, EMBEDDING_MD_ENDPOINT, RERANKER_MD_ENDPOINT, TOP_K
from pprint import pprint
from langchain import PromptTemplate
from config_private import DB_USER, DB_PWD, DB_HOST_IP, DB_SERVICE
import oracledb
import re

ads.set_auth("resource_principal")
command_md = OCIModelDeploymentVLLM(
    endpoint= COMMAND_MD_ENDPOINT,
    model="odsc-llm"
)
model_name = f"<replace-with-your-model-name>"


class CustomRetriever(BaseRetriever):
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        matching_documents = []
        
        #Embedding model 
        rps = oci.auth.signers.get_resource_principals_signer()
        print(f"###Query {query}")
        prediction = requests.post(EMBEDDING_MD_ENDPOINT, data=f'["{query}"]', auth=rps)

        #Search in DB
        q_result = oracle_query(prediction.json()['embeddings'][0], TOP_K, True, False)        
        text_list = []
        for n, id, sim in zip(q_result.nodes, q_result.ids, q_result.similarities):
            text_list.append(n.text)
        paired_list = [[query, text] for text in text_list]
        
        #print(f'Reranker payload: {paired_list}')        
        #ReRanker model
        reranker_results = requests.post(RERANKER_MD_ENDPOINT, data=json.dumps(paired_list), auth=rps)  # make a prediction request        
        max_value = max(reranker_results.json()['prediction'])
        print(f"###Reranker Result Max value: {max_value}")

        if max_value < -13:
            return matching_documents;
        # Find the index of the maximum value
        max_index = reranker_results.json()['prediction'].index(max_value)
        #print(f"The maximum value is: {max_value}")
        #print(f"The index of the maximum value is: {max_index}")
        doc =  Document(page_content=paired_list[max_index][1], metadata={"source": "local"})        
        #print(f"###Contextttt: {doc}")
        matching_documents.append(doc)
        return matching_documents


def load_model(model_file_name=model_name):
    if not model_file_name:
        raise ValueError('model_file_name cannot be None')

    # This is the default implementation of the load_model() specific to this score.py template only.
    if model_file_name == "<replace-with-your-model-name>":
        return "default_model"

def get_data_from_DB(query):
    DSN = f"{DB_HOST_IP}/{DB_SERVICE}"
    connection = oracledb.connect(user=DB_USER, password=DB_PWD, dsn=DSN, config_dir="/opt/oracle/config")
    # Creating a cursor object
    cursor = connection.cursor()

    # Executing the query
    cursor.execute(query)
    # Fetching the column names
    column_names = [desc[0] for desc in cursor.description]
    result = ','.join(column_names) + '\n'

    # Fetching and printing the results
    for row in cursor:
        row_values = [str(value).replace(',', ' ') for value in row]
        result += ','.join(row_values) + '\n'
    print(f"Query Result: {result}")
    # Closing the cursor and connection
    cursor.close()
    connection.close()
    return result;

def predict(data, model=load_model()):
    print(str)
    ads.set_auth("resource_principal")
    
    prompt_template = PromptTemplate(template=nl2sql_prompt_template, input_variables=['question'])
    customRetriever = CustomRetriever()
    chain = RetrievalQA.from_chain_type(
    llm=command_md,
    chain_type="stuff",
    chain_type_kwargs={"prompt": prompt_template},
    retriever=customRetriever
)
    chain.combine_documents_chain.llm_chain.llm.auth['signer'].refresh_security_token()

    res = chain(data)
    print(f"Output: {res['result']}")
    op= res['result']
    if 'Question' in op:
        query_str = op.split("Question:")[0]
    else:
        query_str = op

    match = re.search(r'`([^`]*)`', op)
    if match:
        query_str = match.group(1)
    else:
        query_str = match
        
    query = query_str.replace(';', '')
    result = get_data_from_DB(query)
    
    relational_data_summary_prompt = relational_data_summary_prompt_template.format(question=data, context_data=result)
    op=command_md.predict(relational_data_summary_prompt)
    print(f"Final Output: {op}")
    return {'prediction':op}
