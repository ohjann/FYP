import sys
import xml.etree.ElementTree as ET
from optparse import OptionParser

# Setup program flags and descriptions
parser = OptionParser()
parser.add_option("-f", "--file", action="store", dest="filename", help="specify file")
(options, args) = parser.parse_args()

if(options.filename):
    filename = options.filename
else:
    print("Usage: python3 splitter.py -f [PATH TO FILE]")
    sys.exit()

semitones = [   ("A",0),
                ("A#",1),
                ("B",2),
                ("C",3),
                ("C#",4),
                ("D",5),
                ("D#",6),
                ("E",7),
                ("F",8),
                ("F#",9),
                ("G",10),
                ("G#",11)
            ]

def sectionKeys(parts):
    ''' Sectioning pieces with changing key signature into different parts
        to be transposed individually.
        Parts with different keys stored in (DISTANCE FROM C, PART ELEMENT) tuple '''
    keylist = []
    for i in parts:
            attrlist = i.findall("./measure/attributes")
            for attr in attrlist:
                for key in attr:
                    if key.tag == "key":
                        keylist.append((key[0].text,i))
    # XXX: Fix note overflow!
    return keylist

def noteTrans(stringrep, alter, distance):
    semiTup = [i for i, v in enumerate(semitones) if v[0] == stringrep]
    semiTup = semiTup[0]+int(alter)
    trans = semiTup+int(distance)
    for tone in semitones:
        if tone[1] == trans:
            return tone[0]

    #print("semiTup: %d, distance: %d, alter: %d, trans: %d" % (semiTup[0],int(distance), int(alter),trans))
    #print("Ó %s go dtí %s" % (([v[0][0] for i,v in enumerate(semitones) if i == semiTup[0]]),([v[0][0] for i,v in enumerate(semitones) if i == trans])))
 
def transpose(parttuple):
    distance, part = parttuple
    for pitch in part.findall('./measure/note/pitch/'):
        alter = 0
        if(pitch.tag == "step"):
            note = pitch.text
        if(pitch.tag == "alter"):
            alter = int(pitch.text)

        newNote = noteTrans(note,alter,distance)
        if '#' in newNote:
            print(1)

if __name__ == '__main__':
    tree = ET.parse( filename )
    parts = tree.findall("./part")
    keylist = sectionKeys(parts)
    for part in keylist:
        transpose(part)
