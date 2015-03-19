#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Eoghan Hynes <eoghan@hyn.es>
#
# Distributed under terms of the MIT license.

"""
    Program which iterates through MusicXML files by beat 
    addding <speac> element to each note as well as a 
    'beatnumber' attribute to allow for easier parsing
    
    MusicXML files must be in the key of C or A minor for this to work correctly.

"""

###
###
###     TODO:   pretty much just rewrite this whole file
###             - Account for time signature changes
###             - Account for single staves
###             - Fix last note beatnumber (not 100% necessary)
###             - Don't add speac element if already exists
###
###

import sys
import SPEACIDs
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

globalbeat = 1

def splitBeats(measure,divisions,beats,staves):
    """ Splits a measure into beats and returns a list
        of lists of notes in each beat
    :param measure: the MusicXML measure to be queried
    :type measure: xml.etree.ElementTree.Element
    :param divisions: what a each note needs to be divided by to get its 'real' duration
    :type divisions: int
    :param beats: number of beats in each measure
    :type beats: int
    :param staves: number of staves in each measure
    :type staves: int
    :returns: list of list of notes for each beat
    :rtype: list(list(str))
    """

    ###TODO: This function works but is not pretty at all, needs to be refactored a lot

    global globalbeat
    everynote = []
    # defaults
    notestr = (0,"") # [0] chord or not [1] note string TODO using a tuple here is very clumbsy
    staff = 1
    duration = 0

    ### Get details of every note in the measure
    #TODO: This should be made into a method to make it DRY
    for note in measure.findall("./note/"):

        if note.tag == "chord":
            notestr = (1,notestr[1])
        elif note.tag == "pitch":
            notestr = (notestr[0], note[0].text)
            if note[1].tag == "alter":
                if note[1].text == 1:
                    notestr[1] += "#"
                elif note[1].text == -1: 
                    if notestr[1] == "A":
                        notestr[1] == "G#"
                    else:
                        notestr = (notestr[0], chr(ord(notestr[1])-1)+"#")
                # remove duplicates
                if notestr[1] == "B#":
                    notestr = (notestr[0],"C")
                elif notestr[1] == "E#":
                    notestr = (notestr[0],"F")
            if note[1].tag == "octave":
                notestr = (notestr[0], notestr[1]+note[1].text)
            else:
                notestr = (notestr[0], notestr[1] + note[2].text)

        elif note.tag == "duration":
            duration = float(note.text)/divisions

        elif note.tag == "staff":
            staff = int(note.text)
            everynote.append((notestr, duration, staff,note))

    ### Split notes by beats
    beatlist = [[] for _ in range(beats) ]
    # variables to keep track of the current beat
    beatlength = 0.0
    currentbeat = 0
    clef = 1
    for note in everynote:
        if currentbeat > beats-1 or note[2] != clef:
            globalbeat -= currentbeat
            currentbeat = 0
            beatlength = 0
            clef = note[2]

        beatlist[currentbeat].append((note[0][1],note[1],note[-1]))
        note[-1].getparent().set('beatnumber',str(globalbeat))

        if everynote.index(note) != len(everynote) -1:
            nextnote = everynote[everynote.index(note) + 1]
            if nextnote[0][0] == 0: # i.e. not part of a chord
                beatlength += note[1]
        if beatlength >= 1:
            beatlength -= 1
            currentbeat += 1
            globalbeat += 1
    globalbeat += beats - currentbeat

    for beat in beatlist:
        if beat != []:
            notelist, noteduration, notexml = zip(*beat)
            SPEAC = SPEACIDs.getSPEAC(notelist,noteduration)
            if SPEAC == []:
                continue
            speacxml = ET.Element('speac')
            speacxml.text = " ".join(SPEAC)
            speacxml.tail = "\n\t   "
            for xml in notexml:
                xml.getparent().append(speacxml)

            tradIDs = SPEACIDs.getTrad(notelist, noteduration)
            tradxml = ET.Element('chordid')
            tradxml.text = " ".join(tradIDs)
            tradxml.tail = "\n\t   "
            for xml in notexml:
                xml.getparent().append(tradxml)

def clarifyDivisions(measure):
    duration = ET.Element("br")
    dotted = 1
    for note in measure.findall("./note/"):

        if note.findall("dot") != None:
            dotted = 2

        if note.tag == "duration":
            duration = note
        elif note.tag == "type":
            if note.text == "whole":
                duration.text = str(int(192 + 192/dotted))
                duration.set('updated','yes')
            elif note.text == "half":
                duration.text = str(int(96 + 96/dotted))
                duration.set('updated','yes')
            elif note.text == "quarter":
                duration.text = str(int(48 + 48/dotted))
                duration.set('updated','yes')
            elif note.text == "eighth":
                duration.text = str(int(24 + 24/dotted))
                duration.set('updated','yes')
            elif note.text == "16th":
                duration.text = str(int(12 + 12/dotted))
                duration.set('updated','yes')
            elif note.text == "32nd":
                duration.text = str(int(6 + 6/dotted))
                duration.set('updated','yes')
            elif note.text == "64th":
                duration.text = str(int(3 + 3/dotted))
                duration.set('updated','yes')
        dotted = 1


def parseFile(filename):
    tree = ET.parse(filename)
    measurelist = tree.findall("./part/measure")
    divisions = tree.find("./part/measure/attributes/divisions")
    beats = tree.findtext("./part/measure/attributes/time/beats")
    staves = tree.findtext("./part/measure/attributes/staves")
    if(staves != "2"):
        print("Program only supports files with 2 staves (i.e. piano)")
        sys.exit()
    for measure in measurelist:
        splitBeats(measure,int(divisions.text),int(beats),int(staves))
        clarifyDivisions(measure)

    divisions.text = "48"
    tree.write(filename,pretty_print=True)

if __name__ == '__main__':
    parseFile(filename)
