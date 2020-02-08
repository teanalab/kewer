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