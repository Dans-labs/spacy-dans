import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
from nltk.chunk import conlltags2tree, tree2conlltags
from pprint import pprint
from textacy import extract
import io
import sys
import os
from langdetect import detect

nlp = en_core_web_sm.load()
nlp_nl = spacy.load("nl_core_news_sm")

def load_model(lang, text, orig_text):
    #Language models supported: nlp_en, nlp_nl, nlp_ru, nlp_de, nlp_es nlp_fr nlp_nb nlp_it nlp_pl nlp_pt
    doc = False
    docNER = False

    if lang == 'en':
        doc = nlp(text)
        docNER = nlp(orig_text)
    if lang == 'nl':
        doc = nlp_nl(text)
        docNER = nlp_nl(orig_text)
    if lang == 'ru':
        nlp_ru = spacy.load("de_core_news_sm")
        doc = nlp_ru(text)
        docNER = nlp_ru(orig_text)
    if lang == 'de':
        nlp_de = spacy.load("de_core_news_sm")
        doc = nlp_de(text)
        docNER = nlp_de(orig_text)
    if lang == 'es':
        nlp_es = spacy.load("es_core_news_sm")
        doc = nlp_es(text)
        docNER = nlp_es(orig_text)
    if lang == 'fr':
        nlp_fr = spacy.load("fr_core_news_sm")
        doc = nlp_fr(text)
        docNER = nlp_fr(orig_text)
    if lang == 'nb':
        nlp_nb = spacy.load("nb_core_news_sm")
        doc = nlp_nb(text)
        docNER = nlp_nb(orig_text)
    if lang == 'it':
        nlp_it = spacy.load("it_core_news_sm")
        doc = nlp_it(text)
        docNER = nlp_it(orig_text)
    if lang == 'pl':
        nlp_pl = spacy.load("pl_core_news_sm")
        doc = nlp_pl(text)
        docNER = nlp_pl(orig_text)
    if lang == 'pt':
        nlp_pl = spacy.load("pt_core_news_sm")
        doc = nlp_pt(text)
        docNER = nlp_pt(orig_text)
    return (doc, docNER)

def ngrams_tokens(filename=None, article=False, params={}):
    text = False
    data = {}
    lines = False
    grams_ammount = 2
    SUMMARY_LEN = 250
    MIN_FREQ=2
    if 'plain_text' in article:
        summary = ''
        for sentence in article['plain_text']:
            if len(summary) < SUMMARY_LEN:
                summary = summary + ' ' + str(sentence['text'])
        if summary:
            article['summary'] = summary
        article['plain_text'].insert(0, {'text': article['title'] + '. '})
        text = str(article['plain_text'])

    if filename:
        print("NLP process for %s..." % filename)
        fo = io.open(filename, mode="r", encoding="utf-8")
        lines = fo.readlines()
        text = str(lines)

    text = text.replace('\n', ' ')
    if lines:
        lang = detect(lines[0:5])
    else:
        lang = detect(text)
    data['lang'] = lang
    orig_text = text
    text = text.lower()
    
    if 'disable_nlp' in os.environ:
        lang = 'unknown'
        skip = True
    (doc, docNER) = load_model(lang, text, orig_text)

    compoundentities = []
    entities = []
    savedkeywords = {}

    # If there is language model
    if doc:
        for X in docNER.ents:
            tmpres = {}
            tmpres['entity'] = X.text
            tmpres['label'] = X.label_
            compoundentities.append(tmpres)

        for token in docNER:
            entinfo = {'text': token.text, 'pos': token.pos_, 'dep': token.dep_}
            entities.append(entinfo)

        #pprint([(X.text, X.label_) for X in doc.ents])
        if 'ngrams' in params:
            grams_ammount = int(params['ngrams'])
        if 'minfreq' in params:
            min_freq = int(params['minfreq'])

        ngrams = list(extract.basics.ngrams(doc, grams_ammount, min_freq=MIN_FREQ))
        for ngram in ngrams:
            savedkeywords[str(ngram)] = str(ngram)

        for token in savedkeywords:
            print("%s" % (token))

    if 'showcontent' in params:
        thisdoc = {}
        thisdoc['title'] = article['title']
        thisdoc['text'] = article['plain_text']
        thisdoc['content'] = article['content']
        if 'summary' in article:
            thisdoc['summary'] = article['summary']
        data['content'] = thisdoc

    if 'showpos' in params:
        if entities:
            data['pos'] = entities
    if compoundentities:
        data['original_entities'] = compoundentities
        entities = []
        known = {}
        thisent = []
        for e in compoundentities:
            known[e['entity']] = e['label']
        for e in known:
            entities.append(e)
        data['entities'] = ", ".join(entities)

    if savedkeywords:
        keywords = []
        for item in savedkeywords:
            for key in item:
                keywords.append(key)
        data['keywords'] = ", ".join(savedkeywords)
        data['original_keywords'] = savedkeywords
    return data
