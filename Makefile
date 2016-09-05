SHELL := /bin/bash

all:
	./sswag.py

local:	all
	pushd html && python3 -m http.server 8000; popd

clean: 
	rm -rf html/
	rm -rf __pycache__

.PHONY: all local clean

