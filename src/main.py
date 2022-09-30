#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Developed by Slava Tykhonov and Eko Indarto
# Data Archiving and Networked Services (DANS-KNAW), Netherlands
import importlib
from typing import Optional

import urllib3
import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
# from src.model import Vocabularies, WriteXML
from fastapi.openapi.utils import get_openapi
from fastapi.templating import Jinja2Templates
from parsr_client import ParsrClient
from pyDataverse.api import NativeApi
from pydantic import BaseModel
from starlette.staticfiles import StaticFiles

from Annotation import dataverse_metadata, save_annotation
from SpacyDans import *
from src.common import tags_metadata

from utils import make_request
# import codecs

parsr = ParsrClient('localhost:3001')

__version__ = importlib.metadata.metadata("spacy-dans")["version"]


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Spacy DANS",
        description="Annotation service dedicated for Machine Learning and Linked Open Data tasks.",
        version="0.1",
        routes=app.routes,
    )

    openapi_schema['tags'] = tags_metadata

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = FastAPI(
    openapi_tags=tags_metadata
)

class Item(BaseModel):
    name: str
    content: Optional[str] = None

templates = Jinja2Templates(directory='templates/')
app.mount('/static', StaticFiles(directory='static'), name='static')

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex='https?://.*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.openapi = custom_openapi
configfile = '/app/conf/gateway.xml'
if 'config' in os.environ:
    configfile = os.environ['config']
http = urllib3.PoolManager()

@app.get('/version')
def version():
    return '0.1'

@app.get("/dataverse")
async def dataverse(baseurl: str, doi: str, token: Optional[str] = None):
    params = []
    if token:
        api = NativeApi(baseurl, token)
        metadata = api.get_dataset(doi, auth=True)
        response_json = metadata.json()["data"]["latestVersion"]["metadataBlocks"]["citation"]
    else:
        url = "%s/api/datasets/export?exporter=dataverse_json&persistentId=%s" % (baseurl, doi)
        response_json = make_request(url)

    # response = requests.get('https://dataverse.nl/api/access/dataset/:persistentId/?persistentId=doi:10.34894/FO2VHB')

    if response_json:
        response_citation = response_json['datasetVersion']['metadataBlocks']['citation']
        metadata = dataverse_metadata(response_citation)
        metadata['plain_text'] = metadata['content']['text']
        data = ngrams_tokens(False, metadata, params)
        if 'original_entities' in data:
            for item in data['original_entities']:
                item['type'] = 'ML'
                metadata['original_entities'].append(item)
            if metadata:
                return save_annotation(metadata)

        response_files = response_json['datasetVersion']['files']
        if response_files:
            # Download files
            for dv_files in response_files:
                ct = dv_files["dataFile"]["contentType"]
                print(ct)

        return 'Error: no entities found in metadata'
    else:
        return 'Error: no metadata found'


# curl -X POST -F "file=@/Users/akmi/git/CLARIAH/Parsr/samples/ekoi.pdf" http://localhost:9266/upload
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
    save_file(file.filename, contents)
    parsr.send_document(file_path="../../tmp/" + file.filename, config_path="conf/defaultConfig.json"
                        , document_name=file.filename, wait_till_finished=False, refresh_period=1, save_request_id=True)

    # if result_type == 'JSON':
    #     return parsr.get_json()
    # elif result_type == "MARKDOWN":
    #     return parsr.get_markdown()
    # elif result_type == "TEXT":
    #     return parsr.get_text()
    # else:
    #     return None
    x = parsr.get_text()
    print(x)
    return 200


def save_file(filename, data):
    with open("../../tmp/" + filename, 'wb') as f:
        f.write(data)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9266)
