#!/usr/bin/env python3

# run as: python word_probs.py ../dbpedia-2015-10-kewer/**.ttl --outfile ../word_probs

import argparse
import fileinput
import nltk
import re
from collections import Counter
from unidecode import unidecode
from nltk.tokenize import RegexpTokenizer
tokenizer = RegexpTokenizer(r'\w+')

parser = argparse.ArgumentParser()

parser.add_argument('files', metavar='FILE', nargs='*', help='files to read, if empty, stdin is used')
parser.add_argument('--outfile', help='output file')
args = parser.parse_args()

print(args)

triples = set()

def normal_tokens(text):
    tokens = tokenizer.tokenize(text.lower())
    norm_tokens = []
    for token in tokens:
        norm_token = token
        if (not any(c.isalpha() for c in norm_token) and
                not (re.match(r'^[0-9]{4}$', norm_token) and
                    int(norm_token) < 2050)):
            norm_token = re.sub(r'\d', '0', norm_token)
        norm_tokens.append(unidecode(norm_token))
    return norm_tokens

word_counter = Counter()
total_count = 0

for line in fileinput.input(args.files):
    if not line.startswith('#'):
        subj, pred, obj = line.split(maxsplit=2)
        obj = obj[:obj.rfind('.')].strip()
        if obj.startswith('"'):
            lit_text = obj[obj.find('"')+1:obj.rfind('"')]
            lit_text = (lit_text.replace(r'\"', '"').replace(r'\t', '\t').replace(r'\b', '\b').
                replace(r'\n', '\n').replace(r'\r', '\r').replace(r'\f', '\f'))
            lit_text = lit_text.replace(':', '')
            sents = nltk.sent_tokenize(lit_text)
            for sent in sents:
                norm_tokens = normal_tokens(sent.lower())
                word_counter.update(norm_tokens)
                total_count += len(norm_tokens)

test_total_prob = 0.0
with open(args.outfile, 'w') as out_file:
    for word, count in sorted(word_counter.items()):
        print(word, count / total_count, sep='\t', file=out_file)
        test_total_prob += count / total_count

print('Total probability (should be 1):', test_total_prob)
