#FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7-2019-10-15
FROM tiangolo/uvicorn-gunicorn-fastapi
RUN apt-get update && apt-get install -y \
    bash \
    git \
    jq \
    nodejs \
    npm \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*
RUN npm install -g \ 
    wikidata-taxonomy \
    wikibase-cli
RUN pip install --no-cache-dir --upgrade \
    nltk \
    spacy \
    textacy
RUN python -m spacy download de_core_news_sm && \
    python -m spacy download en_core_web_sm && \
    python -m spacy download es_core_news_sm && \
    python -m spacy download fr_core_news_sm && \
    python -m spacy download it_core_news_sm && \
    python -m spacy download nb_core_news_sm && \
    python -m spacy download nl_core_news_sm && \
    python -m spacy download pl_core_news_sm && \
    python -m spacy download pt_core_news_sm && \
    python -m spacy download ru_core_news_sm

COPY ./conf /app/conf
COPY ./static/ /app/static
#COPY ./templates /app/templates
COPY ./app /app
COPY ./app/app.py /app/main.py
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY ./app/simple_json.py /usr/local/lib/python3.7/site-packages/readabilipy/simple_json.py
COPY ./__init__.py /usr/local/lib/python3.9/site-packages/doccano_api_client/__init__.py 
