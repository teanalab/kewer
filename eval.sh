#!/usr/bin/env sh
galago eval --metrics+linndcg10 --metrics+linndcg100 --metrics+map --precision=4 --judgments=$1\
  --runs+bm25f/runs/all.all\
  --runs+word2vec/trecwebs-labels-nonorm-in-out-tw-noew-25.run\
  --runs+interpolation/folds-test-tw.run\
  --runs+interpolation-el/folds-test-smaph-tw-scores.run
