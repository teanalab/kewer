galago eval --metrics+linndcg10 --metrics+linndcg100 --metrics+map --precision=4 --judgments=../qrels/qrels.txt\
  --runs+runs-10-0.9/cat-pred-lit.run\
  --runs+runs-el/spotlight.run\
  --runs+runs-el/smaph.run\
  --runs+runs-el/nordlys.run
