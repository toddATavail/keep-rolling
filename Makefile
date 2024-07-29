# Makefile for screen_selection project

# Compiler and flags
SWIFTC = swiftc
SWIFTC_FLAGS = -O

# Targets
all: screen_selection

screen_selection: screen_selection.swift
	$(SWIFTC) $(SWIFTC_FLAGS) -o $@ $<

lint:
	pylint keep_rolling.py

clean:
	rm -f screen_selection

.PHONY: all lint run_keep_rolling clean
