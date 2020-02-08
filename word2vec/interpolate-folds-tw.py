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
from nltk.tokenize import RegexpTokenizer
from unidecode import unidecode

parser = argparse.ArgumentParser()
parser.add_argument('--model')
parser.add_argument('--outpath')
parser.add_argument('--words', choices=['in', 'inout'], help="matrix to use for query words' embeddings")
parser.add_argument('--entities', choices=['in', 'out', 'inout', 'outin', 'outout'], help="matrix to use for entity embeddings")
parser.add_argument('--entdescs', help="file with descriptions for entities to use")
parser.add_argument('--norm', help='normalize word embeddings', default=False, action='store_true') # experimnts showed that normalization affects results negatively
parser.add_argument('--desm', default=False, action='store_true')

parser.add_argument('--probsfile', help='word probabilities file')
parser.add_argument('--a', help='weighting parameter a',
        default=0.0003, type=float)
parser.add_argument('--ew', default=False, action='store_true', help="weight terms in entity labels")
args = parser.parse_args()

ir_run_path = os.path.join('..', 'bm25f', 'runs', 'all.all')
queries_path = os.path.join('..', 'queries-v2_stopped.txt')
redirects_path = os.path.join('..', 'dbpedia-2015-10-kewer', 'transitive_redirects_en.ttl')
qrel_path = os.path.join('..', 'qrels', 'qrels.txt')
collections = ['SemSearch-ES', 'INEX-LD', 'ListSearch', 'QALD2']
labels_path = os.path.join('..', 'dbpedia-2015-10-kewer', 'labels', 'labels_en.ttl')
trecwebs_path = 'trecwebs'

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

tokenizer = RegexpTokenizer(r"['\w]+")

model = Word2Vec.load(args.model)

def wmean(tokens, regime, norm, weighting):
    positive = []
    for token in tokens:
        if token.lower() in model:
            token = token.lower()
            token_index = model.wv.vocab[token].index
            if regime == 'in':
                tokenemb = model.wv.syn0[token_index]
            elif regime == 'out':
                tokenemb = model.syn1neg[token_index]
            elif regime == 'inout':
                tokenemb = np.concatenate((model.wv.syn0[token_index], model.syn1neg[token_index]))
            elif regime == 'outin':
                tokenemb = np.concatenate((model.syn1neg[token_index], model.wv.syn0[token_index]))
            elif regime == 'outout':
                tokenemb = np.concatenate((model.syn1neg[token_index], model.syn1neg[token_index]))
            if norm:
                tokenemb = tokenemb / np.sqrt((tokenemb ** 2).sum(-1))
            if weighting:
                if token in word_probs:
                    weight = args.a / (args.a + word_probs[token])
                else:
                    weight = 1.0
                    print(token, "doesn't have a weight!")
                tokenemb = tokenemb * weight
            positive.append(tokenemb)
    if not positive:
        # print("no embeddings for tokens:", tokens)
        if regime in ['in', 'out']:
            return np.zeros(model.vector_size)
        else:
            return np.zeros(model.vector_size * 2)
    mean = matutils.unitvec(np.array(positive).mean(axis=0))
    return mean

print("Started to calculate entity embeddings and scores...", end='', flush=True)
entdescs = {}
with open(args.entdescs) as desc_file:
    for line in desc_file:
        entity_id, desc = line.rstrip().split('\t')
        entdescs[entity_id] = wmean(desc.split(' '), args.entities, False, args.ew)

emb_scores = {}
for query_id, query_tokens in queries.items():
    for doc_id in ir_run[query_id].keys():
        qmean = wmean(queries[query_id], args.words, args.norm, True)
        if query_id not in emb_scores:
            emb_scores[query_id] = {}
        emb_scores[query_id][doc_id] = np.dot(qmean, entdescs[doc_id])
print("Finished")

def get_ranking(query_id, l):
    ranking = {}
    for doc_id in ir_run[query_id].keys():
        trad_score = ir_run[query_id][doc_id]

        if doc_id in redirects:
            entity = redirects[doc_id]
            print("using redirect for entity {}: {}".format(doc_id, entity))
        else:
            entity = doc_id
        emb_score = emb_scores[query_id][doc_id]
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
                    ranking = get_ranking(query_id, l)
                    run[query_id] = dict(sorted(ranking.items(), key=operator.itemgetter(1), reverse=True))
                evaluation = evaluator.evaluate(run)
                ndcg_10 = np.mean([metrics['ndcg_cut_100'] for metrics in evaluation.values()])
                if ndcg_10 > best_ndcg_10:
                    best_l = l
                    best_ndcg_10 = ndcg_10
            print(collection, fold, best_l, best_ndcg_10)
            best_l_sum += best_l
            for query_id in fold_queries['testing']:
                ranking = get_ranking(query_id, best_l)
                ranking = sorted(ranking.items(), key=operator.itemgetter(1), reverse=True)
                for i, (doc_id, score) in enumerate(ranking):
                    print(query_id, 'Q0', doc_id, i + 1, score, 'interp', sep=' ', file=run_file)
        print(collection, best_l_sum / 5)
