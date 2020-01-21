cmake_minimum_required(VERSION 3.10)
project(StarSpace)

set(CMAKE_CXX_STANDARD 11)

include_directories(src)
include_directories(src/utils)

add_executable(StarSpace
        src/apps/embed_doc.cpp
        src/apps/print_ngrams.cpp
        src/apps/query_nn.cpp
        src/apps/query_predict.cpp
        src/test/matrix_test.cpp
        src/test/proj_test.cpp
        src/utils/args.cpp
        src/utils/args.h
        src/utils/normalize.cpp
        src/utils/normalize.h
        src/utils/utils.cpp
        src/utils/utils.h
        src/data.cpp
        src/data.h
        src/dict.cpp
        src/dict.h
        src/doc_data.cpp
        src/doc_data.h
        src/doc_parser.cpp
        src/doc_parser.h
        src/main.cpp
        src/matrix.h
        src/model.cpp
        src/model.h
        src/parser.cpp
        src/parser.h
        src/proj.cpp
        src/proj.h
        src/starspace.cpp
        src/starspace.h)
