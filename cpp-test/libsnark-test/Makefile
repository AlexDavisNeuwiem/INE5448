# Compiler and flags
CXX = g++
CXXFLAGS = -std=c++17 -O2 -I/usr/local/include -Iinclude
LDFLAGS = -L/usr/local/lib -lsnark -lsnark_adsnark -libff -lgmp -lgmpxx -lcrypto -lpthread

# Sources
SRC_DIRS = src
SRCS = main.cpp $(wildcard $(SRC_DIRS)/*.cpp)

# Build directory
BUILD_DIR = build
OBJS = $(SRCS:.cpp=.o)
OBJS := $(patsubst %,$(BUILD_DIR)/%,$(OBJS))

# Output
TARGET = main

# Default rule
all: $(TARGET)

# Linking
$(TARGET): $(OBJS)
	$(CXX) -o $@ $^ $(LDFLAGS)

# Compiling
$(BUILD_DIR)/%.o: %.cpp
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Cleaning
clean:
	rm -rf $(BUILD_DIR) $(TARGET)

.PHONY: all clean
