import json
import oci
import requests

from langchain_community.llms import OCIModelDeploymentVLLM
import ads
from langchain.chains import RetrievalQA
from typing import List
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from oracle_vector_db import oracle_query
from config import COMMAND_MD_ENDPOINT, EMBEDDING_MD_ENDPOINT, RERANKER_MD_ENDPOINT, TOP_K
from pprint import pprint

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
        prediction = requests.post(EMBEDDING_MD_ENDPOINT, data=f'["{query}"]', auth=rps)

        #Search in DB
        q_result = oracle_query(prediction.json()['embeddings'][0], TOP_K, True, False)
        text_list = []
        for n, id, sim in zip(q_result.nodes, q_result.ids, q_result.similarities):
            text_list.append(n.text)
        paired_list = [[query, text] for text in text_list]
        
        print(f'Reranker payload: {paired_list}')
        
        #ReRanker model
        reranker_results = requests.post(RERANKER_MD_ENDPOINT, data=json.dumps(paired_list), auth=rps)  # make a prediction request        
        max_value = max(reranker_results.json()['prediction'])
        if max_value < -3:
            return matching_documents;
        # Find the index of the maximum value
        max_index = reranker_results.json()['prediction'].index(max_value)
        print(f"The maximum value is: {max_value}")
        print(f"The index of the maximum value is: {max_index}")
        doc =  Document(page_content=paired_list[max_index][1], metadata={"source": "local"})        
        matching_documents.append(doc)
        return matching_documents

customRetriever = CustomRetriever()
chain = RetrievalQA.from_chain_type(
    llm=command_md,
    retriever=customRetriever
)

def load_model(model_file_name=model_name):
    if not model_file_name:
        raise ValueError('model_file_name cannot be None')

    # This is the default implementation of the load_model() specific to this score.py template only.
    if model_file_name == "<replace-with-your-model-name>":
        return "default_model"


def predict(data, model=load_model()):
    print(str)
    ads.set_auth("resource_principal")
    
    pprint(vars(chain.combine_documents_chain.llm_chain.llm.auth['signer']))
    chain.combine_documents_chain.llm_chain.llm.auth['signer'].refresh_security_token()
    pprint(vars(chain.combine_documents_chain.llm_chain.llm.auth['signer']))
    res = chain(data)
    print("\n")
    print("\n")
    print(f"Output: {res['result']}")
    return {'prediction':res['result']}
