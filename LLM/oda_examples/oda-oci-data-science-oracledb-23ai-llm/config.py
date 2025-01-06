"""
File name: config.py
Author: Luigi Saetta
Date created: 2023-12-15
Date last modified: 2024-03-16
Python Version: 3.11

Description:
    This module provides some configurations


Usage:
    Import this module into other scripts to use its functions. 
    Example:
    ...

License:
    This code is released under the MIT License.

Notes:
    This is a part of a set of demo showing how to use Oracle Vector DB,
    OCI GenAI service, Oracle GenAI Embeddings, to build a RAG solution,
    where all he data (text + embeddings) are stored in Oracle DB 23c 

Warnings:
    This module is in development, may change in future versions.
"""

# the book we're going to split and embed
INPUT_FILES = [
    "python-oracledb_Vector_support_LA2_v2.pdf",
    "oracle-partner-award-official-rules.pdf"
]

VERBOSE = False

# to enable splitting pages in chunks
# in token
# modified 05/02/2024
ENABLE_CHUNKING = True
# set to 1000
MAX_CHUNK_SIZE = 1600
CHUNK_OVERLAP = 100

# for retrieval
TOP_K = 2

# bits used to store embeddings
# possible values: 32 or 64
# must be aligned with the create_tables.sql used
EMBEDDINGS_BITS = 64

# ID generation: LLINDEX, HASH, BOOK_PAGE_NUM
# define the method to generate ID
ID_GEN_METHOD = "HASH"

# Tracing
ADD_PHX_TRACING = True
PHX_PORT = "7777"
PHX_HOST = "0.0.0.0"

#RAG Additional config
CONDA_PACK_PATH = "oci://<bucket>@<namespace>/rag-oracle23db-poc_v3/gpu/PyTorch 2.0 for GPU on Python 3.9/2.0/pytorch20_p39_gpu_v2"

LOG_GROUP_ID="ocid1.loggroup.oc1.<ocid>"

#Embedding model
EMBEDDING_MODEL_ACCESS_LOG_LOG_ID="ocid1.log.oc1.<ocid>"
EMBEDDING_MODEL_PREDICT_LOG_LOG_ID="ocid1.log.oc1.<ocid>"

#Reranker model
RERANKER_MODEL_ACCESS_LOG_LOG_ID="ocid1.log.oc1.<ocid>"
RERANKER_MODEL_PREDICT_LOG_LOG_ID="ocid1.log.oc1.<ocid>"

#Langchain Model
COMMAND_MD_ENDPOINT = 'https://modeldeployment.eu-frankfurt-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.<ocid>/predict'
EMBEDDING_MD_ENDPOINT = 'https://modeldeployment.eu-frankfurt-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.<ocid>/predict'
RERANKER_MD_ENDPOINT = 'https://modeldeployment.eu-frankfurt-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.<ocid>/predict'
LANGCHAIN_MODEL_ACCESS_LOG_LOG_ID="ocid1.log.oc1.<ocid>"
LANGCHAIN_MODEL_PREDICT_LOG_LOG_ID="ocid1.log.oc1.<ocid>"
