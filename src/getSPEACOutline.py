#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Eoghan Hynes <eoghan@hyn.es>
#
# Distributed under terms of the MIT license.

"""
    Uses a markov chain to get a SPEAC outline
    to aid recombination.
"""

import random
import sys
import os
import lxml.etree as ET
from optparse import OptionParser

# Setup program flags and descriptions
parser = OptionParser()
parser.add_option("-f", "--file", action="store", dest="filename", help="specify file")
(options, args) = parser.parse_args()

if(options.filename):
    filename = options.filename
else:
    print("Usage: python3 ScoreAnalyser.py -f [PATH TO FILE]")
    sys.exit()

class SPEACOutline:
    """ Markov generator for building a structure for
        recombination of SPEAC IDs 

        Based on: http://agiliq.com/blog/2009/06/generating-pseudo-random-text-with-markov-chains-u/
        """

    def __init__(self, dn):
        self.cache = {}
        self.dirname = dn
        self.outlines = self.getOutlines()
        self.outline_size = len(self.outlines)
        self.database()

    def getOutlines(self):
        """ get list of SPEAC outlines in a directory """
        filenames = os.listdir(self.dirname)
        outlinelist = []
        for f in filenames:
            outlinelist.append(self.getAnOutline(self.dirname+"/"+f))
        outlinelist = [x for x in outlinelist if x != []] # remove any empty ones
        return outlinelist

    def getAnOutline(self, fpath):
        """ get a single SPEAC outline from a file """
        speacoutline = ""
        tree = ET.parse(fpath)
        measurelist = tree.findall("./part/measure")
        for measure in measurelist:
            notelist = measure.findall("note/")
            for note in notelist:
                if note.tag == "speac":
                    speacoutline += " "+note.text[:2]
        return speacoutline.split()

   
    def triples(self):
        for outline in self.outlines:
            if len(outline) < 3:
                continue

            for i in range (len(outline) - 2):
                yield (outline[i], outline[i+1], outline[i+2])

    def database(self):
        for id1, id2, id3 in self.triples():
            key = (id1,id2)
            if key in self.cache:
                self.cache[key].append(id3)
            else:
                self.cache[key] = [id3]

    def generate_new(self, size=25):
        seed = random.randint(0, self.outline_size-3)
        ol1, ol2 = self.outlines[seed][0], self.outlines[seed+1][1]
        outline = []
        for i in range(size):
            outline.append(ol1)
            ol1,ol2 = ol2, random.choice(self.cache[(ol1,ol2)])

        outline.append(ol2)
        return " ".join(outline)

thing = SPEACOutline(filename)
print(thing.generate_new())
