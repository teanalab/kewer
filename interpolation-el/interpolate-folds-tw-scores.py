#!/usr/bin/env python3

import os
import numpy as np
import operator
import argparse
import re
import json
from collections import defaultdict
from gensim.models import Word2Vec, KeyedVectors
from gensim import matutils
import pytrec_eval

parser = argparse.ArgumentParser()
parser.add_argument('--model')
parser.add_argument('--outpath')

parser.add_argument('--probsfile', help='word probabilities file')
parser.add_argument('--a', help='weighting parameter a',
        default=0.0003, type=float)
args = parser.parse_args()

ir_run_path = os.path.join('..', 'bm25f', 'runs', 'all.all')
queries_path = os.path.join('..', 'queries-v2_stopped.txt')
redirects_path = os.path.join('..', 'dbpedia-2015-10-kgeer', 'transitive_redirects_en.ttl')
el_path = os.path.join('..', 'entity-extraction', 'smaph', 'query-entities.json')
qrel_path = os.path.join('..', 'qrels', 'qrels.txt')
collections = ['SemSearch-ES', 'INEX-LD', 'ListSearch', 'QALD2']

word_probs = {}

with open(args.probsfile) as f:
    for line in f:
        word, prob = line.rstrip('\n').split('\t')
        word_probs[word] = float(prob)

queries = {}
with open(queries_path) as qfile:
    for line in qfile:
        qid, qtext = line.strip().split('\t')
        qtext = re.sub(r'[^\w\s]',' ' , qtext)
        qtokens = [word for word in qtext.strip().split(' ') if word != '']
        queries[qid] = qtokens

folds = {}
for collection in collections:
    with open(os.path.join('..', 'queries', 'json', collection + '.json')) as f:
        folds[collection] = json.load(f)

with open(el_path) as f:
    qid_entities = json.load(f)

with open(qrel_path, 'r') as f_qrel:
    qrel = pytrec_eval.parse_qrel(f_qrel)

evaluator = pytrec_eval.RelevanceEvaluator(
        qrel, {'ndcg_cut'})

redirects = {}
with open(redirects_path) as f:
    for line in f:
        if not line.startswith('#'):
            subj, pred, obj = line.split(maxsplit=2)
            obj = obj[:obj.rfind('.')].strip()
            redirects[subj] = obj

with open(ir_run_path, "r") as ir_run_file:
    ir_run = pytrec_eval.parse_run(ir_run_file)

model = Word2Vec.load(args.model)

entityv = KeyedVectors(model.vector_size * 2)
entityv_entities = []
entityv_weights = []
wordv = KeyedVectors(model.vector_size * 2)
wordv_entities = []
wordv_weights = []
for entity, vocab in model.wv.vocab.items():
    if entity.startswith('<'):
        entityv_entities.append(entity)
        entityv_weights.append(np.concatenate((model.syn1neg[vocab.index], model.wv.syn0[vocab.index])))
    else:
        wordv_entities.append(entity)
        wordv_weights.append(np.concatenate((model.wv.syn0[vocab.index], model.syn1neg[vocab.index])))
entityv.add(entityv_entities, entityv_weights)
wordv.add(wordv_entities, wordv_weights)
entityv.init_sims()

def wmean(tokens, entities):
    positive = []
    for token in tokens:
        token = token.lower()
        if token in wordv.vocab:
            weight = args.a / (args.a + word_probs[token])
            positive.append(wordv.word_vec(token, use_norm=False) * weight)
    for entity, score in entities:
        entity = '<{}>'.format(entity)
        if entity in entityv.vocab:
            entity_vec = entityv.word_vec(entity, use_norm=False)
            positive.append(np.concatenate((entity_vec[model.vector_size:],entity_vec[:model.vector_size])) * score)
        else:
            print('query entity {} doesn\'t have an embedding'.format(entity))
    mean = matutils.unitvec(np.array(positive).mean(axis=0))
    return mean

def get_ranking(query_id, l, qmean):
    ranking = {}
    for doc_id in ir_run[query_id].keys():
        trad_score = ir_run[query_id][doc_id]

        if doc_id in redirects:
            entity = redirects[doc_id]
            print("using redirect for entity {}: {}".format(doc_id, entity))
        else:
            entity = doc_id
        if entity in entityv.vocab:
            emb_score = np.dot(qmean, entityv.vectors_norm[entityv.vocab[entity].index])
        else:
            emb_score = 0
        ranking[doc_id] = (1 - l) * trad_score + l * emb_score
    return ranking


with open(args.outpath, "w") as run_file:
    for collection in collections:
        best_l_sum = 0
        for fold, fold_queries in folds[collection].items():
            best_l = 0.0
            best_ndcg_10 = float("-inf")
            for l in np.linspace(0,1,41):
                run = {}
                for query_id in fold_queries['training']:
                    qmean = wmean(queries[query_id], qid_entities[qid]['entities'])
                    ranking = get_ranking(query_id, l, qmean)
                    run[query_id] = dict(sorted(ranking.items(), key=operator.itemgetter(1), reverse=True))
                evaluation = evaluator.evaluate(run)
                ndcg_10 = np.mean([metrics['ndcg_cut_100'] for metrics in evaluation.values()])
                if ndcg_10 > best_ndcg_10:
                    best_l = l
                    best_ndcg_10 = ndcg_10
            print(collection, fold, best_l, best_ndcg_10)
            best_l_sum += best_l
            for query_id in fold_queries['testing']:
                qmean = wmean(queries[query_id], qid_entities[qid]['entities'])
                ranking = get_ranking(query_id, best_l, qmean)
                ranking = sorted(ranking.items(), key=operator.itemgetter(1), reverse=True)
                for i, (doc_id, score) in enumerate(ranking):
                    print(query_id, 'Q0', doc_id, i + 1, score, 'interp', sep=' ', file=run_file)
        print(collection, best_l_sum / 5)
