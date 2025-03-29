# Generic makefile: requires GNU make

DIRS  = 0-es 1-onemax 2-deception 3-tsp 4-function 5-eval 6-clustering

all:
	for i in $(DIRS); do make -C $${i} all; done

dep:
	for i in $(DIRS); do make -C $${i} dep; done

clean:
	for i in $(DIRS); do make -C $${i} clean; done

run:
	./do_all.sh
