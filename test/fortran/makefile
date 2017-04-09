include model_makefile


# defining variables
TESTSRC = src/
TEST_FLAGS = -coverage -DUNITTESTING
TEST_BIN = bin
override TEST_BIN := $(strip $(TEST_BIN))/


# list used to do initial compilation of test framework objects
TEST_FILES = UNIT_TEST_MODULE.F \
       STRING_MODULE_UNIT_TEST.F \
       UNIT_CONVERSION_UNIT_TEST.F \
       IO_MODULE_UNIT_TEST.F
TEST_OBJS = $(addprefix $(OBJDIR), $(TEST_FILES:.F=.o))


# defining test file lists for each unit test
STRING_MOD_TEST_FILES =  STRING_MODULE_UNIT_TEST.F \
	UNIT_TEST_MODULE.F \
	STRING_MODULE.F
STRING_MOD_TEST_OBJS  = $(addprefix $(OBJDIR), $(STRING_MOD_TEST_FILES:.F=.o))

UNIT_CONV_TEST_FILES = UNIT_CONVERSION_UNIT_TEST.F \
	UNIT_TEST_MODULE.F \
	STRING_MODULE.F \
	UNIT_CONVERSION_MODULE.F
UNIT_CONV_TEST_OBJS = $(addprefix $(OBJDIR), $(UNIT_CONV_TEST_FILES:.F=.o))

IO_MOD_TEST_FILES = IO_MODULE_UNIT_TEST.F \
	UNIT_TEST_MODULE.F
IO_MOD_TEST_OBJS = $(addprefix $(OBJDIR), $(IO_MOD_TEST_FILES:.F=.o))


# compiles test specific files without test flags to avoid unwanted coverage data
${OBJDIR}%.o : ${TESTSRC}%.F | ${OBJDIR}
	$(FC) -c $(BUILD_FLAGS) $(FFLAGS) -o $@ $<

test_string: ${STRING_MOD_TEST_OBJS}
	$(FC) -o $(TEST_BIN)TEST_STRING_MOD.EXE $(STRING_MOD_TEST_OBJS) $(BUILD_FLAGS) $(LDFLAGS) $(FFLAGS) $(TEST_FLAGS) $(LOADLIBES) $(LDLIBS)

test_unit_conv: ${UNIT_CONV_TEST_OBJS}
	$(FC) -o $(TEST_BIN)TEST_UNIT_CONV_MOD.EXE $(UNIT_CONV_TEST_OBJS) $(BUILD_FLAGS) $(LDFLAGS) $(FFLAGS) $(TEST_FLAGS) $(LOADLIBES) $(LDLIBS)

test_io_mod: ${MODULE_OBJS} ${APM_SUBS_TEST_OBJS}
	$(FC) -o $(TEST_BIN)TEST_IO_MOD.EXE ${MODULE_OBJS} $(IO_MOD_TEST_OBJS) $(BUILD_FLAGS) $(LDFLAGS) $(FFLAGS) $(TEST_FLAGS) $(LOADLIBES) $(LDLIBS)

unit_tests: test_string test_unit_conv test_io_mod

test: clean ${MODULE_OBJS} ${TEST_OBJS} ${OBJDIR}${MODELNAME} unit_tests
	mv ${OBJDIR}${MODELNAME} .

coverage:
	gcov *.F -o dist
