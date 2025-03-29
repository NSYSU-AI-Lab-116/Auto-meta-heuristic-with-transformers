# Generic makefile: requires GNU make

DIRS  = 1-onemax 1-onemax/standalone 2-deception

all:
	for i in $(DIRS); do make -C $${i} all; done

dep:
	for i in $(DIRS); do make -C $${i} dep; done

clean:
	for i in $(DIRS); do make -C $${i} clean; done
