#!/usr/bin/env sh
galago eval --metrics+linndcg10 --metrics+linndcg100 --metrics+map --precision=4 --judgments=../qrels/qrels.txt --runs+ joint-tw/joint.run --runs+ joint-tw/joint-el.run --runs+ joint-tw/joint-el-smaph.run --runs+ joint-tw/joint-el-ltr.run --runs+ joint-tw/joint-sf.run --runs+ joint-tw/joint-sf-el.run --runs+ joint-tw/joint-sf-el-smaph.run --runs+ joint-tw/joint-sf-el-ltr.run
