#!/usr/bin/env python3

import os
import fileinput
from collections import defaultdict
from nltk.tokenize import RegexpTokenizer
from unidecode import unidecode
import re

indexed_path = os.path.join('..', '..', 'indexed')
redirects_path = os.path.join('..', '..', 'dbpedia-2015-10-kewer', 'transitive_redirects_en.ttl')
long_abstracts_path = os.path.join('..', '..', 'dbpedia-2015-10-kewer', 'short_abstracts_en.ttl')

graph_path = os.path.join('..', 'KEWER', 'data', 'graph.tsv')
out_path = os.path.join('data', 'data.txt')
labels_dir = os.path.join('..', '..', 'dbpedia-2015-10-kewer', 'labels')
labels_paths = [os.path.join(labels_dir, path) for path in os.listdir(labels_dir)]

tokenizer = RegexpTokenizer(r"['\w]+")

def literal_tokens(obj):
    text = obj[obj.find('"')+1:obj.rfind('"')]
    text = (text.replace(r'\"', '"').replace(r'\t', '\t').replace(r'\b', '\b').
        replace(r'\n', '\n').replace(r'\r', '\r').replace(r'\f', '\f')) # unescape characters

    if len(text) == 0 or sum([ord(c) < 128 for c in text])/len(text) < 0.8: # filter out non-english literals
        return []

    text = unidecode(text) # remove accents
    text = text.replace('_', ' ')
    text = re.sub('([A-Z][a-z]+)', r' \1 ', text).strip() # separate CamelCase
    text = text.lower()

    tokens = tokenizer.tokenize(text)
    norm_tokens = []
    for token in tokens:
        token = re.sub(r"'s$", "", token)
        token = token.replace("'", "")
        # filter words and years
        if len(token) > 1 and len(token) <= 20 and (all(c.isalpha() for c in token) or (re.match(r'^[12][0-9]{3}$', token) and int(token) <= 2050)):
            norm_tokens.append(token)
    return norm_tokens

with open(indexed_path) as f:
    indexed = set(line.rstrip('\n') for line in f)

redirects = {}
with open(redirects_path) as f:
    for line in f:
        if not line.startswith('#'):
            subj, pred, obj = line.split(maxsplit=2)
            obj = obj[:obj.rfind('.')].strip()
            redirects[subj] = obj

labels_set = defaultdict(set)
for line in fileinput.input(labels_paths):
    if line.startswith('#'):
        continue
    subj, pred, obj = line.split(maxsplit=2)
    obj = obj[:obj.rfind('.')].strip()
    if subj in redirects:
        subj = redirects[subj]
    if subj in indexed and (pred == '<http://www.w3.org/2000/01/rdf-schema#label>' or
            pred == '<http://dbpedia.org/ontology/wikiPageWikiLinkText>') and obj.endswith("@en"):
        tokens = literal_tokens(obj)
        if len(tokens):
            labels_set[subj].add(' '.join(tokens))

with open(out_path, 'w') as data_file:
    for entity, labels in labels_set.items():
        for label in labels:
            print(label, 'entity:' + entity, sep='\t', file=data_file)

    with open(graph_path) as in_file:
        for line in in_file:
            subj, pred, obj = line.rstrip().split('\t')
            if obj.startswith('<') and pred != '<http://purl.org/dc/terms/subject>':
                print('entity:' + subj, 'relation:' + pred, 'entity:' + obj, sep='\t', file=data_file)
