# Spacy DANS
This is Spacy based Machine Learning pipeline for CLARIAH WP3 task on Dataverse metadata enrichment. It's being developed by DANS R&D group in the CLARIAH project.

# CLARIAH WP3 Challenges for FAIR CMDI metadata 

There are five challenges that we defined in this work. 
* First challenge: make a proposal of a core set of similar data as a recommendation for the CLARIN community is quite a challenging task. 
* Second challenge: the extraction and transformation of metadata fields into the Dataverse core set of metadata, in the collaboration with the Global Dataverse Community Consortium. For this task we're working on infrastructure components, such as external controlled vocabularies support, and also using Dataverse Semantic API. 
* Third challenge: building workflow to predict and link concepts from the external control vocabularies datasets metadata values. This task is about metadata enrichment with the help of Machine Learning and storing datasets back in the Dataverse data repository. It will allow to produce Linked Open Data out of FAIR datasets containing links to the appropriate ontologies and external controlled vocabularies. **Spacy DANS pipeline suppose to be a solution for this challenge**.
* Fourth Challenge: the extension of a common framework with the support of ANY controlled vocabularies. The task is to build a pipeline to predict which controlled vocabularies could be used for the specific metadata fields.
* Fifth Challenge is about getting back CMDI metadata from datasets stored in Dataverse. As soon as we have metadata in the standardized format like JSON or JSON-LD, we have to make a conversion to CMDI by applying some transformations and make metadata available for the CLARIN and CLARIAH communities.

# Annotations

This pipeline is based on [Doccano](https://github.com/doccano/doccano), an Open Source text annotation tool for humans. It provides annotation features for text classification, sequence labeling and sequence to sequence tasks and was extended with integration layer to train models based on Dataverse Metadata. 

You can install and run Doccano by running the commands below:
```
git clone https://github.com/doccano/doccano
cd doccano
docker-compose -f docker-compose.dev.yml up -d
```
The service should be available on port 3000, for example, http://0.0.0.0:3000

# Install and run Spacy DANS
To run the pipeline via Docker, you'll need a working installation of docker and docker-compose, and running instance of Doccano.
Copy the sample file to .env and change enviromental variables and credentials to make a connection to your Doccano service: 
```
cp .env_sample .env
```
Open .env file and fill DOCCANO_URL, DOCCANO_USER and DOCCANO_PASSWORD. Now build and run the infrastructure:
```
docker-compose up -d
```

# Academic publications and presentations
* Slava Tykhonov, Jerry de Vries, Andrea Scharnhorst, Eko Indarto, Mike Priddy, Femmy Admiraal. "Flexible metadata schemes for research data repositories. The Common Framework in Dataverse and the CMDI use case". CLARIN 2021 Annual Conference (2021). [PDF](https://github.com/Dans-labs/spacy-dans/raw/master/docs/Flexible_metadata_schemes_CMDI.pdf) 
* Slava Tykhonov, Andrea Scharnhorst. "Research Observatory: Research Repositories and Dataverse: Negotiating Metadata, Vocabularies and Domain Needs". ISKO UK (2021). [Event information](https://www.iskouk.org/event-4527328), [recording](https://www.youtube.com/watch?v=bw_EkE9WLjc&t=2s) and [slides](https://www.iskouk.org/resources/Documents/EventsUploads/KO-%20RO/2021-11-24-slides-KORO-VTykhonov-AScharnhorst.pdf).



