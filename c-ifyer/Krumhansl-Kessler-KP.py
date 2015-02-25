# -*- coding: utf-8 -*-
"""

    Krumhansl-Schmuckler key-finding algorithm
    ... not reliable 

"""

import xml.dom.minidom
import copy
import sys
from functools import reduce
from collections import OrderedDict
from optparse import OptionParser
from itertools import cycle
from optparse import OptionParser

# Setup program flags and descriptions
parser = OptionParser()
parser.add_option("-f", "--file", action="store", dest="filename", help="specify file")
(options, args) = parser.parse_args()

if(options.filename):
    filename = options.filename
else:
    print("Usage: python3 Krumhansl-Kessler-KP.py -f [PATH TO FILE]")
    sys.exit()

noteVector = OrderedDict()  
noteVector["C"]  = 0
noteVector["C#"] = 0
noteVector["D"]  = 0
noteVector["D#"] = 0
noteVector["E"]  = 0
noteVector["E#"] = 0
noteVector["F"]  = 0
noteVector["F#"] = 0
noteVector["G"]  = 0
noteVector["G#"] = 0
noteVector["A"]  = 0
noteVector["A#"] = 0
noteVector["B"]  = 0
noteVector["B#"] = 0

#  Krumhansl-Kessler key profiles for C major
keyProfMaj = [ 6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
#  C minor
keyProfMin = [ 6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]

def kkProb(offset, avrg, noteVect, keyAvrg, keyProf):
    nv = cycle(noteVect)
    for i in range(0, offset):
        next(nv)
    x = 0
    y = 0
    top = 0
    for note in range(0, 12):
        nvt = next(nv)
        top += (nvt - avrg) * (keyProf[note] - keyAvrg)
        x += (nvt - avrg)**2
        y += (keyProf[note] - keyAvrg)**2

    return top / ((x * y)**0.5)
      

def assessKey(noteVector):
    # get average note occurance
    total = 0
    for note in noteVector:
        total += noteVector[note]

    average = float(total/len(noteVector))

    possibleKeys = [0] * 24
    noteOList = list()
    for note in noteVector:
        noteOList.append(noteVector[note])

    # iterate through scales to find which key is best matched
    notePointer = 0
    keyBase = -1

    kpmjAvrg = reduce(lambda x, y: x + y, keyProfMaj) / len(keyProfMaj)
    kpmiAvrg = reduce(lambda x, y: x + y, keyProfMin) / len(keyProfMin)

    for key in range(0,12):
        keyBase += 1
        possibleKeys[keyBase] = kkProb(keyBase, average, noteOList, kpmjAvrg, keyProfMaj)
        possibleKeys[keyBase+12] = kkProb(keyBase, average, noteOList, kpmiAvrg, keyProfMin)

    return possibleKeys

def getKey():
    DOMTree = xml.dom.minidom.parse(filename)
    collection = DOMTree.documentElement
    lastNote = 'q'
    # iterate through xml
    for attr in collection.getElementsByTagName('attributes'):
        for div in attr.getElementsByTagName('divisions'):
            # get what the 'scale' of the note duration is
            divisions = int(div.firstChild.data) 

    for notes in collection.getElementsByTagName('note'):
        for dur in notes.getElementsByTagName('duration'): 
            # add weighting to notes by duration
            duration = float(dur.firstChild.data)/divisions

        for pitch in notes.getElementsByTagName('pitch'):
            for child in pitch.childNodes:
                if(child.nodeType == 1):
                    if(child.nodeName == "step"):
                        note = child.firstChild.data
                        noteVector[note] += duration
                        lastNote = note

                    elif(child.nodeName == "alter"):
                        flatsharp = child.firstChild.data
                        noteVector[lastNote]-= duration
                        if(flatsharp == "-1"):
                            if(lastNote == "A"):
                                noteVector["G#"]+= duration
                            else:
                                lastNote = chr(ord(lastNote)-1) + '#'
                                noteVector[lastNote]+= duration
                        elif(flatsharp == "1"):
                            lastNote = lastNote + '#'
                            noteVector[lastNote]+= duration

    # delete equivalent notes
    noteVector["F"] += noteVector["E#"]
    noteVector["C"] += noteVector["B#"]
    del noteVector["E#"]
    del noteVector["B#"]

    keyProb = assessKey(noteVector)

    maxx = max(keyProb)
    maxindex = [i for i, j in enumerate(keyProb) if j == maxx]
    i=0
    for key, value in noteVector.items() :
        if(maxindex == [i]):
            return (key, "major")
        i+=1
    for key, value in noteVector.items() :
        if(maxindex == [i]):
            return (key, "minor")
        i+=1

if __name__ == '__main__':
    print("%s %s" % (getKey()))
