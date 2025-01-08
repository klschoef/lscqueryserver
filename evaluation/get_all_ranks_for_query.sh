#!/usr/bin/env bash

# This script is used to get all ranks of all results (of results folder) for a query

echo "Usage: ./get_all_ranks_for_query.sh <query_id>"

# iterate through all json files in results folder
for file in results/*.json
do
     echo "Processing $file"
    python3 get_rank_for_query.py $file $1 --latex_output true
done

