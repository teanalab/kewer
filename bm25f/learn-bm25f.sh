#!/usr/bin/env bash

COLS=(INEX_LD ListSearch QALD2 SemSearch_ES)
parallel galago learner --index=index --qrels=../qrels.txt\
  --queries=../queries/{1}-{2}-train.tsv --queryFormat=tsv\
  --operatorWrap=bm25f traversals-config.json fields.json\
  --output=weights/{1}-{2}\
  learn-bm25f.json --metric=linndcg10 --name=default ::: ${COLS[@]} :::: <(seq 0 4)
