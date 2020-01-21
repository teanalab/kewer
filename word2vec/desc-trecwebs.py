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
trecwebs_path = 'trecwebs'
out_path = os.path.join('data', 'desc-trecwebs')

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
        # filter words and years
        norm_tokens.append(token)
    return norm_tokens

with open(out_path, "w") as out_file:
    in_paths = [os.path.join(trecwebs_path, path) for path in os.listdir('trecwebs') if path.startswith('part-')]
    for part_path in in_paths:
        with open(part_path) as infile:
            description = []
            for line in infile:
                line = line.rstrip()
                if line == '</DOC>':
                    if entity_id in topdocs:
                        print(' '.join(description), file=out_file)
                    description = []
                elif line.startswith('<DOCNO'):
                    entity_id = line[line.find('>')+1:line.rfind('<')]
                    if entity_id in topdocs:
                        out_file.write(entity_id + '\t')
                elif line not in ['<DOC>', '<TEXT>', '</TEXT>', '<names>', '</names>', '<attributes>', '</attributes>', '<categories>', '</categories>', '<similarentitynames>', '</similarentitynames>', '<relatedentitynames>', '</relatedentitynames>']:
                    if entity_id in topdocs:
                        description += literal_tokens(line)
