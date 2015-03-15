# -*- coding: utf-8 -*-
""" 

    Transposes a MusicXML file in .xml format to the key of C

"""

import sys
import os
import xml.etree.ElementTree as ET
from optparse import OptionParser

# Setup program flags and descriptions
parser = OptionParser()
parser.add_option("-f", "--file", action="store", dest="filename", help="specify file")
(options, args) = parser.parse_args()

if(options.filename):
    filename = options.filename
else:
    print("Usage: python3 transposer.py -f [PATH TO FILE]")
    sys.exit()

semitones = [   ("C",0),
                ("C#",1),
                ("D",2),
                ("D#",3),
                ("E",4),
                ("F",5),
                ("F#",6),
                ("G",7),
                ("G#",8),
                ("A",9),
                ("A#",10),
                ("B",11)
            ]

def queryKey(measure):
    """Finds if there is a key change in the given MusicXML measure
       returning the new key and changing that key to C (i.e. 0).
    :param measure: the MusicXML measure to be queried
    :type measure: xml.etree.ElementTree.Element
    :returns: 'x' if there is no key change otherwise returns the key
    :rtype: str
    """
    measurekey = 'x'
    for child in measure:
        for attr in child:
            if attr.tag == "key":
                measurekey = attr[0].text
                attr[0].text = '0'
                attr[0].set('updated', 'yes')
    return measurekey

def noteTrans(stringrep, alter, numflatsharps):
    """ Transposes individual notes by passed numflatsharps
    :param stringrep: string representation of the note to be transposed
    :type stringrep: str
    :param alter: int -1, 0, or 1 depending on flat, natural or sharp respectively
    :type alter: int
    :param numflatsharps: the numflatsharps from C which the note needs to be transposed by
    :type numflatsharps: str or int
    :returns: tuple with three values corresponding to (the new transposed note, any alter necessary, any octave change necessary)
    :rtype: (str,int,int)
    """
    #print("Args: stringrep: %s, alter: %d, numflatsharps: %s" % (stringrep, alter, numflatsharps))
    semiTup = [i for i, v in enumerate(semitones) if v[0] == stringrep]
    semiTup = semiTup[0]+int(alter)

    distance = (int(numflatsharps)*5)%12 # circle of fifths for flats

    if distance > 6:
        distance = distance - 12 # transpose to nearest, avoid huge jumps
    #print("FlatSharp: %s, distance to transpose: %d" % (numflatsharps,distance))

    trans = semiTup+int(distance)
    octave = 0
    if(trans>11):
        trans = trans%12
        octave = 1
    elif(trans<0):
        trans = trans+12
        octave = -1
    for tone in semitones:
        if tone[1] == trans:
            if(len(tone[0])>1):
                return (tone[0], 1, octave)
            else:
                return (tone[0], 0, octave)
 
def transpose(measure, numflatsharps):
    """ Transposes MusicXML measure by numflatsharps
    :param measure: MusicXML measure which is to be transposed
    :type measure: xml.etree.ElementTree.Element
    :param numflatsharps: string, the numflatsharps from C which the note needs to be transposed by
    :type numflatsharps: str or int
    """
    #print(measure.attrib)
    for note in measure.findall('./note'):
        index = -1
        if(note[0].tag == "pitch"):
            index = 0
        elif (note[0].tag == "chord"):
            index = 1
        if index != -1 :
            alterint = 0
            step = note[index][0]
            stepstring = step.text
            
            if(note[index][1].tag == "alter"):
                alter = note[index][1]
                alterint = int(alter.text)
                octave = note[index][2]
            else:
                octave = note[index][1]

            newNote, alterchange, octavechange = noteTrans(stepstring,alterint,numflatsharps)
            #print("Returned: newNote: %s, alterchange: %d, octavechange: %d\n" % (newNote, alterchange, octavechange))

            # update values
            step.text = newNote[0]
            step.set('updated', 'yes')
            del step
            if 'alter' in locals():
                alter.text = str(alterchange)
                alter.set('updated', 'yes')
                del alter
            else:
                alter = ET.Element('alter')
                alter.text = str(alterchange)
                alter.set('updated', 'yes')
                alter.tail = "\n\t\t  "
                note[index].insert(1,alter)
                del alter
            if 'octave' in locals():
                if octavechange != 0 and octave.attrib == {}:
                    octave.text = str(int(octave.text)+octavechange)
                    octave.set('updated', 'yes')
                del octave # deleting to avoid weird variable mixups

def removeExcess(measure):
    """ Removes "notations" from MusicXML because it causes wacky sheet music upon recombination 
    :param measure: MusicXML measure which is to be transposed
    :type measure: xml.etree.ElementTree.Element
    """
    for notes in measure.findall("note"):
        for child in notes:
            if child.tag == "notations":
                notes.remove(child)

if __name__ == '__main__':
    tree = ET.parse( filename )
    measurelist = tree.findall("./part/measure")
    key = '0'
    for measure in measurelist:
        tmpkey = queryKey(measure)
        if tmpkey != 'x':
            #print("key change!")
            key = tmpkey
        if key == '0':
            # measure alread in C
            continue
        transpose(measure,key)
        removeExcess(measure)

    #directory = os.path.dirname(os.path.realpath(filename))+"/c-versions/"
    directory = os.path.join(os.path.realpath(os.path.dirname(__file__)), os.pardir)+"/../data/clarified-scores/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    print("Storing transposed file in %s..." % (directory))
    tree.write(directory+os.path.basename(filename))
