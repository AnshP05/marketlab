#!/bin/bash
set -e

#Navigate to the correct directory
cd "$(dirname "$0")/../latency_stats"

#Compiling our pogram
g++ latency_stats.cpp -o latency_stats

#Running our program
./latency_stats "$1"