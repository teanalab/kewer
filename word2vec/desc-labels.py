#!/usr/bin/env python3

import os
import numpy as np
import operator
import re
import json
from collections import defaultdict
import pytrec_eval
from nltk.tokenize import RegexpTokenizer
from unidecode import unidecode

ir_run_path = os.path.join('..', 'bm25f', 'runs', 'all.all')
qrel_path = os.path.join('..', 'qrels', 'qrels.txt')
out_path = os.path.join('data', 'desc-labels')
labels_path = os.path.join('..', 'dbpedia-2015-10-kewer', 'labels', 'labels_en.ttl')

with open(qrel_path, 'r') as f_qrel:
    qrel = pytrec_eval.parse_qrel(f_qrel)

with open(ir_run_path, "r") as ir_run_file:
    ir_run = pytrec_eval.parse_run(ir_run_file)

topdocs = set()
for query, rels in ir_run.items():
    topdocs.update(rels.keys())

tokenizer = RegexpTokenizer(r"['\w]+")

def literal_tokens(text):
    text = (text.replace(r'\"', '"').replace(r'\t', '\t').replace(r'\b', '\b').
        replace(r'\n', '\n').replace(r'\r', '\r').replace(r'\f', '\f')) # unescape characters

    text = unidecode(text) # remove accents
    text = re.sub('([A-Z][a-z]+)', r' \1 ', text).strip() # separate CamelCase

    tokens = tokenizer.tokenize(text)
    norm_tokens = []
    for token in tokens:
        token = re.sub(r"'s$", "", token)
        token = token.replace("'", "")
        norm_tokens.append(token)
    return norm_tokens

with open(labels_path) as infile, open(out_path, "w") as out_file:
    for line in infile:
        if line.startswith('#'):
            continue
        subj, _, obj = line.split(maxsplit=2)
        if subj in topdocs:
            obj = obj[:obj.rfind('.')].strip()
            text = obj[obj.find('"')+1:obj.rfind('"')]
            print(subj, ' '.join(literal_tokens(text)).lower(), file=out_file, sep='\t')
