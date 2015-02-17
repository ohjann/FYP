import xml.dom.minidom
from findkey import getKey
from optparse import OptionParser

# Setup program flags and descriptions
parser = OptionParser()
parser.add_option("-f", "--file", action="store", dest="filename", help="specify file")
(options, args) = parser.parse_args()

if(options.filename):
    filename = options.filename
else:
    print("Usage: python3 parser.py -f [PATH TO FILE]")
    sys.exit()

distance = {    "A" : 3,
                "A#": 2,
                "B" : 1,
                "C#":-1,
                "D" :-2,
                "D#":-3,
                "E" :-4,
                "F" :-5,
                "G" : 5,
                "G#": 4
                }

def distanceFromC(key):
    if(key == "C"): return


def main():
    key, majmin = getKey(filename)
    print ("Key of %s %s" % (key, majmin))
    distanceFromC(key)

main()
