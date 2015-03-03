#!/bin/bash

SCRIPTPATH=$(dirname "$0")

for f in $SCRIPTPATH/../data/clarified-scores/*.xml;
do
    echo "Processing $f file..."
    python3 $SCRIPTPATH/ScoreSplitter.py -f "$f"
done
