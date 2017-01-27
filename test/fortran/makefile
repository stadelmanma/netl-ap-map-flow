include model_makefile


# defining variables
TESTSRC = src/
TEST_FLAGS = -coverage -DUNITTESTING


# list used to do initial compilation of test framework objects
TEST_FILES = UNIT_TEST_MODULE.F \
       STRING_MODULE_UNIT_TEST.F \
       UNIT_CONVERSION_UNIT_TEST.F \
       APM_SUBROUTINES_UNIT_TEST.F
TEST_OBJS = $(addprefix $(OBJDIR), $(TEST_FILES:.F=.o))


# defining test file lists for each unit test
STRING_MOD_TEST_FILES =  STRING_MODULE_UNIT_TEST.F \
	UNIT_TEST_MODULE.F \
	STRING_MODULE.F
STRING_MOD_TEST_OBJS  = $(addprefix $(OBJDIR), $(STRING_MOD_TEST_FILES:.F=.o))

UNIT_CONV_TEST_FILES = UNIT_CONVERSION_UNIT_TEST.F \
	UNIT_TEST_MODULE.F \
	UNIT_CONVERSION_MODULE.F
UNIT_CONV_TEST_OBJS = $(addprefix $(OBJDIR), $(UNIT_CONV_TEST_FILES:.F=.o))

APM_SUBS_TEST_FILES = APM_SUBROUTINES_UNIT_TEST.F \
	UNIT_TEST_MODULE.F \
	APM_SUBROUTINES.F
APM_SUBS_TEST_OBJS = $(addprefix $(OBJDIR), $(APM_SUBS_TEST_FILES:.F=.o))


# compiles test specific files without test flags to avoid unwanted coverage data
${OBJDIR}%.o : ${TESTSRC}%.F | ${OBJDIR}
	$(CC) -c $(FLAGS) -o $@ $< 

test_string: ${STRING_MOD_TEST_OBJS}
	$(CC) -o TEST_STRING_MOD.EXE $(STRING_MOD_TEST_OBJS) $(FLAGS) $(TEST_FLAGS)

test_unit_conv: ${UNIT_CONV_TEST_OBJS}
	$(CC) -o TEST_UNIT_CONV_MOD.EXE.EXE $(UNIT_CONV_TEST_OBJS) $(FLAGS) $(TEST_FLAGS)

test_apm_subs: ${MODULE_OBJS} ${APM_SUBS_TEST_OBJS}
	$(CC) -o TEST_APM_SUBROUTINES.EXE ${MODULE_OBJS} $(APM_SUBS_TEST_OBJS) $(FLAGS) $(TEST_FLAGS)

unit_tests: test_string test_unit_conv test_apm_subs

test: clean ${MODULE_OBJS} ${TEST_OBJS} ${OBJDIR}${MODELNAME} unit_tests
	mv ${OBJDIR}${MODELNAME} .






# testing variables
#UNIT_TEST_OBJ = UNIT_TEST_MODULE.o
#STRING_MOD_TEST = TEST_STRING_MOD.EXE $(UNIT_TEST_OBJ) STRING_MODULE.o STRING_MODULE_UNIT_TEST.o
#UNIT_CONV_MOD_TEST = TEST_UNIT_CONV_MOD.EXE $(UNIT_TEST_OBJ)  UNIT_CONVERSION_MODULE.o UNIT_CONVERSION_UNIT_TEST.o
#APM_SUBS_TEST = TEST_APM_SUBROUTINES.EXE $(UNIT_TEST_OBJ) $(MODULE_OBJS) APM_SUBROUTINES_UNIT_TEST.o APM_SUBROUTINES.o
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

