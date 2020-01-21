#!/usr/bin/env python3

import numpy as np
import argparse
import os
import re
import json
from gensim.models import Word2Vec, KeyedVectors

# ss_model_filename = '../../Starspace-data/namelabels-labelonly-newnorm-cat/model.tsv'
parser = argparse.ArgumentParser()
parser.add_argument('--model')
parser.add_argument('--outfile')
parser.add_argument('--norm', help='normalize word embeddings', default=False, action='store_true')

parser.add_argument('--probsfile', default='/scratch/fedor/edeer/embeddings/WEDEER/word_probs', help='word probabilities file')
parser.add_argument('--a', help='weighting parameter a',
        default=0.0003, type=float)

parser.add_argument('--el', help='perform entity linking', default=False, action='store_true')
parser.add_argument('--elremove', help='remove linked tokens from queries', default=False, action='store_true')
parser.add_argument('--elremoveall', help='remove all tokens from queries', default=False, action='store_true')
parser.add_argument('--qentities', help='entities for queries',
        default=os.path.join('..', 'entity-extraction', 'query-entities.json'))
args = parser.parse_args()

indexed_path = os.path.join('..', '..', 'indexed')
queries_path = os.path.join('..', '..', 'queries-v2_stopped.txt')

word_probs = {}

with open(args.probsfile) as f:
    for line in f:
        word, prob = line.rstrip('\n').split('\t')
        word_probs[word] = float(prob)

with open(indexed_path) as f:
    indexed = set(line.rstrip('\n') for line in f)

queries = {}
with open(queries_path) as qfile:
    for line in qfile:
        qid, qtext = line.strip().split('\t')
        qtext = re.sub(r'[^\w\s]',' ' , qtext)
        qtokens = [word for word in qtext.strip().split(' ') if word != '']
        queries[qid] = list(set(qtokens))

if args.el:
    with open(args.qentities) as f:
        qid_entities = json.load(f)

entityv_entities = []
entityv_weights = []
wordv_entities = []
wordv_weights = []

with open(args.model) as model_file:
    for line in model_file:
        line_values = line.rstrip().split('\t')
        entity = line_values[0]
        embedding = np.array([float(x) for x in line_values[1:]])
        if entity.startswith('entity:') and entity[7:] in indexed:
            entityv_entities.append(entity[7:])
            entityv_weights.append(embedding)
        elif not (entity.startswith('entity:') or entity.startswith('relation:')):
            wordv_entities.append(entity)
            wordv_weights.append(embedding)

print('entities:', entityv_entities[:4])
print('words:', wordv_entities[:4])

entityv = KeyedVectors(entityv_weights[0].shape[0])
entityv.add(entityv_entities, entityv_weights)

wordv = KeyedVectors(wordv_weights[0].shape[0])
wordv.add(wordv_entities, wordv_weights)
wordv.init_sims()

print(entityv.most_similar(positive=[wordv['detroit']]))

with open(args.outfile, 'w') as out_file:
    for qid, qtokens in queries.items():
        if args.el:
            if args.elremove:
                for entity in qid_entities[qid]['entities']:
                    if '<{}>'.format(entity) in entityv:
                        qtokens = list(set(qtokens) - set(qid_entities[qid]['surface_tokens'][entity]))
                    else:
                        print('not removing tokens for entity {} because it doesn\'t have an embedding'.format(entity))
            elif args.elremoveall and qid_entities[qid]['entities']:
                qtokens = []
        positive = []
        for token in qtokens:
            token = token.lower()
            if token in wordv.vocab:
                weight = args.a / (args.a + word_probs[token])
                positive.append(wordv.word_vec(token, use_norm=args.norm) * weight)
            else:
                print('token {} not in vocab'.format(token))
        if args.el:
            for entity, score in qid_entities[qid]['entities']:
                entity = '<{}>'.format(entity)
                if entity in entityv:
                    positive.append(entityv.word_vec(entity, use_norm=args.norm))
                else:
                    print('entity {} doesn\'t have an embedding'.format(entity))
        if not positive:
            print('No vocab tokens for query {}: {}! Using zero vector for "positive".'.format(qid, ' '.join(qtokens)))
            positive.append(np.zeros(wordv.vector_size))
        for i, (entity, score) in enumerate(entityv.most_similar(positive=positive, topn=1000)):
            print(qid, 'Q0', entity, i + 1, score, 'kgeer', sep=' ', file=out_file)
