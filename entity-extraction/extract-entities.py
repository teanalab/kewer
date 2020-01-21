#!/usr/bin/env python3

import requests
import json
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--confidence', default=0.5, type=float)
parser.add_argument('--outfile', required=True)
args = parser.parse_args()

url = "https://api.dbpedia-spotlight.org/en/annotate"
headers = {'accept': 'application/json'}
qid_entities = {}

def stop_surface_form(surface_form):
    text = re.sub(r'\.','' , surface_form)
    text = re.sub(r'[^\w\s]',' ' , text)
    tokens = [word.lower() for word in text.split(' ') if word != '']
    return tokens

with open('queries-v2.txt') as qf:
    for line in qf:
        qid, qtext = line.rstrip().split('\t')
        # print(qid, qtext, sep=' === ')
        while True:
            r = requests.get(url, headers=headers, params={'text': qtext, 'confidence': args.confidence})
            if r.status_code == requests.codes.ok:
                break
        response = r.json()
        if 'Resources' in response:
            entities = list(set([(resource['@URI'], float(resource['@similarityScore'])) for resource in response['Resources']]))
            surface_tokens = {resource['@URI']:stop_surface_form(resource['@surfaceForm']) for resource in response['Resources']}
        else:
            entities = []
            surface_tokens = {}
        print(qid, qtext, entities, surface_tokens)
        qid_entities[qid] = {'entities': entities, 'surface_tokens': surface_tokens}

with open(args.outfile, 'w') as qef:
    json.dump(qid_entities, qef, sort_keys=True,
            indent=4, separators=(',', ': '))
