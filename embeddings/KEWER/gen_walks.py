#!/usr/bin/env python3

import os
import random
import argparse
from collections import defaultdict
from datetime import datetime
import gc

parser = argparse.ArgumentParser()
parser.add_argument('--outfile', help='output file with walks', required=True)
parser.add_argument('--cat', help='process categories',
        default=False, action='store_true')
parser.add_argument('--length', help='length of walks', default=10, type=int)
parser.add_argument('--walks', help='walks per root', default=100, type=int)
args = parser.parse_args()

graph_path = os.path.join('data', 'graph.tsv')

outents = {}
outlits = {}

def process_node(subj, out_file):
    for _ in range(args.walks):
        walk = [subj]
        l = 1
        visited = {subj}
        obj = subj

        while obj in outents and l < args.length:
            pred, obj2 = random.choice(outents[obj])
            tried = set()
            while obj2 in visited:
                tried.add((pred, obj2))
                if len(tried) == len(outents[obj]):
                    break
                pred, obj2 = random.choice(outents[obj])
            else:
                obj = obj2
                walk.extend([pred, obj])
                l += 1
                visited.add(obj)
                continue
            break

        if obj in outlits:
            walk.extend(random.choice(outlits[obj]))

        print(*walk, sep='\t', file=out_file)

def main():
    random.seed(42)
    outents_set = defaultdict(set)
    outlits_set = defaultdict(set)
    i = 0
    with open(graph_path) as in_file:
        for line in in_file:
            subj, pred, obj = line.rstrip().split('\t')
            if obj.startswith('<') and (args.cat or pred != '<http://purl.org/dc/terms/subject>'):
                outents_set[subj].add((pred, obj))
                outents_set[obj].add((pred, subj))
            else:
                outlits_set[subj].add((pred, obj))
            i += 1
            if i % 10000000 == 0:
                print('Read {} lines'.format(i))


    start_nodes = []
    for subj, onodes in outents_set.items():
        outents[subj] = list(onodes)
        if not subj.startswith('<http://dbpedia.org/resource/Category:'):
            start_nodes.append(subj)
    del outents_set

    for subj, olits in outlits_set.items():
        outlits[subj] = list(olits)
    del outlits_set
    gc.collect()

    print('Total start nodes: {}. Current time: {}'.format(len(start_nodes), datetime.now().strftime('%H:%M:%S')))

    i = 0
    with open(args.outfile, 'w') as out_file:
        for subj in start_nodes:
            process_node(subj, out_file)
            i += 1
            if i % 100000 == 0:
                print('Processed {} nodes. Current time: {}'.format(i, datetime.now().strftime('%H:%M:%S')))

if __name__ == "__main__":
    main()
