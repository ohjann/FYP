# Algorithmic Music Composer
Algorithmic music composition program based off David Cope's EMI. Done as part of my Final Year Project with TCD SCSS.

Sample output can be seen [here](http://ohjann.netsoc.ie/music/FYP).


##Usage

#### Clarifying database
For an entire directory:
	
	src/clarifyer/claryifydir.sh [DIRECTORY PATH]
For individual files:
	
	python3 src/clarifyer/transposer.py -f [PATH TO FILE]
	
#### Analysing database
For an entire directory:

	src/Analyse.sh
	
For individual files:

	python3 src/ScoreAnalyser.py -f [PATH TO FILE]

#### Splitting files
For an entire directory: 

	src/Split.sh
	
For individual files:

	python3 src/ScoreSplitter.py -f [PATH TO FILE]

#### Generating new composition
	python3 src/generate.py
	
Composition is then stored in `src/Composition.xml`

### Dependencies
- [lxml](http://lxml.de/)


####Note 
Code quality is poor as structure was very much done on a figure-out-as-I-go-along basis and certain features had to be crowbarred in close to project deadline with no time for adequate refactoring.
