#!/bin/bash

SCRIPTPATH=$(dirname "$0")

for f in $SCRIPTPATH/../data/clarified-scores/*.xml;
do
    echo "Processing $f file..."
    python3 $SCRIPTPATH/ScoreAnalyser.py -f "$f"
done
