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


class Outline:
    """ Markov generator for building a structure for
        recombination of beats 

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
        """ get a single (SPEAC,chord) outline from a file """
        speacoutline = []
        tree = ET.parse(fpath)
        measurelist = tree.findall("./part/measure")
        for measure in measurelist:
            notelist = measure.findall("note/")
            speac = ""
            chord = ""
            for note in notelist:
                if note.tag == "speac":
                    if not note.text == None:
                        speac = note.text.split()[0]
                elif note.tag == "chordid":
                    chord = note.text.split()[0]
                if len(speac) and len(chord):
                    speacoutline.append((speac,chord))
                    speac = ""
                    chord = ""
        return speacoutline
   
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

    def testProgression(self, current, candidate):
        chord1 = current[1]
        chord2 = candidate[1]

        if chord1 == "I":
            return True

        elif chord1 == "II":
            if chord2 == "V" or chord2 == "VII" or chord2 == "II":
                return True

        elif chord1 == "III":
            if chord2 == "IV" or chord2 == "VI" or chord2 == "III":
                return True

        elif chord1 == "IV":
            if chord2 == "II" or chord2 == "V" or chord2 == "VII" or chord2 == "I" or chord2 == "IV":
                return True

        elif chord1 == "V":
            if chord2 == "VII" or chord2 == "VI" or chord2 == "I" or chord2 == "V":
                return True

        elif chord1 == "VI":
            if chord2 == "IV" or chord2 == "II" or chord2 == "VI":
                return True

        elif chord1 == "VII":
            if chord2 == "VI" or chord2 == "I" or chord2 == "V" or chord2 == "VII":
                return True

        return False

    def generate_new(self, size=24):
        seed = random.randint(0, self.outline_size-3)
        ol1, ol2 = self.outlines[seed][0], self.outlines[seed+1][1]
        outline = []
        outline.append(ol1)
        attempts = 0 # if it can't find a good progression just choose a random one
        while len(outline) < size: # get minimum size 
            choice = random.choice(self.cache[(ol1,ol2)])
            attempts += 1
            if self.testProgression(ol2,choice) or attempts > 30:
                ol1,ol2 = ol2, choice
                outline.append(ol1)
                attempts = 0
        outline.append(ol2)
        while not(ol2[1] == "I" and (ol1[1] == "IV" or ol1[1] == "V" or ol1[1] == "VII")): # get cadence
            choice = random.choice(self.cache[(ol1,ol2)])
            attempts += 1
            if self.testProgression(ol2,choice) or attempts > 30:
                ol1,ol2 = ol2, choice
                outline.append(ol1)
                attempts = 0
        outline.append(ol2)
        return outline

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
    for beat in fourbeats:
        for note in beat:
            print("Note: ",note)
            measure.append(note)
    print()
    part.append(measure)

def jigsaw(beats,outline):
    bdict = dict(beats)
    del bdict['dirname']
    mxlskeleton = ET.parse("mxl-skeleton.xml")
    measure = []
    for ID in outline:
        #print(ID[0],bdict[ID[0]])
        beat = random.choice(bdict[ID[0]])
        if len(beat): # XXX why is this happening
            measure.append(beat)
        #print(ET.tostring(beat), len(beat))

        if len(measure)>=4 :
           print("adding")
           addToPiece(measure,mxlskeleton)
           measure = []
    return mxlskeleton

def generate():
    pwd = os.path.dirname(os.path.realpath(__file__))
    speacdir = pwd + "/../data/SPEAC"
    sheetdir = pwd + "/../data/clarified-scores"

    outline = Outline(sheetdir)
    speacStructure = outline.generate_new(72)
    beats = speacBeats(speacdir)

    gen_piece = jigsaw(beats,speacStructure)
    if os.path.isfile("composition.xml"):
        os.remove("composition.xml")
    gen_piece.write("composition.xml")

if __name__ == '__main__':
    generate()
