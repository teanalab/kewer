#!/usr/bin/env sh
mkdir dbpedia-2016-10-kewer && cd dbpedia-2016-10-kewer || exit

mkdir graph && cd graph || exit
wget http://downloads.dbpedia.org/2016-10/core-i18n/en/infobox_properties_en.ttl.bz2
wget http://downloads.dbpedia.org/2016-10/core-i18n/en/mappingbased_literals_en.ttl.bz2
wget http://downloads.dbpedia.org/2016-10/core-i18n/en/mappingbased_objects_en.ttl.bz2
bunzip2 *.bz2
cd ..

mkdir labels && cd labels || exit
wget http://downloads.dbpedia.org/2016-10/core-i18n/en/anchor_text_en.ttl.bz2
wget http://downloads.dbpedia.org/2016-10/core-i18n/en/category_labels_en.ttl.bz2
wget http://downloads.dbpedia.org/2016-10/core-i18n/en/infobox_property_definitions_en.ttl.bz2
wget http://downloads.dbpedia.org/2016-10/core-i18n/en/labels_en.ttl.bz2
bunzip2 *.bz2
wget http://downloads.dbpedia.org/2016-10/dbpedia_2016-10.nt
cd ..

wget http://downloads.dbpedia.org/2016-10/core-i18n/en/article_categories_en.ttl.bz2
wget http://downloads.dbpedia.org/2016-10/core-i18n/en/short_abstracts_en.ttl.bz2
wget http://downloads.dbpedia.org/2016-10/core-i18n/en/transitive_redirects_en.ttl.bz2
bunzip2 *.bz2
