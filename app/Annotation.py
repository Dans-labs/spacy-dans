import json
import requests
import os
import tempfile
import time
from doccano_client import DoccanoClient
from urllib.parse import urlparse
import re

DOCCANO_PROJECT_ID = 12
MAX_RESULTS = 10000
TAG_TYPES = ['UMLS', 'GGP', 'SO', 'TAXON', 'CHEBI', 'GO', 'CL', 'DNA', 'CELL_TYPE', 'CELL_LINE', 'RNA', 'PROTEIN', 'DISEASE', 'CHEMICAL', 'CANCER', 'ORGAN', 'TISSUE', 'ORGANISM', 'CELL', 'AMINO_ACID', 'GENE_OR_GENE_PRODUCT', 'SIMPLE_CHEMICAL', 'ANATOMICAL_SYSTEM', 'IMMATERIAL_ANATOMICAL_ENTITY', 'MULTI-TISSUE_STRUCTURE', 'DEVELOPING_ANATOMICAL_STRUCTURE', 'ORGANISM_SUBDIVISION', 'CELLULAR_COMPONENT', 'PATHOLOGICAL_FORMATION', 'ORGANISM_SUBSTANCE']
SPLIT_SENTENCES = False

def dataverse_metadata(response):
    metadata = {}
    metadata['content'] = {}
    for typename in response['fields']:
        if typename['typeName'] == 'title':
            metadata['title'] = str(typename['value'])
        if typename['typeName'] == 'dsDescription':
            metadata['description'] = typename['value'][0]['dsDescriptionValue']['value']
        if typename['typeName'] == 'notesText':
            metadata['notesText'] = typename['value']
        if typename['typeName'] == 'keyword':
            for i in range(0, len(typename['value'])):
                if not 'keywords' in metadata:
                    metadata['keywords'] = typename['value'][i]['keywordValue']['value'].split(',')
                else:
                    metadata['keywords']+= typename['value'][i]['keywordValue']['value'].split(',')
    metadata['content']['fulltext'] = metadata['title'] + '. ' + metadata['description']
    if 'notesText' in metadata:
        metadata['content']['fulltext'] = metadata['content']['fulltext'] + '. ' + metadata['notesText']

    metadata['content']['text'] = []
    metadata['original_entities'] = []
    for item in metadata['content']['fulltext'].split('. '):
        metadata['content']['text'].append({'text': item})
    if 'keywords' in metadata:
        for item in metadata['keywords']:
            metadata['original_entities'].append({'entity': item.strip(), 'label': 'keyword', 'type': 'human' })
    #if metadata:
        #return save_annotation(metadata)
    return metadata 

def doccano_annotation(document):
    results = []
    texts = []
    labels = []
    previous_length = 0
    done_labels = [] # Some label could be applied multiple times which would cause a constraint error on doccano's side.
                 # This serves as marking sure a label is applied only once at a given location in the text
    content = []
    data = {}
    spacydata = []
    sentences = document['content']['text']
    for item in sentences:
        content.append(item['text'])

    if content:
        stream = []
        labels = []
        for i in range(0, len(content)):
            sentence = content[i]
            data = {}
            spacystream = []
            data['id'] = i
            data['text'] = sentence
            data['meta'] = [ { 'ORG': 'https://www.wikidata.org/wiki/Q43229' },
                            { 'PERSON': 'https://www.wikidata.org/wiki/Q215627' },
                            {'CARDINAL': 'https://www.wikidata.org/wiki/Q163875',
                            'DATE': 'https://www.wikidata.org/wiki/Property:P2913'}]
            data['meta'] = []
            if SPLIT_SENTENCES:
                labels = []

            known = {}
            labelspos = []
            #document['original_entities'] = ''
            for thistag in document['original_entities']:
                print(str(thistag))
                tag = thistag['entity']
                label = thistag['label']
                tag_type = label
                if not label in known:
                    if len(tag) == 1: # empty lists are returned '[]' as a string by ES, and some lists contain just punctuation symbols
                        continue

                    #pos = sentence.find(tag)
                    pos = sentence.lower().find(tag.lower())
                    if pos != -1:
                        if not SPLIT_SENTENCES:
                            pos = previous_length + pos #Adding the length of previous sentences to calculate the new position

                        if '{},{},{}'.format(pos, pos+len(tag), tag_type) not in done_labels:
                            #labels.append([pos, pos+len(tag), tag_type])
                            done_labels.append('{},{},{}'.format(pos, pos+len(tag), tag_type))
                            thislabel = [ pos, pos+len(tag), tag_type ]
                            if not str(thislabel) in known:
                                labelspos.append(thislabel)
                                known[str(thislabel)] = label
                                #print("%s * %s %s => %s" % (sentence, tag, label, thislabel))
            data['label'] = labelspos
            stream.append(data)
            spacystream.append(sentence)
            spacystream.append({'entities': labelspos })
            spacydata.append(spacystream)

        if SPLIT_SENTENCES:
            results.append(json.dumps({"text":sentence, "labels":labels}))
        else:
            if sentence[-1] == '.':
                sentence = sentence[:-1]

            previous_length += len(sentence) + 2 # Sentences will be joined with '. '
            texts.append(sentence)
    return (stream, spacydata)

def save_annotation(document, thisparams=None):
    (annotation, spacyanno) = doccano_annotation(document)
    params = {}
    if thisparams:
        params = thisparams
    if 'url' in params:
        params['urlm'] = re.search(r'Id\=(\S+)', params['url'])
        params['domain'] = "%s://%s" % (urlparse(url).scheme, urlparse(url).netloc)
        params['netloc'] = urlparse(url).netloc
        if urlm:
            params['doi'] = urlm.group(1)

    if 'doi' in params:
        filename = "%s.jsonl" % params['doi']
    else:
        filename = "doccano.jsonl"
    if 'CACHEFOLDER' in os.environ:
        tmpdir = os.environ['CACHEFOLDER']
    else:
        tmpdir = '/tmp'

    if 'netloc' in params:
        tmpdir = "%s/%s" % (tmpdir, params['netloc'])
        if not os.path.exists(tmpdir):
            os.makedirs(tmpdir)

    outfile = "%s/%s" % (tmpdir, filename)
    outfilespacy = "%s/%s.spacy" % (tmpdir, filename)
    with open(outfile, 'w', encoding='utf8') as f:
        #for item in annotation:
            #f.write("%s\n" % json.dumps(item))
        f.write(json.dumps(annotation))

    if spacyanno:
        with open(outfilespacy, 'w', encoding='utf8') as spacyf:
            spacyf.write(json.dumps(spacyanno))
    params[filename] = tmpdir
    send_to_doccano(filename, params)
    #spacy_train = convert_to_spacy(annotation)
    return (annotation, spacyanno)

def send_to_doccano(filename, thisparams=None):
    params = {}
    if thisparams:
        params = thisparams

    # instantiate a client and log in to a Doccano instance
    doccano_client = DoccanoClient(os.environ['DOCCANO_URL'])
    doccano_client.login(
    os.environ['DOCCANO_USER'],
    os.environ['DOCCANO_PASSWORD']
)

    # get basic information about the authorized user
    #r_me = doccano_client.get_me()
    cachedir = '/tmp'
    if 'CACHEFOLDER' in os.environ:
        cachedir = os.environ['CACHEFOLDER']
    project_id = 1
    if 'DOCCANO_PROJECT_ID' in os.environ:
        project_id = os.environ['DOCCANO_PROJECT_ID']
    if 'DOCCANO_PROJECT_ID' in params:
        project_id = params['DOCCANO_PROJECT_ID']
    tmpdir = '/tmp'
    if filename in params:
        print("File %s" % filename)
        print(project_id)
        tmpdir2 = 0 #= params[filename]['tmpdir']
    #r_json_upload = doccano_client.post_doc_upload(project_id, filename, tmpdir, format='JSON')
    taskname = os.environ['TASKNAME']
    r_json_upload = doccano_client.upload(project_id, ["%s/%s" % (tmpdir, filename)], task=taskname, format='JSON')
    return

def convert_to_spacy(lines):
    data = []
    for line in lines:
        linedata = {}
        if "label" in line:
            line["entities"] = line.pop("label")
        else:
            line["entities"] = []

        tmp_ents = []
        for e in line["entities"]:
            if e[2] in ['RISK', 'ORG', 'GPE', 'DATE', 'LAW', 'CARDINAL', 'MONEY', 'PRODUCT', 'ORDINAL', 'PERCENT', 'LOC', 'NORP', 'EVENT', 'WORK_OF_ART', 'FAC', 'PERSON', 'TIME', 'Date']:
                tmp_ents.append({"start": e[0], "end": e[1], "label": e[2]})

            line["entities"] = tmp_ents
        linedata["entities"] = line["entities"]
        linedata["text"] = line["text"]
        data.append(linedata)
    return data
