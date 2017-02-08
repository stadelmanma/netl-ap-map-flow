#
# defining variables
CC = gfortran
OPTIMIZE ?= -O3
MODELNAME ?= APM-MODEL.EXE
OBJDIR = dist/
RM = rm -rf
MKDIR = mkdir -p $(OBJDIR)
.DEFAULT_GOAL:= $(OBJDIR)$(MODELNAME)

# setting OS flag
OS = -DWIN64=0
ifdef SystemRoot
	OS = -DWIN64=1
	MKDIR = echo "Manually create source/dist directory if needed"
else ifdef SYSTEMROOT
	OS = -DWIN64=1
	MKDIR = echo "Manually create source/dist directory if needed"
endif

# setting variables
MODEL_FILES := $(wildcard *.F)
MODEL_OBJS = $(addprefix $(OBJDIR), $(MODEL_FILES:.F=.o))

MODULE_FILES = STRING_MODULE.F  \
	IO_MODULE.F \
	UNIT_CONVERSION_MODULE.F \
	D4_SOLVER_MODULE.F \
	MAP_MODULE.F \
	APM_MODULE.F
MODULE_OBJS = $(addprefix $(OBJDIR), $(MODULE_FILES:.F=.o))

#
# determining flags to apply at compile time based on target
# test flags are only defined when this file is included into the testing makefile
FLAGS = $(OPTIMIZE) $(OS) -J$(OBJDIR)
debug test: FLAGS = -fimplicit-none -fwhole-file -fcheck=all -std=f2008 -pedantic -fbacktrace -cpp -g -pg
debug test: FLAGS += -Wall -Wline-truncation -Wcharacter-truncation -Wsurprising -Waliasing -Wunused-parameter
debug test: FLAGS += $(OS) -J$(OBJDIR) -I$(OBJDIR)


${OBJDIR}:
	$(MKDIR)

${OBJDIR}%.o : %.F | ${OBJDIR}
	$(CC) -c $(FLAGS) $(TEST_FLAGS) -o $@ $<

${OBJDIR}${MODELNAME}: ${MODULE_OBJS} ${MODEL_OBJS}
	$(CC) $(FLAGS) $(TEST_FLAGS) $^ -o $@

debug: clean ${OBJDIR}${MODELNAME}

clean:
	$(RM) $(OBJDIR) *.o *.mod *.EXE *.gcno *.gcda *.gcov
