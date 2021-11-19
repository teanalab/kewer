#!/usr/bin/env sh
commented=$(mktemp)
labeled=$(mktemp)
grep -h ' <http://www.w3.org/2000/01/rdf-schema#comment> ' ./dbpedia-2021-06-kewer/short-abstracts_lang=en.ttl | cut -f1 -d' ' | sort > "$commented"
grep -h ' <http://www.w3.org/2000/01/rdf-schema#label> ' ./dbpedia-2021-06-kewer/labels/labels_lang=en.ttl | cut -f1 -d' ' | sort > "$labeled"
comm -12 "$commented" "$labeled" > indexed
rm "$commented" "$labeled"
