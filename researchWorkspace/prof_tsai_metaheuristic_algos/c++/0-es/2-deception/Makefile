CXX	 := g++
CXXFLAGS := -Wall -O3
SRCS	 := es_main.cpp es_search.cpp
LIBS	 := -lgmp

OBJS	 := $(SRCS:.cpp=.o)
APP	 := es

all: $(APP)

$(APP): $(OBJS)
	$(CXX) -o $(APP) $(OBJS) $(LIBS)

$(OBJS): $(SRCS)

dep:
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -M $(SRCS) >.depend

clean:
	rm -f $(APP) *.o .depend

sinclude .depend
