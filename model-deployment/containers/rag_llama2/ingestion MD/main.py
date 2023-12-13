"""The main model serving HTTP server. Creates the following endpoints:

  /predict (POST) - model prediction endpoint
"""
from fastapi import FastAPI, Body, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
import logging
from langchain.embeddings import LlamaCppEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import LlamaCpp
from langchain.prompts.prompt import PromptTemplate
from langchain.vectorstores import Qdrant
import qdrant_client

fast_app = FastAPI()

model_path = "<MODEL_PATH>"

def load_model(model_folder_directory):
    embedding = LlamaCppEmbeddings(model_path=model_folder_directory,n_gpu_layers=15000)
    return embedding

try:
    logging.info("Loading the model")
    embeddings = load_model(model_path)
except Exception as e: 
    print("Error: %s", e)

url = "<QDRANT_URL>"
api_key= "<API_KEY>"

template = """You are an assistant to the user, you are given some context below, please answer the query of the user with as detail as possible

Context:\"""
{context}
\"""

Question:\"
{question}
\"""

Answer:"""



client = qdrant_client.QdrantClient(
    url,
    api_key=api_key
)

qdrant = Qdrant(
    client=client, collection_name="my_documents",
    embeddings=embeddings
)

qa_prompt = PromptTemplate.from_template(template)

llm = LlamaCpp(model_path=model_path,n_gpu_layers=15000, n_ctx=2048)

@fast_app.get("/", response_class=HTMLResponse)
def read_root():
    return """
        <h2>Hello! Welcome to the model serving api.</h2>
        Check the <a href="/docs">api specs</a>.
    """

@fast_app.post("/predict")
def model_predict(request: Request, response: Response, data=Body(None)):
    global llm, embeddings, qa_prompt, qdrant
    question = data.decode("utf-8")
    chain = load_qa_chain(llm, chain_type="stuff", prompt=qa_prompt)
    try:
        docs = qdrant.similarity_search(question)
    except Exception as e:
        return e
    answer = chain({"input_documents": docs, "question": question,"context": docs}, return_only_outputs=True)['output_text']
    return answer

'''
Health GET endpoint returning the health status
'''
@fast_app.get("/health")
def model_predict1(request: Request, response: Response):
    return {"status":"success"}

if __name__ == "__main__":
    uvicorn.run("main:fast_app", port=8080, reload=True)

