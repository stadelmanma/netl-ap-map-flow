#
# defining default variable names (assume UNIX system)
FC = gfortran
MKDIR = mkdir -p
RMDIR = rm -rf
OS_NAME = $(shell uname)
MODELNAME = apm-lcl-model.exe
.DEFAULT_GOAL := all

OBJDIR = dist
override OBJDIR := $(strip $(OBJDIR))/

OS_FLAG = -DWIN64=0
STATIC_FLAG =
BUILD_FLAGS = -cpp -m64 $(OS_FLAG) $(STATIC_FLAG) -J$(OBJDIR)
FFLAGS = -O3 -fdefault-real-8 -fdefault-double-8

# determining system type if not supplied
ifndef SYS
	ifneq (,$(findstring CYGWIN,$(OS_NAME)))
		SYS = POSIX
	else ifdef SystemRoot
		SYS = WIN
	else ifdef SYSTEMROOT
		SYS = WIN
	else
		SYS = POSIX
	endif
endif

# updating some commands if system is windows
ifeq ($(SYS),WIN)
	SHELL=cmd.exe
	OS_FLAG = -DWIN64=1
	MKDIR = mkdir
	RM = del /Q
	RMDIR = rmdir /Q /S
endif

# setting up object variables
MODEL_FILES := $(wildcard *.F)
MODEL_OBJS = $(addprefix $(OBJDIR), $(MODEL_FILES:.F=.o))

MODULE_FILES = STRING_MODULE.F  \
	UNIT_CONVERSION_MODULE.F \
	D4_SOLVER_MODULE.F \
	IO_MODULE.F \
	MAP_MODULE.F \
	OUTPUT_MODULE.F \
	APM_MODULE.F
MODULE_OBJS = $(addprefix $(OBJDIR), $(MODULE_FILES:.F=.o))

#
# determining flags to apply at compile time based on target
# test flags are only defined when this file is included into the testing makefile

debug test: FFLAGS = -fimplicit-none -fwhole-file -fcheck=all -std=f2008 -pedantic -fbacktrace -g -pg
debug test: FFLAGS += -Wall -Wline-truncation -Wcharacter-truncation -Wsurprising -Waliasing -Wunused-parameter
debug test: FFLAGS += -fdefault-real-8 -fdefault-double-8


${OBJDIR}:
	-$(MKDIR) $(OBJDIR:/=)

${OBJDIR}%.o : %.F | ${OBJDIR}
	$(FC) -c $(BUILD_FLAGS) $(FFLAGS) $(TEST_FLAGS) -o $@ $<

${OBJDIR}${MODELNAME}: ${MODULE_OBJS} ${MODEL_OBJS}
	$(FC) $(BUILD_FLAGS) $(LDFLAGS) $(FFLAGS) $(TEST_FLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

all: ${OBJDIR}${MODELNAME}

rebuild: clean all

debug: rebuild

.PHONY: clean
clean:
	$(RM) *.o *.mod *.EXE *.gcno *.gcda *.gcov
	-$(RMDIR) $(OBJDIR:/=)
