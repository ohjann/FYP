#!/bin/bash

# bash script for transposing an entire directory of MusicXML
# files using transpose.py

SCRIPTPATH=$(dirname "$0")

for f in $PWD/$@*.xml;
do
    echo "Processing $f file..."
    echo $SCRIPTPATH"/"
    python3 $SCRIPTPATH/transposer.py -f "$f"
done
