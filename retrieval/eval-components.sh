#!/usr/bin/env sh
galago eval --metrics+linndcg10 --metrics+linndcg100 --metrics+map --precision=4 --judgments=../qrels/qrels.txt --runs+ runs-10-0.9/nocat-nopred-nolit.run --runs+ runs-10-0.9/nocat-pred-nolit.run --runs+ runs-10-0.9/nocat-nopred-lit.run --runs+ runs-10-0.9/nocat-pred-lit.run --runs+ runs-10-0.9/cat-nopred-nolit.run --runs+ runs-10-0.9/cat-pred-nolit.run --runs+ runs-10-0.9/cat-nopred-lit.run --runs+ runs-10-0.9/cat-pred-lit.run
