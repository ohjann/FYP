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
    return keylist

def noteTrans(stringrep, alter, distance):
    ''' Transposes individual notes by passed distance, returns note
        in a (new note, alter, octave change) tuple where octave change is
        the change in octave necessary when transposing '''
    semiTup = [i for i, v in enumerate(semitones) if v[0] == stringrep]
    semiTup = semiTup[0]+int(alter)
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


           #XXX DOESNT WORK WHY DOESNT IT WORK
 
def transpose(parttuple):
    distance, part = parttuple
    #print(distance)
    for pitch in part.findall('./measure/note/pitch/'):
        alterint = 0
        if(pitch.tag == "step"):
            note = pitch
            notestring = note.text
        if(pitch.tag == "octave"):
            octave = pitch
        if(pitch.tag == "alter"):
            alter = pitch
            alterint = int(pitch.text)
        newNote, alterchange, octavechange = noteTrans(notestring,alterint,distance)

        # update values
        note.text = newNote[0]
        note.set('updated', 'yes')
        if 'alter' in locals():
            alter.text = str(alterchange)
            alter.set('updated', 'yes')
        if octavechange != 0 and octave.attrib == {}:
            #print(octave.attrib)
            octave.text = str(int(octave.text)+octavechange)
            octave.set('updated', 'yes')
    for fifth in part.findall('./measure/attributes/key/fifths'):
        fifth.text = "0"
        fifth.set('updated', 'yes')

if __name__ == '__main__':
    tree = ET.parse( filename )
    parts = tree.findall("./part")
    keylist = sectionKeys(parts)
    for part in keylist:
        transpose(part)
    tree.write("output.xml")
