SRC = Launcher.cpp Ray.cpp Globals.cpp main.cpp GeometryHelper.cpp IOHelper.cpp
SRCE = mainEdges.cpp GeometryHelper.cpp Globals.cpp IOHelper.cpp
CLFLAGS = -std=c++0x

build: clean launcher edges #ann

launcher:
	g++ -g -o launcher $(SRC) $(CLFLAGS)

edges: 
	g++ -g -o edges $(SRCE) $(CLFLAGS)
	
	
SRCA = ANNtest.cpp
CANNFLAGS = -std=c++0x -O3
ANNBASEDIR = ../ann_1.1.2
ANNINCDIR = $(ANNBASEDIR)/include
ANNLIBDIR = $(ANNBASEDIR)/lib
ANNLDFLAGS= -lANN
	
# if compiling 'ann' fails, run >make annlib< and try again
ann: 
	g++ -g -o anntest $(SRCA) -I$(ANNINCDIR) -L$(ANNLIBDIR) $(ANNLDFLAGS) $(CANNFLAGS)
	
annlib:
	cd $(ANNBASEDIR); $(MAKE) linux-g++ 

	
clean: clauncher cedges #cann
	
clauncher:
	rm -f launcher
cedges:
	rm -f edges
cann:
	rm -f anntest
