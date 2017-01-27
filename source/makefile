#
# defining variables
CC = gfortran
OPTIMIZE ?= -O3
MODELNAME ?= APM-MODEL.EXE
OBJDIR = dist/
RM = rm -rf
.DEFAULT_GOAL:= $(OBJDIR)$(MODELNAME)

# setting OS flag
OS = -DWIN64=0
ifdef SystemRoot
	OS = -DWIN64=1
else ifdef SYSTEMROOT
	OS = -DWIN64=1
endif

# hard coded file source orders to handle dependencies
MODULE_FILES = STRING_MODULE.F  \
	APM_MODULE.F \
	APM_SOLVER_MODULE.F \
	UNIT_CONVERSION_MODULE.F \

TEST_FILES = UNIT_TEST_MODULE.F \
	STRING_MODULE_UNIT_TEST.F \
	UNIT_CONVERSION_UNIT_TEST.F \
	APM_SUBROUTINES_UNIT_TEST.F


# testing variables
UNIT_TEST_OBJ = UNIT_TEST_MODULE.o
STRING_MOD_TEST = TEST_STRING_MOD.EXE $(UNIT_TEST_OBJ) STRING_MODULE.o STRING_MODULE_UNIT_TEST.o
UNIT_CONV_MOD_TEST = TEST_UNIT_CONV_MOD.EXE $(UNIT_TEST_OBJ)  UNIT_CONVERSION_MODULE.o UNIT_CONVERSION_UNIT_TEST.o
APM_SUBS_TEST = TEST_APM_SUBROUTINES.EXE $(UNIT_TEST_OBJ) $(MODULE_OBJS) APM_SUBROUTINES_UNIT_TEST.o APM_SUBROUTINES.o


#
# setting variables
SRC_FILES := $(wildcard *.F)
OBJ_FILES = $(addprefix $(OBJDIR), $(SRC_FILES:.F=.o))
MOD_OBJS = $(addprefix $(OBJDIR), $(MODULE_FILES:.F=.o))

#
# determining flags to apply at compile time based on target
FLAGS = $(OPTIMIZE) $(OS) -J$(OBJDIR)
debug test: FLAGS = -fimplicit-none -fwhole-file -fcheck=all -std=f2008 -pedantic -fbacktrace -cpp
debug test: FLAGS += -Wall -Wline-truncation -Wcharacter-truncation -Wsurprising -Waliasing -Wunused-parameter
debug test: FLAGS += $(OS) -J$(OBJDIR)
test: TEST_FLAGS = -coverage -DUNITTESTING

${OBJDIR}:
	mkdir -p $(OBJDIR)

${OBJDIR}%.o : %.F | ${OBJDIR}
	$(CC) -c $(FLAGS) $(TEST_FLAGS) -o $@ $< 


${OBJDIR}${MODELNAME}: ${MOD_OBJS} ${OBJ_FILES}
	$(CC) $(FLAGS) $^ -o $@

debug: clean ${OBJDIR}${MODELNAME}

clean:
	$(RM) $(OBJDIR) *.o *.mod *.EXE *.gcno *.gcda *.gcov

#
# actual bulid targets
#debug: modules
#	$(COMPILER) -o $(MODELNAME) $(MODULE_OBJS) $(MODEL_FILES) QUIT.F $(FLAGS)
#
#modules:
#	$(COMPILER) -c $(MODULES) $(FLAGS) $(TEST_FLAGS)
#
#model_files: 
#	$(COMPILER) -c $(MODEL_FILES) $(FLAGS) $(TEST_FLAGS)
#
# test is only meant to be used when called by the run_model_coverage_test script
#test: clean modules model_files
#	#
#	# compiling unit/integration test file links without test flags
#	$(COMPILER) -c $(TEST_FILES) $(FLAGS)
#	#
#	# compiling model and unit test driver programs
#	$(COMPILER) -o $(MODELNAME) $(MODULE_OBJS) $(MODEL_FILE_OBJS) $(FLAGS) $(TEST_FLAGS)
#	$(COMPILER) -o $(STRING_MOD_TEST) $(FLAGS) $(TEST_FLAGS)
#	$(COMPILER) -o $(UNIT_CONV_MOD_TEST) $(FLAGS) $(TEST_FLAGS)
#	$(COMPILER) -o $(APM_SUBS_TEST) $(FLAGS) $(TEST_FLAGS)
#
#coverage:
#	gcov *.F
#
#all: modules
#	$(COMPILER) -o $(MODELNAME) $(MODULE_OBJS) $(MODEL_FILES) $(FLAGS)

