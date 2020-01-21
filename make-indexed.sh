#!/usr/bin/env sh
grep -h ' <http://www.w3.org/2000/01/rdf-schema#comment> ' ./dbpedia-2015-10-nolinks/* | cut -f1 -d' ' | sort > /tmp/commented
grep -h ' <http://www.w3.org/2000/01/rdf-schema#label> ' ./dbpedia-2015-10-nolinks/* | cut -f1 -d' ' | sort > /tmp/labelled
comm -12 /tmp/commented /tmp/labelled > indexed
