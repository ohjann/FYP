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

def sectionKeys(measure):
    measurekey = 'x'
    for child in measure:
        for attr in child:
            if attr.tag == "key":
                measurekey = attr[0].text
                attr[0].text = '0'
                attr[0].set('updated', 'yes')
    return measurekey

def noteTrans(stringrep, alter, distance):
    ''' Transposes individual notes by passed distance, returns note
        in a (new note, alter, octave change) tuple where octave change is
        the change in octave necessary when transposing '''
    #print("Args: stringrep: %s, alter: %d, distance: %s" % (stringrep, alter, distance))
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
 
def transpose(measure, distance):
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

            newNote, alterchange, octavechange = noteTrans(stepstring,alterint,distance)
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

if __name__ == '__main__':
    tree = ET.parse( filename )
    measurelist = tree.findall("./part/measure")
    key = '0'
    for measure in measurelist:
        tmpkey = sectionKeys(measure)
        if tmpkey != 'x':
            #print("key change!")
            key = tmpkey
        if key == '0':
            # measure alread in C
            continue
        transpose(measure,key)

    tree.write("output.xml")
