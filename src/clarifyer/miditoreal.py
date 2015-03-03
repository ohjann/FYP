# -*- coding: utf-8 -*-
"""

    Quick 'n' Dirty  program for converting midi notes to real ones

"""

midi = input("Enter midi notes: ")
midi = midi.split()

for mid in midi:

    note = int(mid)
    if(note%12 == 0):
        print("C %d," % (note/12), end=" ")
    elif(note%12 == 1):
        print("C# %d," % (note/12), end=" ")
    elif(note%12 == 2):
        print("D %d," % (note/12), end=" ")
    elif(note%12 == 3):
        print("D# %d," % (note/12), end=" ")
    elif(note%12 == 4):
        print("E %d," % (note/12), end=" ")
    elif(note%12 == 5):
        print("F %d," % (note/12), end=" ")
    elif(note%12 == 6):
        print("F# %d," % (note/12), end=" ")
    elif(note%12 == 7):
        print("G %d," % (note/12), end=" ")
    elif(note%12 == 8):
        print("G# %d," % (note/12), end=" ")
    elif(note%12 == 9):
        print("A %d," % (note/12), end=" ")
    elif(note%12 == 10):
        print("A# %d," % (note/12), end=" ")
    elif(note%12 == 11):
        print("B %d," % (note/12), end=" ")
    else:
        print("What.")
print()
