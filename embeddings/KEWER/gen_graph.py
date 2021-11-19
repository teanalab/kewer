#!/usr/bin/env python3

import os
import fileinput
from nltk.tokenize import RegexpTokenizer
from unidecode import unidecode
import re
from collections import defaultdict

indexed_path = os.path.join('..', '..', 'indexed')
redirects_path = os.path.join('..', '..', 'dbpedia-2021-06-kewer', 'redirects_lang=en_transitive.ttl')
categories_path = os.path.join('..', '..', 'dbpedia-2021-06-kewer', 'categories_lang=en_articles.ttl')
graph_dir = os.path.join('..', '..', 'dbpedia-2021-06-kewer', 'graph')
graph_paths = [os.path.join(graph_dir, path) for path in os.listdir(graph_dir)]

blacklist = set(pred.lower() for pred in [
    '<http://www.w3.org/2000/01/rdf-schema#seeAlso>',
    '<http://dbpedia.org/property/seeAlso>',
    '<http://www.w3.org/2002/07/owl#differentFrom>',
    '<http://dbpedia.org/property/urlname>',
    '<http://dbpedia.org/property/isbn>',
    '<http://dbpedia.org/property/issn>',
    '<http://dbpedia.org/ontology/isbn>',
    '<http://dbpedia.org/ontology/issn>',
    '<http://dbpedia.org/property/caption>',
    '<http://dbpedia.org/property/imageCaption>',
    '<http://dbpedia.org/property/photoCaption>',
    '<http://dbpedia.org/property/mapCaption>',
    '<http://dbpedia.org/property/staticImageCaption>',
    '<http://dbpedia.org/property/floatCaption>',
    '<http://dbpedia.org/property/group>',
    '<http://dbpedia.org/property/groupstyle>',
    '<http://dbpedia.org/property/style>',
    '<http://dbpedia.org/property/align>',
    '<http://dbpedia.org/property/width>',
    '<http://dbpedia.org/property/bgcolor>',
    '<http://dbpedia.org/property/direction>',
    '<http://dbpedia.org/property/headerAlign>',
    '<http://dbpedia.org/property/footerAlign>',
    '<http://dbpedia.org/property/headerBackground>',
    '<http://dbpedia.org/property/imagenamel>',
    '<http://dbpedia.org/property/imagenamer>',
    '<http://dbpedia.org/property/imageAlt>',
    '<http://dbpedia.org/property/voy>',
    '<http://dbpedia.org/property/wikt>',
    '<http://dbpedia.org/property/commons>',
    '<http://dbpedia.org/property/id>',
    '<http://dbpedia.org/property/text>',
    '<http://dbpedia.org/property/reason>',
    '<http://dbpedia.org/property/hideroot>',
    '<http://dbpedia.org/property/notes>',
    '<http://dbpedia.org/property/crewPhotoAlt>',
    '<http://dbpedia.org/property/signatureAlt>',
    '<http://dbpedia.org/property/title>',
    '<http://dbpedia.org/property/alt>',
    # 'name' predicates that shouldn't be used for names
    '<http://dbpedia.org/property/nativeName>',
    '<http://dbpedia.org/ontology/formerName>',
    '<http://dbpedia.org/property/names',
    # name predicates that can be used for names
    '<http://dbpedia.org/property/name>',
    '<http://dbpedia.org/property/fullname>',
    '<http://dbpedia.org/property/birthName>',
    '<http://dbpedia.org/property/longName>',
    '<http://dbpedia.org/property/conventionalLongName>',
    '<http://dbpedia.org/property/commonName>',
    '<http://dbpedia.org/property/altname>',
    '<http://dbpedia.org/property/glottorefname>',
    '<http://dbpedia.org/property/sname>',
    '<http://dbpedia.org/property/clubname>',
    '<http://dbpedia.org/property/alternativeNames>',
    '<http://dbpedia.org/property/officialName>',
    '<http://xmlns.com/foaf/0.1/name>',
    '<http://dbpedia.org/ontology/birthName>',
    '<http://dbpedia.org/ontology/longName>',
    '<http://xmlns.com/foaf/0.1/givenName>',
    '<http://xmlns.com/foaf/0.1/surname>',  # didn't find this one in data
    '<http://dbpedia.org/property/showName>',
    '<http://dbpedia.org/property/shipName>',
    '<http://dbpedia.org/property/unitName>',
    '<http://dbpedia.org/property/otherName>',
    '<http://dbpedia.org/property/otherNames>'
])

with open(indexed_path) as f:
    indexed = set(line.rstrip('\n') for line in f)

redirects = {}
with open(redirects_path) as f:
    for line in f:
        if not line.startswith('#'):
            subj, pred, obj = line.split(maxsplit=2)
            obj = obj[:obj.rfind('.')].strip()
            redirects[subj] = obj

tokenizer = RegexpTokenizer(r"['\w]+")


def literal_tokens(obj):
    text = obj[obj.find('"') + 1:obj.rfind('"')]
    text = (text.replace(r'\"', '"').replace(r'\t', '\t').replace(r'\b', '\b').
            replace(r'\n', '\n').replace(r'\r', '\r').replace(r'\f', '\f'))  # unescape characters

    if len(text) == 0 or sum([ord(c) < 128 for c in text]) / len(text) < 0.8:  # filter out non-english literals
        return []

    text = unidecode(text)  # remove accents
    text = re.sub('([A-Z][a-z]+)', r' \1 ', text).strip()  # separate CamelCase
    text = text.lower()

    if text in ['yes', 'no', 'on', 'off']:  # filter out boolean literals
        return []
    if text.startswith('http'):  # filter out urls
        return []
    if re.search(r'\.[a-z]{3,4}$', text):  # filter out filenames
        return []

    tokens = tokenizer.tokenize(text)
    norm_tokens = []
    for token in tokens:
        token = re.sub(r"'s$", "", token)
        token = token.replace("'", "")
        # filter words and years
        if len(token) > 1 and len(token) <= 20 and (
                all(c.isalpha() for c in token) or (re.match(r'^[12][0-9]{3}$', token) and int(token) <= 2050)):
            norm_tokens.append(token)
    return norm_tokens


outnodes = defaultdict(set)

for line in fileinput.input(graph_paths):
    if line.startswith('#'):
        continue
    subj, pred, obj = line.split(maxsplit=2)
    if pred.lower() in blacklist or re.match(r'<http://dbpedia.org/property/([0-9]|footnote|.{1,2}>$)', pred):
        continue
    obj = obj[:obj.rfind('.')].strip()
    if subj in redirects:
        subj = redirects[subj]
    if obj in redirects:
        obj = redirects[obj]

    if obj.startswith('"') and subj in indexed:
        tokens = literal_tokens(obj)
        if len(tokens):
            outnodes[subj].add((pred, ' '.join(tokens)))
    elif subj in indexed and obj in indexed:
        outnodes[subj].add((pred, obj))

with open(categories_path) as input_file:
    for line in input_file:
        if line.startswith('#'):
            continue
        subj, pred, obj, _ = line.split()
        if subj in redirects:
            subj = redirects[subj]

        if subj in indexed:
            outnodes[subj].add((pred, obj))

if not os.path.exists('data'):
    os.makedirs('data')

with open(os.path.join('data', 'graph.tsv'), 'w') as out_file:
    for subj, onodes in outnodes.items():
        for pred, obj in onodes:
            print(subj, pred, obj, sep='\t', file=out_file)
