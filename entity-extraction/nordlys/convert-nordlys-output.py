import sys
import json

query_entities = {}

with open('../queries-v2.txt') as qf:
    for line in qf:
        qid, _ = line.rstrip().split('\t')
        query_entities[qid] = []

with open(sys.argv[1]) as cmns_file:
    for line in cmns_file:
        line = line.rstrip()
        qid, score, uri = line.split('\t')
        score = float(score)
        query_entities[qid].append((uri, score))

output_json = {}
for qid, entities in query_entities.items():
    output_entities = []
    for entity, score in entities:
        entity = entity[1:-1]
        entity = entity.replace("dbpedia:", "http://dbpedia.org/resource/")
        output_entities.append((entity, score))
    output_json[qid] = {'entities': output_entities}

with open(sys.argv[2], 'w') as qef:
    json.dump(output_json, qef, sort_keys=True,
            indent=4, separators=(',', ': '))
