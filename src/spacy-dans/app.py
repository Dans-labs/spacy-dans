#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Developed by Slava Tykhonov and Eko Indarto
# Data Archiving and Networked Services (DANS-KNAW), Netherlands
import uvicorn
import pandas as pd
from DatesRecognition import DatesRecognition
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pyDataverse.api import Api, NativeApi
from pyDataverse.models import Datafile
from pyDataverse.models import Dataset
from pydantic import BaseModel
from typing import Optional
from starlette.responses import FileResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
#from src.model import Vocabularies, WriteXML
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from Annotation import dataverse_metadata, save_annotation, doccano_annotation
import xml.etree.ElementTree as ET
import requests
import re
import os
import json
import urllib3, io
import subprocess
from dateutil.parser import parse
import urllib
import subprocess
from SpacyDans import *
from bs4 import BeautifulSoup
from readabilipy import simple_json_from_html_string
#import codecs
import datefinder
from datetime import datetime

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="DANS Machine Learning API",
        description="Annotation service dedicated for Machine Learning and Linked Open Data tasks.",
        version="0.1",
        routes=app.routes,
    )

    openapi_schema['tags'] = tags_metadata

    app.openapi_schema = openapi_schema
    return app.openapi_schema

tags_metadata = [
    {
        "name": "country",
        "externalDocs": {
            "description": "Put this citation in working papers and published papers that use this dataset.",
            "authors": 'Slava Tykhonov',
            "url": "https://dans.knaw.nl/en",
        },
    },
    {
        "name": "namespace",
        "externalDocs": {
            "description": "API endpoint for Dataverse specific Machine Learning tasks.",
            "authors": 'Slava Tykhonov',
            "url": "https://dans.knaw.nl",
        },
    }
]

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
        response = metadata.json()["data"]["latestVersion"]["metadataBlocks"]["citation"]
    else:
        url = "%s/api/datasets/export?exporter=dataverse_json&persistentId=%s" % (baseurl, doi)
        resp = requests.get(url=url)
        response = resp.json()['datasetVersion']['metadataBlocks']['citation']

    if response:
        metadata = dataverse_metadata(response)
        metadata['plain_text'] = metadata['content']['text']
        data = ngrams_tokens(False, metadata, params)
        if 'original_entities' in data:
            for item in data['original_entities']:
                item['type'] = 'ML'
                metadata['original_entities'].append(item)
            if metadata:
                return save_annotation(metadata)
        return 'Error: no entities found in metadata'
    else:
        return 'Error: no metadata found'

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9266)
