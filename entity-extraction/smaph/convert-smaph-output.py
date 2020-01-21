import json
import re

with open('smaph-responses.json') as f:
    responses = json.load(f)

queries = {}
with open('../queries-v2.txt') as qf:
    for line in qf:
        qid, qtext = line.rstrip().split('\t')
        queries[qid] = qtext

def stop_surface_form(surface_form):
    text = re.sub(r'\.','' , surface_form)
    text = re.sub(r'[^\w\s]',' ' , text)
    tokens = [word.lower() for word in text.split(' ') if word != '']
    return tokens

output_json = {}
for qid, response in responses.items():
    output_entities = []
    output_surface_tokens = {}
    for annotation in response['annotations']:
        entity = "http://dbpedia.org/resource/" + annotation['title'].replace(' ', '_')
        score = annotation['score']
        output_entities.append((entity, score))
        surface_form = queries[qid][annotation['begin']:annotation['end']]
        output_surface_tokens[entity] = stop_surface_form(surface_form)
    output_json[qid] = {'entities': output_entities, 'surface_tokens': output_surface_tokens}

with open('query-entities.json', 'w') as qef:
    json.dump(output_json, qef, sort_keys=True,
            indent=4, separators=(',', ': '))
