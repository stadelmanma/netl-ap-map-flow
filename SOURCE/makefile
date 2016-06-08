#
# defining variables
COMPILER = gfortran
OPTIMIZE = -O2
MODELNAME = APM-MODEL.EXE
EXPORTNAME = OPENFOAM-EXPORT.EXE
#
SHAREDFILES = APM_MODULE.F UNIT_CONVERSION_MODULE.F D4_MODULE.F90 APM_SUBROUTINES.F APM_SOLVER.F
MODELFILES = APERTURE_MAP_FLOW.F APM_FLOW.F APM_OUTPUT.F
EXPORTFILES = OPENFOAM_EXPORT.F OPENFOAM_EXPORT_SUBROUTINES.F
#
WFLAGS = -Wall -Wline-truncation -Wcharacter-truncation -Wsurprising -Waliasing -Wunused-parameter
FFLAGS = -fimplicit-none -fwhole-file -fcheck=all -std=f2008 -pedantic -fbacktrace -cpp
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
# hardcoding for now it since make cant seem to access windows commands only it's shell commands
RM = rm -f
RM_TEMP = find . -type f -name "*~" -delete
#
# This will compile the entire program and it's modules
all: modules model export

modules:
	$(COMPILER) -c APM_MODULE.F
	$(COMPILER) -c UNIT_CONVERSION_MODULE.F
	$(COMPILER) -c D4_MODULE.F90

model: modules
	$(COMPILER) -o $(MODELNAME) $(SHAREDFILES) $(MODELFILES) $(OPTIMIZE) $(FFLAGS) $(OS) $(WFLAGS)
	mv $(MODELNAME) ..

export: modules
	$(COMPILER) -o $(EXPORTNAME) $(SHAREDFILES) $(EXPORTFILES) $(OPTIMIZE) $(FFLAGS) $(OS) $(WFLAGS)
	mv $(EXPORTNAME) ..

clean:
	$(RM) *.o
	$(RM) *.mod
	$(RM) *.EXE
	#
	cd ..; $(RM) *.EXE

rm_temp:
	cd ..; $(RM_TEMP)