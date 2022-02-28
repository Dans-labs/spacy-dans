FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
RUN apt update
RUN apt-get -y install curl gnupg
RUN curl -sL https://deb.nodesource.com/setup_14.x  | bash -
RUN apt-get -y install poppler-utils nodejs wget bash vim git nodejs jq
RUN pip install spacy
RUN python -m spacy download nl_core_news_sm
RUN python -m spacy download en_core_web_sm
RUN python -m spacy download ru_core_news_sm
RUN python -m spacy download de_core_news_sm
RUN python -m spacy download es_core_news_sm
RUN python -m spacy download fr_core_news_sm
RUN python -m spacy download nb_core_news_sm
RUN python -m spacy download it_core_news_sm
RUN python -m spacy download pl_core_news_sm
RUN python -m spacy download pt_core_news_sm
RUN pip install nltk
RUN pip install textacy

RUN npm install -g wikidata-taxonomy
RUN npm install -g wikibase-cli
COPY ./conf /app/conf
COPY ./static/ /app/static
#COPY ./templates /app/templates
COPY spacy-dans /app
COPY spacy-dans/app.py /app/main.py
RUN pip install -r /app/requirements.txt
COPY spacy-dans/simple_json.py /usr/local/lib/python3.7/site-packages/readabilipy/simple_json.py
