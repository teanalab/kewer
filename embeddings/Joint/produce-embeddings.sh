#!/usr/bin/env sh

python convert.py
StarSpace-joint/starspace train -trainFile data/data.txt  -model data/model -trainMode 6 -fileFormat fastText -initRandSd 0.01 -adagrad true -ngrams 1 -lr 0.05 -dim 300 -negSearchLimit 5 -maxNegSamples 3 -dropoutRHS 0.8 -similarity "cosine" -minCount 5 -verbose true -normalizeText 0 -trainWord 1 -p 0 -label 'entity:' -relation 'relation:' -thread 30 -saveEveryEpoch 1
