#
# defining variables
COMPILER = gfortran
OPTIMIZE = -O2
MODELNAME = APM-MODEL.EXE
RM = rm -f
RM_TEMP = find . -type f -name "*~" -delete

# filename variables
MODULES = STRING_MODULE.F APM_MODULE.F APM_SOLVER_MODULE.F UNIT_CONVERSION_MODULE.F PVT_MODULE.F
LINKED_MODULES = STRING_MODULE.o APM_MODULE.o APM_SOLVER_MODULE.o UNIT_CONVERSION_MODULE.o PVT_MODULE.o
MODELFILES = APERTURE_MAP_FLOW.F APM_SUBROUTINES.F APM_FLOW.F APM_SOLVER.F  APM_OUTPUT.F


# testing variables
LINKED_MODELFILES = APERTURE_MAP_FLOW.o APM_SUBROUTINES.o APM_FLOW.o APM_SOLVER.o  APM_OUTPUT.o
STRING_MOD_TEST = TEST_STRING_MOD.EXE UNIT_TEST_MODULE.o STRING_MODULE.o STRING_MODULE_UNIT_TEST.o
UNIT_CONV_MOD_TEST = TEST_UNIT_CONV_MOD.EXE UNIT_TEST_MODULE.o UNIT_CONVERSION_MODULE.o UNIT_CONVERSION_UNIT_TEST.o
APM_SUBS_TEST0 = TEST_APM_SUBROUTINES.EXE UNIT_TEST_MODULE.o STRING_MODULE.o APM_MODULE.o UNIT_CONVERSION_MODULE.o PVT_MODULE.o
APM_SUBS_TEST = $(APM_SUBS_TEST0) APM_SUBROUTINES_UNIT_TEST.o APM_SUBROUTINES.o

# compilation flag variables
WFLAGS = -Wall -Wline-truncation -Wcharacter-truncation -Wsurprising -Waliasing -Wunused-parameter
FFLAGS = -fimplicit-none -fwhole-file -fcheck=all -std=f2008 -pedantic -fbacktrace -cpp
TEST_FLAGS = -coverage -DUNITTESTING

# setting OS flag
ifdef SystemRoot
	OS = -DWIN64=1
else ifdef SYSTEMROOT
	OS = -DWIN64=1
else
	OS = -DWIN64=0
endif

# default action
all: modules model

modules:
	$(COMPILER) -c $(MODULES)

model: modules
	$(COMPILER) -o $(MODELNAME) $(LINKED_MODULES) $(MODELFILES) $(OPTIMIZE) $(FFLAGS) $(OS) $(WFLAGS)
	mv $(MODELNAME) ..

# test is only meant to be used when called by the run_model_coverage_test script
test: clean
	#
	# compiling link files for reuse in test drivers and model with test flags
	$(COMPILER) -c $(MODULES) $(FFLAGS) $(OS) $(WFLAGS) $(TEST_FLAGS)
	$(COMPILER) -c $(MODELFILES) $(FFLAGS) $(OS) $(WFLAGS) $(TEST_FLAGS)
	#
	# compiling test file links without test flags
	$(COMPILER) -c UNIT_TEST_MODULE.F $(FFLAGS) $(OS) $(WFLAGS)
	$(COMPILER) -c STRING_MODULE_UNIT_TEST.F $(FFLAGS) $(OS) $(WFLAGS)
	$(COMPILER) -c UNIT_CONVERSION_UNIT_TEST.F $(FFLAGS) $(OS) $(WFLAGS)
	$(COMPILER) -c APM_SUBROUTINES_UNIT_TEST.F $(FFLAGS) $(OS) $(WFLAGS)
	#
	# compiling model and unit test driver programs
	$(COMPILER) -o $(MODELNAME) $(LINKED_MODULES) $(LINKED_MODELFILES) $(FFLAGS) $(OS) $(WFLAGS) $(TEST_FLAGS)
	$(COMPILER) -o $(STRING_MOD_TEST) $(FFLAGS) $(OS) $(WFLAGS) $(TEST_FLAGS)
	$(COMPILER) -o $(UNIT_CONV_MOD_TEST) $(FFLAGS) $(OS) $(WFLAGS) $(TEST_FLAGS)
	$(COMPILER) -o $(APM_SUBS_TEST) $(FFLAGS) $(OS) $(WFLAGS) $(TEST_FLAGS)

coverage:
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
