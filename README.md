# KEWER: Knowledge graph Entity and Word Embedding for Retrieval

[![Dancing KEWER](https://i.imgur.com/HnIBZXn.png)](https://youtu.be/AGvGldtbJSU)

The repository contains code and data for ECIR 2020 paper "Joint Word and Entity Embeddings for Entity Retrieval from Knowledge Graph" \[[pdf](https://link.springer.com/content/pdf/10.1007%2F978-3-030-45439-5_10.pdf), [slides](https://www.slideshare.net/FedorNikolaev/joint-word-and-entity-embeddings-for-entity-retrieval-from-knowledge-graph), [presentation](https://youtu.be/TK4F0GjLKRc?t=26769)\].

KEWER embeddings trained on categories, literals, predicates structural components and unigram probabilities are available here: https://academictorrents.com/details/4778f904ca10f059eaaf27bdd61f7f7fc93abc6e.

## Entity Retrieval example

KEWER allows to significantly improve entity retrieval for complex queries. Below are the top 10 results for the query "wonders of the ancient world" obtained using BM25F and KEWER. Relevant results are *italicized*, and highly relevant results are **boldfaced**.

| BM25F                                           | KEWER                                        |
|-------------------------------------------------|----------------------------------------------|
| **Seven Wonders of the Ancient World**          | **Colossus of Rhodes**                       |
| *7 Wonders of the Ancient World (video game)*   | **Statue of Zeus at Olympia**                |
| *Wonders of the World*                          | **Temple of Artemis**                        |
| *Seven Ancient Wonders*                         | List of archaeoastronomical sites by country |
| The Seven Fabulous Wonders                      | **Hanging Gardens of Babylon**               |
| The Seven Wonders of the World (album)          | Antikythera mechanism                        |
| Times of India's list of seven wonders of India | Timeline of ancient history                  |
| *Lighthouse of Alexandria*                      | *Wonders of the World*                       |
| 7 Wonders (board game)                          | *Lighthouse of Alexandria*                   |
| Colossus of Rhodes                              | **Great Pyramid of Giza**                    |

## Download dataset

To download the dataset, which is a subset of [DBpedia Snapshot 2021-06](https://www.dbpedia.org/blog/snapshot-2021-06-release/), simply run `make-dataset.sh` script.
Verify that it produced the following files and directories in `dbpedia-2021-06-kewer` directory:

```bash
$ tree --dirsfirst dbpedia-2021-06-kewer
dbpedia-2021-06-kewer
├── graph
│   ├── infobox-properties_lang=en.ttl
│   ├── mappingbased-literals_lang=en.ttl
│   └── mappingbased-objects_lang=en.ttl
├── labels
│   ├── anchor-text_lang=en.ttl
│   ├── categories_lang=en_labels.ttl
│   ├── infobox-property-definitions_lang=en.ttl
│   ├── labels_lang=en.ttl
│   └── ontology--DEV_type=parsed.nt
├── categories_lang=en_articles.ttl
├── redirects_lang=en_transitive.ttl
└── short-abstracts_lang=en.ttl

2 directories, 11 files
```

## Train KEWER embeddings

1. Generate `indexed` file with the filtered entities: `make-indexed.sh`.
2. Install required packages:
```shell script
$ conda env create -f environment.yml
$ conda activate kewer-2021-06
```
2. Train embeddings:
```shell script
$ cd embeddings/KEWER
$ ./gen_graph.py
$ ./gen_walks.py --cat --outfile data/walks-cat.txt
$ ./replace_uris.py --pred --lit --infile data/walks-cat.txt --outfile data/sents-cat-pred-lit.txt
$ shuf data/sents-cat-pred-lit.txt -o data/sents-cat-pred-lit.txt.shuf
$ ./train_w2v.py --infile data/sents-cat-pred-lit.txt.shuf --outfiles data/kewer
```

## Cite

```
@InProceedings{Nikolaev:2020:KEWER,
  author="Nikolaev, Fedor and Kotov, Alexander",
  title="Joint Word and Entity Embeddings for Entity Retrieval from a Knowledge Graph",
  booktitle="Advances in Information Retrieval",
  year="2020",
  publisher="Springer International Publishing",
  address="Cham",
  pages="141--155",
  isbn="978-3-030-45439-5"
}
```

## Contact

If you have any questions or suggestions, send an email to fedor@wayne.edu or [create a GitHub issue](https://github.com/teanalab/kewer/issues/new).
