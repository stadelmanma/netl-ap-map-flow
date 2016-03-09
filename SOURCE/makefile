#
# defining variables
COMPILER = gfortran
OPTIMIZE = -O2
MODELNAME = APM-MODEL.EXE
EXPORTNAME = OPENFOAM-EXPORT.EXE
#
SHAREDFILES = APM_MODULE.F UNIT_CONVERSION_MODULE.F APM_SUBROUTINES.F APM_SOLVER.F
MODELFILES = APERTURE_MAP_FLOW.F APM_FLOW.F APM_OUTPUT.F
EXPORTFILES = OPENFOAM_EXPORT.F OPENFOAM_EXPORT_SUBROUTINES.F
#
WFLAGS = -Wall -Wline-truncation -Wcharacter-truncation -Wsurprising -Waliasing -Wunused-parameter 
FFLAGS = -fimplicit-none -fwhole-file -fcheck=all -std=f2008 -pedantic -fbacktrace
#
ifdef SystemRoot
	RM = del /Q
	RM_TEMP = del /Q *~
else
	RM = rm -f
	RM_TEMP = find . -type f -name "*~" -delete
endif
#
# This will compile the entire program and it's modules
all: modules model export

modules:	
	$(COMPILER) -c APM_MODULE.F
	$(COMPILER) -c UNIT_CONVERSION_MODULE.F

model: modules
	$(COMPILER) -o $(MODELNAME) $(SHAREDFILES) $(MODELFILES) $(OPTIMIZE) $(FFLAGS) $(WFLAGS) 
	mv $(MODELNAME) ..

export: modules
	$(COMPILER) -o $(EXPORTNAME) $(SHAREDFILES) $(EXPORTFILES) $(OPTIMIZE) $(FFLAGS) $(WFLAGS) 
	mv $(EXPORTNAME) ..
	
clean:
	$(RM) *.o
	$(RM) *.mod
	$(RM) *.EXE
	#
	cd ..; $(RM) *.EXE

rm_temp:
	cd ..; $(RM_TEMP)