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
        dirnames = os.listdir(self.dirname)
        outlinelist = []
        for f in dirnames:
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

    def generate_new(self, size=24):
        seed = random.randint(0, self.outline_size-3)
        ol1, ol2 = self.outlines[seed][0], self.outlines[seed+1][1]
        outline = []
        for i in range(size):
            outline.append(ol1)
            ol1,ol2 = ol2, random.choice(self.cache[(ol1,ol2)])

        outline.append(ol2)
        return " ".join(outline)

class speacBeats:

    def __init__(self,dirname):

        self.dirname = dirname

        self.A1 = self.getBeats("A1")
        self.A2 = self.getBeats("A2")
        self.A3 = self.getBeats("A3")
        self.A4 = self.getBeats("A4")

        self.C1 = self.getBeats("C1")
        self.C2 = self.getBeats("C2")
        self.C3 = self.getBeats("C3")
        self.C4 = self.getBeats("C4")

        self.E1 = self.getBeats("E1")
        self.E2 = self.getBeats("E2")
        self.E3 = self.getBeats("E3")
        self.E4 = self.getBeats("E4")

        self.P1 = self.getBeats("P1")
        self.P2 = self.getBeats("P2")
        self.P3 = self.getBeats("P3")
        self.P4 = self.getBeats("P4")

        self.S1 = self.getBeats("S1")
        self.S2 = self.getBeats("S2")
        self.S3 = self.getBeats("S3")
        self.S4 = self.getBeats("S4")


    def getBeats(self,SPEAC):
        tree = ET.parse(self.dirname+"/"+SPEAC+".xml")
        return tree.findall("beat")
    
    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value
            
globalmeasure = 1
def addToPiece(fourbeats,mxl):
    global globalmeasure 
    globalmeasure += 1
    part = mxl.find("./part")
    measure = ET.Element("measure")
    measure.set("number",str(globalmeasure))
    #barline = ET.fromstring('<barline location="right"><bar-style>light-heavy</bar-style><repeat direction="backward"/></barline>')
    for beat in fourbeats:
        notes = beat.findall("note")
        for note in notes:
            measure.append(note)
    #        measure.append(barline)
    part.append(measure)

def jigsaw(beats,outline):
    bdict = dict(beats)
    del bdict['dirname']
    mxlskeleton = ET.parse("mxl-skeleton.xml")
    measure = []
    for ID in outline.split():
        beat = random.choice(bdict[ID])
        measure.append(beat)

        if len(measure)>=4 :
           addToPiece(measure,mxlskeleton)
           measure = []
    return mxlskeleton

def generate():
    pwd = os.path.dirname(os.path.realpath(__file__))
    speacdir = pwd + "/../data/SPEAC"
    sheetdir = pwd + "/../data/clarified-scores"

    outline = SPEACOutline(sheetdir)
    speacStructure = outline.generate_new(72)
    beats = speacBeats(speacdir)

    gen_piece = jigsaw(beats,speacStructure)
    gen_piece.write("composition.xml")

if __name__ == '__main__':
    generate()
