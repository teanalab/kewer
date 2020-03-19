#!/usr/bin/env python3

import logging
import os.path
import sys
import argparse
import multiprocessing

from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence

parser = argparse.ArgumentParser()
parser.add_argument('--infile', help='input file with sentences', required=True)
parser.add_argument('--outfiles', help='output file prefix with embeddings', required=True)
parser.add_argument('--size', help='embedding dimension', default=300, type=int)
parser.add_argument('--workers', help='number of threads', default=multiprocessing.cpu_count(), type=int)
parser.add_argument('--window', help='window size', default=5, type=int)
args = parser.parse_args()

if __name__ == '__main__':
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)

    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
    logging.root.setLevel(level=logging.INFO)

    model = Word2Vec(LineSentence(args.infile), size=args.size, window=args.window, min_count=5, sg=1,
                     workers=args.workers)

    # trim unneeded model memory = use(much) less RAM
    # model.init_sims(replace=True)
    model.save(args.outfiles + '.bin')
    model.wv.save_word2vec_format(args.outfiles + '.text', binary=False)
