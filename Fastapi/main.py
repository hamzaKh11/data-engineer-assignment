# import libraries
from typing import List, Optional
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import uvicorn
from fastapi.responses import PlainTextResponse
import spacy
from textblob import TextBlob


# credentials to access to database in mongodb
uri = "MONGODB_Link"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Initialize MongoDB client and connect to the database
db = client['bbc_articles']
collection = db['articles']


app = FastAPI()


class Article(BaseModel):
    Menu: str
    Submenu: str
    Title: str
    Subtitle: str
    Authors: List[str]
    date_published: Optional[str]  # Make date_published field optional
    Text: str
    Images: List[str]
    Video: List[str]
    Topics: List[str]


@app.get("/")
def root():
    return {"Welcome to our api"}


@app.get("/sw.js", response_class=PlainTextResponse)
async def service_worker():
    return "console.log('Service worker script placeholder')"


@app.get("/articles", response_model=List[Article])
async def get_articles():
    articles = collection.find({})
    return articles


@app.get("/articles/topics")
async def get_topic_distribution():
    data = list(collection.find({}))
    df = pd.DataFrame(data)
    topic_counts = df['Topics'].explode().value_counts().to_dict()
    return topic_counts


@app.get("/articles/submenu")
async def get_topic_distribution():
    data = list(collection.find({}))
    df = pd.DataFrame(data)
    submenu_counts = df['Submenu'].explode().value_counts().to_dict()
    return submenu_counts

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
