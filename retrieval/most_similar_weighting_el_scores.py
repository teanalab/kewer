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
parser.add_argument('--words', choices=['in', 'out', 'inout'], default='inout', help="matrix to use for query words' embeddings")
parser.add_argument('--entities', choices=['in', 'out', 'inout', 'outin', 'outout'], default='outin', help="matrix to use for entity embeddings")
parser.add_argument('--norm', help='normalize word embeddings', default=False, action='store_true') # experimnts showed that normalization affects results negatively

parser.add_argument('--probsfile', help='word probabilities file')
parser.add_argument('--a', help='weighting parameter a',
        default=0.0003, type=float)

parser.add_argument('--el', help='perform entity linking', default=True, action='store_true')
parser.add_argument('--elentities', choices=['inout', 'outin'], default='inout', help="matrix to use for linked entity embeddings")

parser.add_argument('--qentities', help='entities for queries',
        default=os.path.join('..', 'entity-extraction', 'query-entities.json'))
args = parser.parse_args()

indexed_path = os.path.join('..', 'indexed')
queries_path = os.path.join('..', 'queries-v2_stopped.txt')

word_probs = {}

with open(args.probsfile) as f:
    for line in f:
        word, prob = line.rstrip('\n').split('\t')
        word_probs[word] = float(prob)

if args.el:
    with open(args.qentities) as f:
        qid_entities = json.load(f)

with open(indexed_path) as f:
    indexed = set(line.rstrip('\n') for line in f)

queries = {}
with open(queries_path) as qfile:
    for line in qfile:
        qid, qtext = line.strip().split('\t')
        qtext = re.sub(r'[^\w\s]',' ' , qtext)
        qtokens = [word for word in qtext.strip().split(' ') if word != '']
        queries[qid] = list(set(qtokens))

model = Word2Vec.load(args.model)

if args.entities not in ['inout', 'outin', 'outout']:
    entityv = KeyedVectors(model.vector_size)
else:
    entityv = KeyedVectors(model.vector_size * 2)
entityv_entities = []
entityv_weights = []
if args.words != 'inout':
    wordv = KeyedVectors(model.vector_size)
else:
    wordv = KeyedVectors(model.vector_size * 2)
wordv_entities = []
wordv_weights = []
for entity, vocab in model.wv.vocab.items():
    if entity in indexed:
        entityv_entities.append(entity)
        if args.entities == 'in':
            entityv_weights.append(model.wv.syn0[vocab.index])
        elif args.entities == 'out':
            entityv_weights.append(model.trainables.syn1neg[vocab.index])
        elif args.entities == 'inout':
            entityv_weights.append(np.concatenate((model.wv.vectors[vocab.index], model.trainables.syn1neg[vocab.index])))
        elif args.entities == 'outin':
            entityv_weights.append(np.concatenate((model.trainables.syn1neg[vocab.index], model.wv.vectors[vocab.index])))
        elif args.entities == 'outout':
            entityv_weights.append(np.concatenate((model.trainables.syn1neg[vocab.index], model.trainables.syn1neg[vocab.index])))
    elif not entity.startswith('<'):
        wordv_entities.append(entity)
        if args.words == 'in':
            wordv_weights.append(model.wv.vectors[vocab.index])
        elif args.words == 'out':
            wordv_weights.append(model.trainables.syn1neg[vocab.index])
        elif args.words == 'inout':
            wordv_weights.append(np.concatenate((model.wv.vectors[vocab.index], model.trainables.syn1neg[vocab.index])))
entityv.add(entityv_entities, entityv_weights)
wordv.add(wordv_entities, wordv_weights)
entityv.init_sims()
# wordv.init_sims()

# print(entityv.most_similar(positive=[wordv['detroit']]))

with open(args.outfile, 'w') as out_file:
    for qid, qtokens in queries.items():
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
                    if args.elentities == args.entities:
                        positive.append(entityv.word_vec(entity, use_norm=args.norm) * score)
                    elif (args.entities == 'outin' and args.elentities == 'inout' or
                            args.entities == 'inout' and args.elentities == 'outin'):
                        entity_vec = entityv.word_vec(entity, use_norm=args.norm)
                        positive.append(np.concatenate((entity_vec[model.vector_size:],entity_vec[:model.vector_size])) * score)
                    else:
                        raise Exception("Configuration is not supported")
                else:
                    print('entity {} doesn\'t have an embedding'.format(entity))
        if not positive:
            print('No vocab tokens for query {}: {}! Using zero vector for "positive".'.format(qid, ' '.join(qtokens)))
            positive.append(np.zeros(entityv.vector_size))
        for i, (entity, score) in enumerate(entityv.most_similar(positive=positive, topn=1000)):
            print(qid, 'Q0', entity, i + 1, score, 'kewer', sep=' ', file=out_file)
