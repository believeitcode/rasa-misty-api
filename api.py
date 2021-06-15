import pathlib
import uuid
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests as rq
from fastapi.middleware.cors import CORSMiddleware

import json

app = FastAPI()

with open("config.json") as json_file:
    config = json.load(json_file)

# We want to be flexible in our localhost so we'll set
# very open CORS policies.
origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Text(BaseModel):
    text: str

 #This endpoint returns our HTML page for testing purpose
@app.get("/",response_class=HTMLResponse)
def index():
    html = pathlib.Path("index.html").read_text()
    return HTMLResponse(content=html, status_code=200)

@app.get("/1/",response_class=HTMLResponse)
def index():
    html = pathlib.Path("index1.html").read_text()
    return HTMLResponse(content=html, status_code=200)

# This endpoint will receive texts, proxy to Rasa and return parsed results.
# Note that we assume that Rasa is hosted at localhost:5005

# API usage : To get intent from from text 
@app.post("/intent/")
def post_intent(text: Text):
    body = {
      "text": text.text,
      "message_id": str(uuid.uuid4())
    }
    url = "http://"+config["NGROKIP"]+"/model/parse" # rasa run --enable-api --cors "*" --debug , #rasa run actions
    return (rq.post(url, json=body).json())

# API usage: To receive bot respond message
@app.post("/botrespond/")
def post_botrespond(request: Text):
    body = {
        "sender": "sender_01",
        "message": request.text
    }
    url = "http://"+config["NGROKIP"]+"/webhooks/rest/webhook" 
    
    return rq.post(url, json=body).json()[0]

#API usage: To Check for server status 
@app.get("/status/")
def get_attempt():
    return {"status": "alive"}