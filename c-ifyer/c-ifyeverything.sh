#!/bin/bash

# bash script for transposing an entire directory of MusicXML
# files using transpose.py

for f in $PWD/$@*.xml;
do
    echo "Processing $f file..."
    python3 transposer.py -f "$f"
done
