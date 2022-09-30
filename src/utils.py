import traceback
from parsr_client import ParsrClient
import time
import requests
from fastapi import HTTPException
from requests.adapters import HTTPAdapter
from urllib3 import Retry


def make_request(url):
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    response = session.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail=f'Not found "{url}"')
    try:
        parsed = response.json()
        return parsed
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f'Error on response.json() for "{url}"')


def process_file(fpath, doc_name, rev):
    parsr = ParsrClient('localhost:3001')
    try:
        parsr.send_document(file_path=fpath,
                            config_path='/src/conf/defaultConfig.json',
                            document_name=doc_name, revision=rev, refresh_period=1,
                            save_request_id=True)
        a = parsr.get_request_id(document_name=doc_name, revision=rev)

        print('>>>>>>>a: ', a)

        check_status = True
        while check_status:
            if parsr is not None:
                c = parsr.get_status(request_id=a, server='localhost:3001')
                j = c['server_response']
                print(j)
                if "status" in j:
                    print("ok")
                    time.sleep(1)
                else:
                    check_status = False
                    print("---------")
            else:
                print("******")
        #
        x = parsr.get_text()
        print(x)
        f = parsr.get_status(request_id=a, server='localhost:3001')
    except Exception as e:
        print("error")
        print(e)


def process_csv(fpath):
    #todo: process here csv or tsv file
    pass