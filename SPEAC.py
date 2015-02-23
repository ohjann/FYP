# -*- coding: utf-8 -*-
""" 

    Program to determine SPEAC identifier of given notes

"""
from collections import Counter

# List of SPEAC Identifier Tuples
SPEACLists = [  ( 'C1' , set([ "C2","C3","C4","C5","C6","C7","C8","C9","E2","E3","E4","E5","E6","E7","E8","G2","G3","G4","G5","G6","G7","G8" ]) ),
                ( 'P1' , set([ "F2","F3","F4","F5","F6","F7","F8","A2","A7","A8","A6","A3","A4","A5","C2","C3","C4","C5","C6","C7","C8","C9" ]) ),
                ( 'A1' , set([ "G2","G3","G4","G5","G6","G7","G8","B2","B3","B4","B5","B6","B7","B8","D2","D3","D4","D5","D6","D7","D8","F2","F3","F4","F5","F6","F7","F8" ]) ),
                ( 'A2' , set([ "B2","B3","B4","B5","B6","B7","B8","D2","D3","D4","D5","D6","D7","D8","F2","F3","F4","F5","F6","F7","F8" ]) ),
                ( 'C4' , set([ "E2","E3","E4","E5","E6","E7","E8","G2","G3","G4","G5","G6","G7","G8","B2","B3","B4","B5","B6","B7","B8" ]) ),
                ( 'P2' , set([ "D2","D3","D4","D5","D6","D7","D8","F7","F8","F6","F5","F2","F3","F4","A7","A8","A6","A5","A2","A3","A4" ]) ),
                ( 'C2' , set([ "A2","A3","A4","A5","A6","A7","A8","C2","C3","C4","C5","C6","C7","C8","C9","E2","E3","E4","E5","E6","E7","E8" ]) ),
                ( 'S1' , set([ "D2","D3","D4","D5","D6","D7","D8","D#3","A2","F#3","F#4","F#5","F#6","F#7","F#8","A3","A4","A5","A6","A7","A8" ]) ),
                ( 'S3' , set([ "E2","E3","E4","E5","E6","E7","E8","G#2","B2","G#3","G#4","G#5","G#6","G#7","G#8","B3","B4","B5","B6","B7","B8" ]) ),
                ( 'E1' , set([ "A2","A3","A4","A5","A6","A7","A8","C#2","C#3","C#4","C#5","C#6","C#7","C#8","E2","E3","E4","E5","E6","E7","E8" ]) ),
                ( 'E3' , set([ "B2","B3","A#4","B5","B6","B7","B8","D#2","D#3","D#4","D#5","D#6","D#7","D#8","F#2","F#3","F#4","F#5","F#6","F#7","F#8" ]) ),
                ( 'C3' , set([ "C2","C3","C4","C5","C6","C7","C8","C9","E2","G2","A#2","E3","E4","E5","E6","E7","E8","G3","G4","G5","G6","G7","G8","A#3","A#4","A#5","A#6","A#7","A#8" ]) ),
                ( 'E2' , set([ "C#2","C#3","C#4","C#5","C#6","C#7","C#8","E2","G2","A#2","E3","E4","E5","E6","E7","E8","G3","G4","G5","G6","G7","G8","A#3","A#4","A#5","A#6","A#7","A#8" ]) ),
                ( 'E4' , set([ "D#2","D#3","D#4","D#5","D#6","D#7","D#8","C2","F#2","A2","C3","C4","C5","C6","C7","C8","C9","F#3","F#4","F#5","F#6","F#7","F#8","A3","A4","A5","A6","A7","A8" ]) ),
                ( 'A3' , set([ "G#2","G#3","G#4","G#5","G#6","G#7","G#8","D2","F2","B2","D3","D4","D5","D6","D7","D8","F#3","F4","F5","F6","F7","F8","B3","B4","B5","B6","B7","B8" ]) ),
                ( 'P3' , set([ "G#2","G#3","G#4","G#5","G#6","G#7","G#8","C2","F#2","C3","E2","C5","C6","C7","C8","C9","F#3","F#4","F#5","F#6","F#7","F#8" ]) ),
                ( 'P4' , set([ "C#2","C#3","C#4","C#5","C#6","C#7","C#8","F2","G#2","F3","F4","F5","F6","F7","F8","G#3","G#4","G#5","G#6","G#7","G#8" ]) ),
                ( 'S4' , set([ "F#2","F#3","F#4","F#5","F#6","F#7","F#8","C#2","C#3","C#4","C#5","C#6","C#7","G#7","A#2","A#3","A#4","A#5","A#6,","A#7,","A#8" ]) ),
                ( 'A4' , set([ "D#2","D#3","D#4","D#5","D#6","D#7","D#8","G2","G3","G4","G5","G6","G7","G8","A#2","A#3","A#4","A#5","A#6","A#7","A#8" ]) ),
                ( 'S2' , set([ "A#2","A#3","A#4","A#5","A#6","A#7","A#8","D2","D3","D4","D5","D6","D7","D8","F2","F3","F4","F5","F6","F7","F8" ]) )
            ]

def getSPEAC(notes):

    ''' Compares passed notes to SPEAC identifiers.
    :param notes: list of notes in the form 'NOTE''OCTAVE' with no space between
    :type notes: list[str]
    :returns: list of SPEAC identifiers best matching passed notes
    :rtype: list[str]
    '''

    SPEACcount = [0] * len(SPEACLists)
    for i in range(0, len(SPEACLists)):
        for j in range(len(notes)):
            if notes[j] in SPEACLists[i][1]:
                SPEACcount[i] += 1
    m = max(SPEACcount)
    maximums = [i for i, j in enumerate(SPEACcount) if j == m]
    SPEACID = []
    for maxx in maximums:
        SPEACID.append(SPEACLists[maxx][0])
    return SPEACID

if __name__ == "__main__":
    temp = input("Enter list of notes in the form 'NOTE''OCTAVE' 'NOTE''OCTAVE' 'NOTE''OCTAVE' etc\n>")
    temp = temp.split()
    print(getSPEAC(temp))
