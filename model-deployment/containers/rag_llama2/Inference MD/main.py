"""The main model serving HTTP server. Creates the following endpoints:

  /predict (POST) - model prediction endpoint
"""
from fastapi import FastAPI, Body, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
import logging
from langchain.embeddings import LlamaCppEmbeddings
from langchain.vectorstores import Qdrant


fast_app = FastAPI()
model_path = "<MODEL_PATH>"

def load_model(model_folder_directory):
    embedding = LlamaCppEmbeddings(model_path=model_folder_directory)
    return embedding

try:
    logging.info("Loading the model")
    embedding = load_model(model_path)
except Exception as e:
    print("Error: %s", e)

url = "<QDRANT_URL>"
api_key= "<API_KEY>"


qdrant = None
text_count = 0

@fast_app.get("/", response_class=HTMLResponse)
def read_root():
    return """
        <h2>Hello! Welcome to the model serving api.</h2>
        Check the <a href="/docs">api specs</a>.
    """

@fast_app.post("/predict")
def model_predict(request: Request, response: Response, data=Body(None)):
    global embedding, qdrant, text_count, url, api_key
    text = data.decode("utf-8")
    try:
        if qdrant is None:
            qdrant = Qdrant.from_texts(
                text,
                embedding,
                url=url,
                api_key=api_key,
                collection_name="my_documents"
            )
        else:
            qdrant.add_texts(text)
        text_count += 1
        result = "Sentence Added: Total sentences count is " + str(text_count)
    except Exception as e:
        result = "Error " + str(e)
    return result

'''
Health GET endpoint returning the health status
'''
@fast_app.get("/health")
def model_predict1(request: Request, response: Response):
    return {"status":"success"}

if __name__ == "__main__":
    uvicorn.run("main:fast_app", port=8080,reload=True)
