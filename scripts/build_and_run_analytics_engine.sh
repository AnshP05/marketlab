#!/bin/bash
set -e

cd "$(dirname "$0")/.."
mkdir -p build/analytics
# Compiling using clang and its relavant options. Only compiling so we can link later. First file is the
clang++ -std=c++17 -Wall -Wextra -Wpedantic -c analytics/aggregate.cpp -o build/analytics/aggregate.o
ar rcs build/analytics/libmarketlab_analytics.a build/analytics/aggregate.o
clang++ -std=c++17 -Wall -Wextra -Wpedantic analytics/main.cpp build/analytics/libmarketlab_analytics.a -o build/analytics/main
./build/analytics/main
