#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Eoghan Hynes <eoghan@hyn.es>
#
# Distributed under terms of the MIT license.

"""
    Composes piece using Genetic Algorithms
"""

import os
import time
import copy
import random
import lxml.etree as ET

class genetic:

    def __init__(self,dirname,crossoverRate,mutateRate):
        self.chromosomes = [self.Chromosome(chromo) \
                for chromolist in self.getChromo(dirname) \
                for chromo in chromolist] # get array of chromosome objects
        self.crRate = crossoverRate
        self.muRate = mutateRate

    class Chromosome():
        def __init__(self, beat=None, fitness=999.0):
            self.beat = beat
            self.fitness = fitness

    def getChromo(self, dirname):
        """ get each beat as chromosome """
        filenames = os.listdir(dirname)
        chromolist = []
        for f in filenames:
            fpath = dirname+"/"+f
            tree = ET.parse(fpath)
            beat = tree.findall("./beat")
            chromolist.append(beat)
        return chromolist
    
    def pitchMedian(self, beat):
        """ gets median pitch of current beat returning an integer 
            and ignoring sharps (because it doesn't need to be that accurate)"""
        notes = (beat.findall("./note/pitch/step"), beat.findall("./note/pitch/octave"))
        if notes == ([],[]):
            return 1
        notelist = []
        for note,octave in zip(*notes):
            nnum = ord(note.text)-64 # not 65 to avoid dividing by zero
            noct = int(octave.text) * 12
            notelist.append(nnum+noct)
        if len(notelist) %2 == 0:
            one = notelist[int(len(notelist)/2)]
            two = notelist[int((len(notelist)/2)-1)]
            return int((one + two)/2)
        else:
            return notelist[int(len(notelist)/2)]

    def lengthAvg(self, beat):
        """ gets average length of notes in a beat """
        notelength = beat.findall("./note/duration")
        if notelength == []:
            return -1
        totallength = 0
        for length in notelength:
            totallength += int(length.text)
        return int(totallength / len(notelength))

    def countNotes(self, beat):
        """ counts notes in a beat """
        notes = beat.findall("./note")
        return len(notes)

    def checkFitness(self, currbeatdetails, beat):
        """ Fitness function
        :param currbeatdetails: tuple with (pitch median, average length, number of notes) of current beat
        :type currbeatdetails: (int, int, int)
        """
        pitch = self.pitchMedian(beat)
        length = self.lengthAvg(beat)
        notecount = self.countNotes(beat)

        cpitch, clength, cnotecount = currbeatdetails

        fitp = abs((cpitch/pitch) - 1)
        fitl = abs((clength/length) - 1)
        fitc = abs((notecount/cnotecount) - 1)

        fittotal = fitp + fitl + fitc
        return fittotal

    def Roulette(self, totalFitness, Population):

        Slice = random.random() * totalFitness
        fitnessSoFar = 0

        for chromo in Population:
            fitnessSoFar += chromo.fitness

            if(fitnessSoFar >= Slice):
                return chromo.beat
        return None

    def mutate(self, beat):
        """ mutate a beat by + or - one note """
        if random.random() < self.muRate:
            notes = beat.findall("./note")
            if notes == []:
                return beat
            munote = random.choice(notes) # choose a random note

            plusminus = ["plus", "minus"]
            choice = random.choice(plusminus)

            step = munote.find("pitch/step")
            if choice == "plus":
                if step.text == "G":
                    step.text = "A"
                else:
                    step.text = chr(ord(step.text)+1) 
            else:
                if step.text == "A":
                    step.text = "G"
                else:
                    step.text = chr(ord(step.text)-1) 
        return beat


    def crossover(self, mammybeat, daddybeat):
        """ crossover two parent beats by swapping bass and treble clef notes 
            and also chopping those notes"""

        if random.random() < self.crRate:

            mammy = mammybeat.findall("./")
            mammynotes = [[],[]] # [[treble notes + backup],[bass notes]]
            bass = 0
            for elem in mammy:
                mammynotes[bass].append(elem)
                if elem.tag == "backup":
                    bass = 1

            daddy = daddybeat.findall("./")
            daddynotes = [[],[]]
            bass = 0
            for elem in daddy:
                daddynotes[bass].append(elem)
                if elem.tag == "backup":
                    bass = 1

            child1 = ET.Element("beat")
            child2 = ET.Element("beat")

            # slice treble notes
            if len(daddynotes[0]) > len(mammynotes[0]):
                slicer = random.randint(0,len(mammynotes[0]))
                treble1 = mammynotes[0][0:slicer] \
                        + daddynotes[0][slicer:len(daddynotes)-1]
                treble2 = daddynotes[0][0:slicer] \
                        + mammynotes[0][slicer:len(mammynotes)-1]
            else:
                slicer = random.randint(0,len(daddynotes[0]))
                treble1 = daddynotes[0][0:slicer] \
                        + mammynotes[0][slicer:len(mammynotes)-1]
                treble2 = mammynotes[0][0:slicer] \
                        + daddynotes[0][slicer:len(daddynotes)-1]

            # slice bass notes
            if len(daddynotes[1]) > len(mammynotes[1]):
                slicer = random.randint(0,len(mammynotes[1]))
                bass1 = mammynotes[1][0:slicer] \
                        + daddynotes[1][slicer:len(daddynotes)-1]
                bass2 = daddynotes[1][0:slicer] \
                        + mammynotes[1][slicer:len(mammynotes)-1]
            else:
                slicer = random.randint(0,len(daddynotes[1]))
                bass1 = daddynotes[1][0:slicer] \
                        + mammynotes[1][slicer:len(mammynotes)-1]
                bass2 = mammynotes[1][0:slicer] \
                        + daddynotes[1][slicer:len(daddynotes)-1]


            for t in treble1:
                child1.append(t)
            for b in bass1:
                child1.append(b)

            for t in treble2:
                child2.append(t)
            for b in bass2:
                child2.append(b)

            return (child1, child2)

        else: 
            return (mammybeat, daddybeat)

    def checkChord (self, beat1, beat2):
        """ checks that both beats are of the same chord """
        try:
            beat1 = beat1.find("./note/chordid").text.split()[0]
            beat2 = beat2.find("./note/chordid").text.split()[0]
        except:
            return False
        
        if beat1 == beat2:
            return True
        else:
            return False

    def getBeat(self, testbeat, minfit):
        """ use genetic algorithms to get a suitable beat """

        generations = 1
        fitness = 9999
        beatdetails = (self.pitchMedian(testbeat), self.lengthAvg(testbeat), self.countNotes(testbeat))

        while fitness > minfit:
            print("\033[92mGeneration {0}, closest match: {1}\033[0m".format(generations,fitness))
            print("number of chromosomes: ",len(self.chromosomes))
            totalFitness = 0
            for chromosome in self.chromosomes:
                chromosome.fitness = self.checkFitness(beatdetails, chromosome.beat)
                totalFitness += chromosome.fitness

                if chromosome.fitness < minfit:
                    # doesn't have to be best match just good enough
                    print("Match found! Fitness: ",chromosome.fitness)
                    return chromosome.beat

            self.chromosomes.sort(key=lambda x:x.fitness) 
            fitness = self.chromosomes[0].fitness
            bestmatch = ET.tostring(self.chromosomes[0].beat)
            #print("Best so far:\n",bestmatch.decode())

            newGen = []
            # XXX: Elitism required


            Ravg = []
            Cavg = []
            Mavg = []
            Wavg = []
            for i in range(int(len(self.chromosomes)/2)):
                startTime = time.time()
                offspring1 = self.Roulette(totalFitness, self.chromosomes)
                elapsedTime = time.time() - startTime
                Ravg.append(elapsedTime)

                startTime = time.time()
                offspring2 = self.Roulette(totalFitness, self.chromosomes)
                elapsedTime = time.time() - startTime
                Ravg.append(elapsedTime)
                print("Generating child number ",i*2,end="\r")
                wstartTime = time.time()
                while not self.checkChord (offspring1, offspring2):
                    # ensure parents are the same chord
                    startTime = time.time()
                    offspring1 = self.Roulette(totalFitness, self.chromosomes)
                    elapsedTime = time.time() - startTime
                    Ravg.append(elapsedTime)

                    startTime = time.time()
                    offspring2 = self.Roulette(totalFitness, self.chromosomes)
                    elapsedTime = time.time() - startTime
                    Ravg.append(elapsedTime)
                elapsedTime = time.time() - wstartTime
                Wavg.append(elapsedTime)

                startTime = time.time()
                offspring1, offspring2 = self.crossover(offspring1,offspring2)
                elapsedTime = time.time() - startTime
                Cavg.append(elapsedTime)

                startTime = time.time()
                offspring1 = self.mutate(offspring1)
                elapsedTime = time.time() - startTime
                Mavg.append(elapsedTime)
                startTime = time.time()
                offspring2 = self.mutate(offspring2)
                elapsedTime = time.time() - startTime
                Mavg.append(elapsedTime)

                newGen.append(self.Chromosome(offspring1))
                newGen.append(self.Chromosome(offspring2))

            r = 0
            for x in Ravg:
                r += x
            print("\033[93mRoulette average time: ",(r/len(Ravg)),"\033[0m")
            r = 0
            for x in Cavg:
                r += x
            print("\033[93mCrossover average time: ",(r/len(Cavg)),"\033[0m")
            for x in Mavg:
                r += x
            print("\033[93mMutate average time: ",(r/len(Mavg)),"\033[0m\n")
            for x in Wavg:
                r += x
            print("\033[93mWhile loop average time: ",(r/len(Wavg)),"\033[0m\n")
            self.chromomes = None
            self.chromosomes = copy.deepcopy(newGen)
            del newGen

            generations += 1
            if generations > 30:
                print("no matching beat found")
                break

        return self.chromosomes[0].beat


#################################################
#################################################
###########   Testing the Class   ###############
#################################################
#################################################

pwd = os.path.dirname(os.path.realpath(__file__))
gen = genetic((pwd + "/../data/SPEAC"),0.7,0.0)
# beat1 = A0 B0     beat2 = E3 G3
beat1 = ET.fromstring('<beat><note color="#000000" default-x="150" default-y="-17" beatnumber="7"><pitch><step updated="yes">A</step><alter updated="yes">0</alter><octave>0</octave></pitch><duration updated="yes">36</duration><instrument id="P1-I1"/><voice>1</voice><type>eighth</type><stem>up</stem><staff>1</staff><beam number="1">begin</beam></note><note color="#000000" default-x="185" default-y="-17" beatnumber="7"><pitch><step updated="yes">B</step><alter updated="yes">0</alter><octave updated="yes">0</octave></pitch><duration updated="yes">36</duration><instrument id="P1-I1"/> <voice>1</voice> <type>eighth</type> <stem>up</stem> <staff>1</staff> <beam number="1">continue</beam> <speac>C1 C4 C3 E2</speac> <chordid>I III</chordid> </note> </beat>')
beat2 = ET.fromstring('<beat><note color="#000000" default-x="150" default-y="-17" beatnumber="7"><pitch><step updated="yes">E</step><alter updated="yes">0</alter><octave>3</octave></pitch><duration updated="yes">36</duration><instrument id="P1-I1"/><voice>1</voice><type>eighth</type><stem>up</stem><staff>1</staff><beam number="1">begin</beam></note><note color="#000000" default-x="185" default-y="-17" beatnumber="7"><pitch><step updated="yes">G</step><alter updated="yes">0</alter><octave updated="yes">3</octave></pitch><duration updated="yes">36</duration><instrument id="P1-I1"/> <voice>1</voice> <type>eighth</type> <stem>up</stem> <staff>1</staff> <beam number="1">continue</beam> <speac>C1 C4 C3 E2</speac> <chordid>I III</chordid> </note> </beat>')
#child = gen.checkFitness((40,36,2),beat1)

child = gen.getBeat(beat1,0.5)
print(ET.tostring(child).decode())
