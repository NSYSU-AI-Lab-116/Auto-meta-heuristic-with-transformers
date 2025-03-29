CXX	 := g++
CXXFLAGS := -Wall -O3
SRCS	 := main/main.cpp
LIBS	 := -lgmp -lgmpxx

OBJS	 := $(SRCS:.cpp=.o)
APP	 := search

all: $(APP)

$(APP): $(OBJS)
	$(CXX) -o $(APP) $(OBJS) $(LIBS)

$(OBJS): $(SRCS)

dep:
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -M $(SRCS) >.depend

clean:
	-rm -f $(APP) main/*.o .depend

sinclude .depend
