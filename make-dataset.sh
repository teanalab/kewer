#!/usr/bin/env sh
mkdir dbpedia-2021-06-kewer && cd dbpedia-2021-06-kewer || exit

mkdir graph && cd graph || exit
wget https://databus.dbpedia.org/dbpedia/generic/infobox-properties/2021.06.01/infobox-properties_lang=en.ttl.bz2
wget https://databus.dbpedia.org/dbpedia/mappings/mappingbased-literals/2021.06.01/mappingbased-literals_lang=en.ttl.bz2
wget https://databus.dbpedia.org/dbpedia/mappings/mappingbased-objects/2021.06.01/mappingbased-objects_lang=en.ttl.bz2
bunzip2 *.bz2
cd ..

mkdir labels && cd labels || exit
wget https://databus.dbpedia.org/dbpedia/generic/anchor-text/2021.06.01/anchor-text_lang=en.ttl.bz2
wget https://databus.dbpedia.org/dbpedia/generic/categories/2021.06.01/categories_lang=en_labels.ttl.bz2
wget https://databus.dbpedia.org/dbpedia/generic/infobox-property-definitions/2021.06.01/infobox-property-definitions_lang=en.ttl.bz2
wget https://databus.dbpedia.org/dbpedia/generic/labels/2021.06.01/labels_lang=en.ttl.bz2
bunzip2 *.bz2
wget https://databus.dbpedia.org/ontologies/dbpedia.org/ontology--DEV/2021.07.09-070001/ontology--DEV_type=parsed.nt
cd ..

wget https://databus.dbpedia.org/dbpedia/generic/categories/2021.06.01/categories_lang=en_articles.ttl.bz2
wget https://databus.dbpedia.org/dbpedia/text/short-abstracts/2021.06.01/short-abstracts_lang=en.ttl.bz2
wget https://databus.dbpedia.org/dbpedia/generic/redirects/2021.06.01/redirects_lang=en_transitive.ttl.bz2
bunzip2 *.bz2
