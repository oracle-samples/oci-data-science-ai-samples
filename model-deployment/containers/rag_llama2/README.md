# Overview
This repo provides the setup of RAG using Llama2 and Qdrant vector DB.
# Pre Requisites
## Object Storage Bucket 

Object storage bucket is required to save the documents which are provided at time of ingestion in vector DB. [Refer](github.com/oracle-samples/oci-data-science-ai-samples/tree/main/distributed_training#2-object-storage)

## Access to Hugging Face Llama2 

Access token from HuggingFace to download Llama2 model. To fine-tune the model, you will first need to access the pre-trained model. The pre-trained model can be obtained from Meta or HuggingFace. In this example, we will use the HuggingFace access token to download the pre-trained model from HuggingFace (by setting the HUGGING_FACE_HUB_TOKEN environment variable). [Refer](https://github.com/oracle-samples/oci-data-science-ai-samples/tree/main/model-deployment/containers/llama2)

## OCI Logging
When experimenting with new frameworks and models, it is highly advisable to attach log groups to model deployment in order to enable self assistance in debugging. Follow below steps to create log groups.

* Create logging for the model deployment (if you have to already created, you can skip this step)
    * Go to the [OCI Logging Service](https://cloud.oracle.com/logging/log-groups) and select `Log Groups`
    * Either select one of the existing Log Groups or create a new one
    * In the log group create ***two*** `Log`, one predict log and one access log, like:
        * Click on the `Create custom log`
        * Specify a name (predict|access) and select the log group you want to use
        * Under `Create agent configuration` select `Add configuration later`
        * Then click `Create agent configuration`

## Required IAM Policies

Public [documentation](https://docs.oracle.com/en-us/iaas/data-science/using/policies.htm).

### Generic Model Deployment policies
`allow group <group-name> to manage data-science-model-deployments in compartment <compartment-name>`

`allow dynamic-group <dynamic-group-name> to manage  data-science-model-deployments in compartment <compartment-name>`

### Allows a model deployment to emit logs to the Logging service. You need this policy if you’re using Logging in a model deployment
`allow any-user to use log-content in tenancy where ALL {request.principal.type = 'datasciencemodeldeployment'}`

### Bring your own container [policies](https://docs.oracle.com/en-us/iaas/data-science/using/model-dep-policies-auth.htm#model_dep_policies_auth__access-logging-service#model_dep_policies_auth__access-custom-container)
`ALL { resource.type = 'datasciencemodeldeployment' }`

`allow dynamic-group <dynamic-group-name> to read repos in compartment <compartment-name> where ANY {request.operation='ReadDockerRepositoryMetadata',request.operation='ReadDockerRepositoryManifest',request.operation='PullDockerLayer' }`

#### If the repository is in the root compartment, allow read for the tenancy

`allow dynamic-group <dynamic-group-name> to read repos in tenancy where ANY {
request.operation='ReadDockerRepositoryMetadata',
request.operation='ReadDockerRepositoryManifest',
request.operation='PullDockerLayer'
}`

#### For user level policies

`allow any-user to read repos in tenancy where ALL { request.principal.type = 'datasciencemodeldeployment' }`

`allow any-user to read repos in compartment <compartment-name> where ALL { request.principal.type = 'datasciencemodeldeployment'}`

### Model Store [export API](https://docs.oracle.com/en-us/iaas/data-science/using/large-model-artifact-export.htm#large-model-artifact-export) for creating model artifacts greater than 6 GB in size

`allow service datascience to manage object-family in compartment <compartment> where ALL {target.bucket.name='<bucket_name>'}`

`allow service objectstorage-<region> to manage object-family in compartment <compartment> where ALL {target.bucket.name='<bucket_name>'}`

### Policy to check Data Science work requests
`allow group <group_name> to manage data-science-work-requests in compartment <compartment_name>`

For all other Data Science policies, please refer these [details](https://github.com/oracle-samples/oci-data-science-ai-samples/blob/main/distributed_training/README.md#3-oci-policies).

## Notebook session 

[Notebook session](docs.oracle.com/en-us/iaas/data-science/using/manage-notebook-sessions.htm) - used to initiate the distributed training and to access the fine-tuned mode

## Compute Instance as basic server

* Setting up Compute Instance. [Refer](https://docs.oracle.com/iaas/Content/Compute/Tasks/launchinginstance.htm)
* Create a compute instance with public subnet with internet gateway. [Refer](https://docs.oracle.com/en/solutions/wls-on-prem-to-oci/use-wizard-create-vcn.html)
* Create a dynamic group and add the compute instance ocid to it. [Refer](https://docs.oracle.com/en-us/iaas/Content/Identity/dynamicgroups/To_create_a_dynamic_group.htm)

Provide the following in policies for the dynamic group

`allow group data-science-model-deployments to manage data_science_projects in compartment <datascience_hol>`


# Deploying the Llama2 Model

Please refer the following [Github Link](https://github.com/oracle-samples/oci-data-science-ai-samples/tree/main/model-deployment/containers/llama2) to download and deploy the Llama2 model.

# Setting Qdrant

Qdrant integrates smoothly with LangChain, and you can actually use Qdrant within LangChain via the VectorDBQA class. The initial step is to compile all the documents that will act as the foundational knowledge for our LLM. Imagine we place these in a list titled docs. Each item in this docs list is a string containing segments of paragraphs. Please download the required python libraries as defined in "ingestion MD" directories requirements.txt file.

## Qdrant Initialisation

Subsequently, the task is to produce embeddings from these documents. To illustrate, we will utilize a compact model from the sentence-transformers package:
```python 
from langchain.vectorstores import Qdrant
from langchain.embeddings import LlamaCppEmbeddings
import qdrant_client

#Load the embeddings model
embedding = LlamaCppEmbeddings(model_path=model_folder_directory,n_gpu_layers=1000)

# Get your Qdrant URL and API Key
url = <QDRANT-URL-HERE>
api_key = <QDRANT-API-KEY-HERE>

# Setting up Qdrant
client = qdrant_client.QdrantClient(
    url,
    api_key=api_key
)

qdrant = Qdrant(
    client=client, collection_name="my_documents",
    embeddings=embeddings
)
```

## Qdrant Upload to Vector DB

```python
# If adding for the first time, this method recreate the collection
qdrant = Qdrant.from_texts(
    texts, # texts is a list of documents to convert in embeddings and store to vector DB
    embedding,
    url=url,
    api_key=api_key,
    collection_name="my_documents"
)

# Adding following texts to the vector DB by calling the same object
qdrant.add_texts(texts) # texts is a list of documents to convert in embeddings and store to vector DB 
```

## Qdrant retrieval from vector DB

Qdrant provides retrieval options in similarity search methods such as batch search, range search, geospatial search, distance metrics etc. Here we would leverage similarity search based on the prompt question. 

```python
qdrant = Qdrant(
    client=client, collection_name="my_documents",
    embeddings=embeddings
)

# Similarity search
docs = qdrant.similarity_search(prompt)
```


# RAG Basic setup 

We use the prompt template and QA chain provided by Langchain to make the chatbot, this helps in passing the context and question directly to the Llama2 based model

```python
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts.prompt import PromptTemplate

template = """You are an assistant to the user, you are given some context below, please answer the query of the user with as detail as possible

Context:\"""
{context}
\"""

Question:\"
{question}
\"""

Answer:"""


chain = load_qa_chain(llm, chain_type="stuff", prompt=qa_prompt)

## Retrieve docs from Qdrant Vector DB based upon user prompt
docs = qdrant.similarity_search(user_prompt)

answer = chain({"input_documents": docs, "question": question,"context": docs}, return_only_outputs=True)['output_text']
```

# Hosting streamlit application 

Go to the streamlit folder in the directory and install the requirements.txt using pip3 and user the app.py as the template of streamlit application. 

The below code define the authentication mechanism after you have setup the dynamic group with the compute instance and have added the required policies as mentioned in the Pre-requisites section. 

```python
from oci.auth import signers
import requests

config = {"region": <YOUR_REGION>}
signer = signers.InstancePrincipalsSecurityTokenSigner()

endpoint = <MD_ENDPOINT>
prompt = <USER_PROMPT>

headers = {"content-type": "application/text"}

response = requests.post(endpoint, data=prompt, auth=signer, headers=headers, timeout=200)
```

Use below command to run the application on the server:
```bash
streamlit run app.py
```

