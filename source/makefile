#
# defining variables
COMPILER = gfortran
OPTIMIZE = -O2
MODELNAME = APM-MODEL.EXE
#
# normal compilation variables
MODULES = STRING_MODULE.F APM_MODULE.F APM_SOLVER_MODULE.F UNIT_CONVERSION_MODULE.F PVT_MODULE.F
SHAREDFILES = APM_SUBROUTINES.F APM_SOLVER.F
MODELFILES = APERTURE_MAP_FLOW.F APM_FLOW.F APM_OUTPUT.F
#
# testing variables
STRING_MOD_TEST = TEST_STRING_MOD.EXE UNIT_TEST_MODULE.F STRING_MODULE.F STRING_MODULE_UNIT_TEST.F
UNIT_CONV_MOD_TEST = TEST_UNIT_CONV_MOD.EXE UNIT_TEST_MODULE.F UNIT_CONVERSION_MODULE.F UNIT_CONVERSION_UNIT_TEST.F
#
WFLAGS = -Wall -Wline-truncation -Wcharacter-truncation -Wsurprising -Waliasing -Wunused-parameter
FFLAGS = -fimplicit-none -fwhole-file -fcheck=all -std=f2008 -pedantic -fbacktrace -cpp
TEST  = -fprofile-arcs -ftest-coverage
#
ifdef SystemRoot
	RM = del /Q
	RM_TEMP = del /Q *~
	OS = -DWIN64=1
else ifdef SYSTEMROOT
	RM = del /Q
	RM_TEMP = del /Q *~
	OS = -DWIN64=1
else
	RM = rm -f
	RM_TEMP = find . -type f -name "*~" -delete
	OS = -DWIN64=0
endif
#
# hardcoding for now it since make cant seem to access windows commands only bash commands
RM = rm -f
RM_TEMP = find . -type f -name "*~" -delete
#
# This will compile the entire program and it's modules
all: modules model

modules:
	$(COMPILER) -c $(MODULES)

model: modules
	$(COMPILER) -o $(MODELNAME) $(MODULES) $(SHAREDFILES) $(MODELFILES) $(OPTIMIZE) $(FFLAGS) $(OS) $(WFLAGS)
	mv $(MODELNAME) ..

test: clean modules
	# test is only meant to be used when called by the run_model_coverage_test script
	$(COMPILER) -c UNIT_TEST_MODULE.F
	$(COMPILER) -o $(MODELNAME) $(MODULES)  $(SHAREDFILES) $(MODELFILES) $(FFLAGS) $(OS) $(WFLAGS) -coverage
	$(COMPILER) -o $(STRING_MOD_TEST)  $(FFLAGS) $(OS) $(WFLAGS) -coverage
	$(COMPILER) -o $(UNIT_CONV_MOD_TEST) $(FFLAGS) $(OS) $(WFLAGS) -coverage


coverage:
	$(RM) *UNIT_TEST*
	gcov *.F

clean:
	$(RM) *.o
	$(RM) *.mod
	$(RM) *.EXE
	$(RM) *.gcno
	$(RM) *.gcda
	$(RM) *.gcov
	#
	cd ..; $(RM_TEMP)
