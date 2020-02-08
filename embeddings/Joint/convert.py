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

with open(out_path, 'w') as data_file:
    with open(long_abstracts_path) as f:
        for line in f:
            if not line.startswith('#'):
                subj, _, obj = line.split(maxsplit=2)
                if subj in redirects:
                    print('{} is redirected to {}!'.format(subj, redirects[subj]))
                    subj = redirects[subj]
                if subj in indexed:
                    obj = obj[:obj.rfind('.')].strip()
                    description = ' '.join(literal_tokens(obj))
                    print(description, 'entity:' + subj, sep='\t', file=data_file)
                # else:
                    # print(subj, 'not indexed, but have a long abstract!')

    with open(graph_path) as in_file:
        for line in in_file:
            subj, pred, obj = line.rstrip().split('\t')
            if obj.startswith('<') and pred != '<http://purl.org/dc/terms/subject>':
                print('entity:' + subj, 'relation:' + pred, 'entity:' + obj, sep='\t', file=data_file)
