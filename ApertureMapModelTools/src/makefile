#
# defining default variable names (assume UNIX system)
FC = gfortran
MKDIR = mkdir -p
RMDIR = rm -rf

OS_NAME =$(shell uname)
OS_FLAG = -DWIN64=0

OPTIMIZE ?= -O3
MODELNAME ?= apm-lcl-model.exe
OBJDIR ?= dist
STATIC_FLAG ?=

.DEFAULT_GOAL := all

override OBJDIR := $(strip $(OBJDIR))/

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
FLAGS = $(OPTIMIZE) $(OS_FLAG) $(STATIC_FLAG) -J$(OBJDIR) -fdefault-real-8 -fdefault-double-8
debug test: FLAGS = -fimplicit-none -fwhole-file -fcheck=all -std=f2008 -pedantic -fbacktrace -cpp -g -pg
debug test: FLAGS += -Wall -Wline-truncation -Wcharacter-truncation -Wsurprising -Waliasing -Wunused-parameter
debug test: FLAGS += $(OS_FLAG) -J$(OBJDIR) -I$(OBJDIR) -fdefault-real-8 -fdefault-double-8


${OBJDIR}:
	-$(MKDIR) $(OBJDIR:/=)

${OBJDIR}%.o : %.F | ${OBJDIR}
	$(FC) -c $(FLAGS) $(TEST_FLAGS) -o $@ $<

${OBJDIR}${MODELNAME}: ${MODULE_OBJS} ${MODEL_OBJS}
	$(FC) $(FLAGS) $(TEST_FLAGS) $^ -o $@

all: ${OBJDIR}${MODELNAME}

rebuild: clean all

debug: rebuild

.PHONY: clean
clean:
	$(RM) *.o *.mod *.EXE *.gcno *.gcda *.gcov
	-$(RMDIR) $(OBJDIR:/=)
