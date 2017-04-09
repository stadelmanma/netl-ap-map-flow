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


# defining test file target and file lists for each unit test
TEST_STRING = $(TEST_BIN)test_string_mod.exe
STRING_MOD_TEST_FILES =  STRING_MODULE_UNIT_TEST.F \
	UNIT_TEST_MODULE.F \
	STRING_MODULE.F
STRING_MOD_TEST_OBJS  = $(addprefix $(OBJDIR), $(STRING_MOD_TEST_FILES:.F=.o))

TEST_UNIT_CONV = $(TEST_BIN)test_unit_conv_mod.exe
UNIT_CONV_TEST_FILES = UNIT_CONVERSION_UNIT_TEST.F \
	UNIT_TEST_MODULE.F \
	STRING_MODULE.F \
	UNIT_CONVERSION_MODULE.F
UNIT_CONV_TEST_OBJS = $(addprefix $(OBJDIR), $(UNIT_CONV_TEST_FILES:.F=.o))

TEST_IO = $(TEST_BIN)test_io_mod.exe
IO_MOD_TEST_FILES = IO_MODULE_UNIT_TEST.F \
	UNIT_TEST_MODULE.F
IO_MOD_TEST_OBJS = $(addprefix $(OBJDIR), $(IO_MOD_TEST_FILES:.F=.o))


# compiles test specific files without test flags to avoid unwanted coverage data
${OBJDIR}%.o : ${TESTSRC}%.F | ${OBJDIR}
	$(FC) -c $(BUILD_FLAGS) $(FFLAGS) -o $@ $<

${TEST_STRING}: ${STRING_MOD_TEST_OBJS}
	$(FC) -o $@ $(STRING_MOD_TEST_OBJS) $(BUILD_FLAGS) $(LDFLAGS) $(FFLAGS) $(TEST_FLAGS) $(LOADLIBES) $(LDLIBS)

${TEST_UNIT_CONV}: ${UNIT_CONV_TEST_OBJS}
	$(FC) -o $@ $(UNIT_CONV_TEST_OBJS) $(BUILD_FLAGS) $(LDFLAGS) $(FFLAGS) $(TEST_FLAGS) $(LOADLIBES) $(LDLIBS)

${TEST_IO}: ${MODULE_OBJS}
	$(FC) -o $@ $(MODULE_OBJS) $(IO_MOD_TEST_OBJS) $(BUILD_FLAGS) $(LDFLAGS) $(FFLAGS) $(TEST_FLAGS) $(LOADLIBES) $(LDLIBS)

unit_tests: ${TEST_STRING} ${TEST_UNIT_CONV} ${TEST_IO}

test: clean ${MODULE_OBJS} ${TEST_OBJS} ${OBJDIR}${MODELNAME} unit_tests
	mv $(OBJDIR)$(MODELNAME) .

coverage:
	gcov *.F -o dist
