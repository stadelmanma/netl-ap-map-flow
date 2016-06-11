#!/bin/bash
# Building the flow model from source
cd ../source/
make
cd ../test/
#
mv ../APM-MODEL.EXE .
#
# testing it
./APM-MODEL.EXE fixtures/PARALELL-PLATE-01VOX_INIT.INP
#
#../bin/test
