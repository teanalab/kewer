The repository contains code and data for ECIR 2020 paper "Joint Word and Entity Embeddings for Entity Retrieval from Knowledge Graph".

KEWER embeddings trained on categories, literals, predicates structural components and unigram probabilities are available here: https://academictorrents.com/details/4778f904ca10f059eaaf27bdd61f7f7fc93abc6e.

## Download Dataset

To download the dataset, which is a subset of English [DBpedia 2015-10](https://wiki.dbpedia.org/dbpedia-dataset-version-2015-10), simply run `make-dataset.sh` script.
Verify that it produced the following files and directories in `dbpedia-2015-10-kewer` directory:

```bash
$ tree --dirsfirst dbpedia-2015-10-kewer
dbpedia-2015-10-kewer
├── graph
│   ├── infobox_properties_en.ttl
│   ├── mappingbased_literals_en.ttl
│   └── mappingbased_objects_en.ttl
├── labels
│   ├── anchor_text_en.ttl
│   ├── category_labels_en.ttl
│   ├── dbpedia_2015-10.nt
│   ├── infobox_property_definitions_en.ttl
│   └── labels_en.ttl
├── article_categories_en.ttl
├── short_abstracts_en.ttl
└── transitive_redirects_en.ttl

2 directories, 11 files
```

## Train KEWER embeddings

1. Generate `indexed` file with the filtered entities: `make-indexed.sh`.
2. Install required packages:
```shell script
$ conda create --name kewer --file requirements.txt
$ conda activate kewer
```
2. Train embeddings:
```shell script
$ cd embeddings/KEWER
$ ./gen_graph.py
$ ./gen_walks.py --cat --outfile data/walks-cat.txt
$ ./replace_uris.py --pred --lit --infile data/walks-cat.txt --outfile data/sents-cat-pred-lit.txt
# optional - shuffle sentences: $ shuf data/sents-cat-pred-lit.txt -o data/sents-cat-pred-lit.txt
$ ./train_w2v.py --infile data/sents-cat-pred-lit.txt --outfiles data/kewer
```