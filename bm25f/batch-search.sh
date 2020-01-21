#!/usr/bin/env bash

COLS=(INEX_LD ListSearch QALD2 SemSearch_ES)

shopt -s globstar
for out in weights/*/*.out; do
  tail -1 $out > ${out%.out}.json
done

parallel galago batch-search --index=index\
  --queries=../queries/{1}-{2}-test.tsv --queryFormat=tsv\
  weights/{1}-{2}/default.json\
  --operatorWrap=bm25f traversals-config.json fields.json\
  --outputFile=runs/{1}-{2}.run ::: ${COLS[@]} :::: <(seq 0 4)

cat runs/*.run > runs/all.all
