#!/bin/bash
# Building the flow model from source
cd ../source/
make
cd ../tests/
mv ../APM-MODEL.EXE .
./APM-MODEL.EXE PARALELL-PLATE-01VOX_INIT.INP
#
# running python test scripts
PYCMD="python3";
command -v $PYCMD >/dev/null 2>&1 || {
    PYCMD="python";
}
$PYCMD test_module.py
$SHELL