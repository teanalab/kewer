#!/usr/bin/env python3

import os
import fileinput
import random
from collections import defaultdict
from nltk.tokenize import RegexpTokenizer
from unidecode import unidecode
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--infile', help='input file with walks', required=True)
parser.add_argument('--outfile', help='output file with word2vec training data', required=True)
parser.add_argument('--prob', help='replace probability', default=0.9, type=float)
parser.add_argument('--pred', help='process predicates', default=False, action='store_true')
parser.add_argument('--lit', help='keep literals', default=False, action='store_true')
args = parser.parse_args()

redirects_path = os.path.join('..', '..', 'dbpedia-2016-10-kewer', 'transitive_redirects_en.ttl')
labels_dir = os.path.join('..', '..', 'dbpedia-2016-10-kewer', 'labels')
labels_paths = [os.path.join(labels_dir, path) for path in os.listdir(labels_dir)]
graph_dir = os.path.join('..', '..', 'dbpedia-2016-10-kewer', 'graph')
graph_paths = [os.path.join(graph_dir, path) for path in os.listdir(graph_dir)]

remove_uris = {'<http://purl.org/dc/elements/1.1/description>', '<http://dbpedia.org/property/description>',
               '<http://dbpedia.org/property/shortDescription>', '<http://purl.org/dc/terms/subject>'}

name_preds = set(pred.lower() for pred in [
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

tokenizer = RegexpTokenizer(r"['\w]+")


def literal_tokens(obj):
    text = obj[obj.find('"') + 1:obj.rfind('"')]
    text = (text.replace(r'\"', '"').replace(r'\t', '\t').replace(r'\b', '\b').
            replace(r'\n', '\n').replace(r'\r', '\r').replace(r'\f', '\f'))  # unescape characters

    if len(text) == 0 or sum([ord(c) < 128 for c in text]) / len(text) < 0.8:  # filter out non-english literals
        return []

    text = unidecode(text)  # remove accents
    text = text.replace('_', ' ')
    text = re.sub('([A-Z][a-z]+)', r' \1 ', text).strip()  # separate CamelCase
    text = text.lower()

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


def uri_to_tokens(uri):
    uri = uri[uri.rfind('/') + 1:-1]
    uri = uri[uri.rfind(':') + 1:]
    return literal_tokens('"{}"'.format(uri))


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
    if (
            pred == '<http://www.w3.org/2000/01/rdf-schema#label>' or pred == '<http://dbpedia.org/ontology/wikiPageWikiLinkText>') and obj.endswith(
        "@en"):
        tokens = literal_tokens(obj)
        if len(tokens):
            labels_set[subj].add(' '.join(tokens))

for line in fileinput.input(graph_paths):
    if line.startswith('#'):
        continue
    subj, pred, obj = line.split(maxsplit=2)
    obj = obj[:obj.rfind('.')].strip()
    if subj in redirects:
        subj = redirects[subj]
    if pred.lower() in name_preds and obj.endswith("@en"):
        tokens = literal_tokens(obj)
        if len(tokens):
            labels_set[subj].add(' '.join(tokens))

labels = {}
for subj, subj_labels in labels_set.items():
    labels[subj] = list(subj_labels)

with open(args.infile) as in_file, open(args.outfile, 'w') as out_file:
    for line in in_file:
        walk = line.rstrip().split('\t')
        for i, step in enumerate(walk):
            if i > 0:
                prefix = ' '
            else:
                prefix = ''
            if step.startswith('<'):
                if (i % 2 != 1 or args.pred) and (i < len(walk) - 2 or args.lit):
                    if random.random() < args.prob:  # should replace uri with label
                        if step not in remove_uris:
                            if step in labels:
                                label = random.choice(labels[step])
                            else:
                                label = ' '.join(uri_to_tokens(step))
                                # print("{} doesn't have a label! Using as label: {}".format(step, label))
                            out_file.write(prefix + label)
                    else:  # should keep uri
                        out_file.write(prefix + step)
            elif args.lit:
                out_file.write(prefix + step)
        out_file.write('\n')
