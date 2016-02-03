C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE INITIALIZE_RUN(BOK)
C     
      USE TWOD_MODULE
      IMPLICIT NONE
      LOGICAL :: BOK
C
C     DEFAULT VALUES
      PERCENTILE = .FALSE.
      MANIFOLD = .TRUE.
      RATEC = .FALSE.
      PRESC = .FALSE.
      IFLUID = 2 !DEFAULTS TO LIQUID
      RHO = 0.0
      VOX_MET = 0.0
      AVG_FACT = 1.0
      MAXDIM = 2000
      HIGH_MASK = 10000.0
      LOW_MASK = 1E-9
      R_FACT = 0.0
      FPB = -1.0
      OUTPB = -1.0
      TEMP_CONV = FAR_RAN
      UNIT(:) = 'SI'
      UNIT_IN(1) = 'PA'
      UNIT_IN(2) = 'M'
      UNIT_IN(3) = 'FAHR'
      UNIT_IN(4) = 'SEC'
      UNIT_IN(5) = 'M^3/SEC'
      UNIT_IN(7) = 'KG/M^3'
C
C     INITIALIZING IO
      CALL ASSIGN_IO(BOK)
      IF (.NOT. BOK) GOTO 1000
C
C     READING INPUT FILE
      CALL READ_MASTER(BOK)
      IF (.NOT. BOK) GOTO 1000
C
C     READING APERTURE MAP
      CALL READ_AP_MAP(BOK)
      IF (.NOT. BOK) GOTO 1000
C
C     INITIALIZING PVT TABLES
      CALL INIT_PVT(BOK)
      IF (.NOT. BOK) GOTO 1000
C
C     INITIALIZING FRACTURE PROPERTIES
      CALL COEF(BOK)
      IF (.NOT. BOK) GOTO 1000
C
C     CREATING FLOW AND PRESSURE BOUNDARIES
      CALL FLOW_BOUNDARY(BOK)
      IF (.NOT. BOK) GOTO 1000
C
C     INITIALIZING OUTPUT FILES
      CALL INIT_OUTPUT(BOK)
      IF (.NOT. BOK) GOTO 1000
      DEALLOCATE(AP_MAP)
C
      RETURN
C
C
 1000 BOK = .FALSE.
      RETURN
C 
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE ASSIGN_IO(BOK)
C
      USE TWOD_MODULE
C
      IMPLICIT NONE
      INTEGER :: I,IFLD,NFLD
      LOGICAL :: BOK,APM,OVERWRITE
      CHARACTER(MAXLEN):: FLOX_FILE,FLOZ_FILE,FLOM_FILE
C
C     INPUT UNIT NUMBERS
      IINP  = 10
      IPVT  = 11
      IAPM  = 12
C     
C     OUTPUT UNIT NUMBERS
      IOUT  = IAPM  + 2
      ISTAT = IOUT  + 1
      IMAP  = ISTAT + 1
      IFLOX = IMAP  + 1
      IFLOZ = IFLOX + 1
      IFLOM = IFLOZ + 1
      IPRES = IFLOM + 1
      IVTK  = IPRES + 1
      IBMD = IVTK  + 1
C
C     DEFAULT FILE IO
      OVERWRITE = .FALSE.
      MASTER = ".\FRACTURE_INITIALIZATION.INP"
      SUM_FILE = ".\FRACTURE_LOG.TXT"
      STAT_FILE = ".\FRACTURE_STAT.CSV"
      MAP_FILE = ".\FRACTURE_APERTURE.CSV"
      FLOW_FILE = ".\FRACTURE_FLOW.CSV"
      PRESS_FILE = ".\FRACTURE_PRESS.CSV"
      VTK_FILE = ".\FRACTURE_VTK.vtk"
      FOAM_FILE = ".\blockMeshDict"
      
C
C     CHECKING FOR A COMMAND LINE INP FILE TO PARSE
      NFLD = COMMAND_ARGUMENT_COUNT()
      IF (NFLD > 0) THEN
        CALL GET_COMMAND_ARGUMENT(1,MASTER)
        WRITE(*,"(A)") ""
        WRITE(*,"(A)") " USING SUPPLIED INPUT FILE "//MASTER
      END IF
C
      OPEN(UNIT=IINP,FILE=MASTER,ACTION="READ",STATUS="OLD")
      WRITE(*,"(A)")""
      WRITE(*,"(A)")" READING INITIALIZATION FILE"
C
C     READING IN FILE NAMES
      DO 
        CALL LNPROC(IINP,MAXFLD,MAXLEN,CVAR,CFLD,LFLD,NFLD)
        IF (NFLD == 0) EXIT
        IF (INDEX(CFLD(1),'PVT-PATH') > 0) THEN
          IFLD = 2
          IF (NFLD < 2) GOTO 905
          PVT_FILE = CFLD(IFLD)
        ELSEIF (INDEX(CFLD(1),'APER-MAP') > 0) THEN
          IFLD = 3
          IF (NFLD < 3) GOTO 905
          APM_FILE = CFLD(IFLD)
          APM = .TRUE.
        ELSEIF (INDEX(CFLD(1),'SUMMARY-PATH') > 0) THEN
          IFLD = 2
          IF (NFLD < 2) GOTO 905
          SUM_FILE = CFLD(IFLD)
        ELSEIF (INDEX(CFLD(1),'STAT-FILE') > 0) THEN
          IFLD = 3
          IF (NFLD < 3) GOTO 905
          STAT_FILE = CFLD(IFLD)
        ELSEIF (INDEX(CFLD(1),'APER-FILE') > 0) THEN
          IFLD = 3
          IF (NFLD < 3) GOTO 905
          MAP_FILE = CFLD(IFLD)
        ELSEIF (INDEX(CFLD(1),'FLOW-FILE') > 0) THEN
          IFLD = 3
          IF (NFLD < 3) GOTO 905
          FLOW_FILE = CFLD(IFLD)
        ELSEIF (INDEX(CFLD(1),'PRESS-FILE') > 0) THEN
          IFLD = 3
          IF (NFLD < 3) GOTO 905
          PRESS_FILE = CFLD(IFLD)
        ELSEIF (INDEX(CFLD(1),'VTK-FILE') > 0) THEN
          IFLD = 3
          IF (NFLD < 3) GOTO 905
          VTK_FILE = CFLD(IFLD)
          I = INDEX(VTK_FILE,'.',BACK=.TRUE.)
          CALL LOWER_CASE(VTK_FILE(I:),VTK_FILE(I:))
        ELSEIF (INDEX(CFLD(1),'OVERWRITE') > 0) THEN
          OVERWRITE = .TRUE.
        ELSE
          EXIT
        END IF
      END DO
C
C     OPENING INPUT FILES
      OPEN(UNIT=IPVT,FILE=PVT_FILE,STATUS="OLD")
      IF (APM) THEN
        OPEN(UNIT=IAPM,FILE=APM_FILE,STATUS="OLD")
      ELSE 
        CVAR = '     NO APERTURE MAP INPUT FILE PROVIDED, EXITING'
        CALL MESSAGE(CVAR)
        GOTO 1000
      END IF
C
C     CREATING ADDITIONAL FLOW FILES USING ROOT NAME
      I = INDEX(FLOW_FILE,'.',.TRUE.)
      FLOX_FILE = FLOW_FILE(1:I-1)//'-X'//FLOW_FILE(I:)
      FLOZ_FILE = FLOW_FILE(1:I-1)//'-Z'//FLOW_FILE(I:)
      FLOM_FILE = FLOW_FILE(1:I-1)//'-M'//FLOW_FILE(I:)
C
C     OPENING OUTPUT FILES
      CALL OPEN_FILE(IOUT,SUM_FILE,OVERWRITE,BOK)
      IF (FOAM_EXPORT) THEN
        CALL OPEN_FILE(IBMD,FOAM_FILE,OVERWRITE,BOK)
        GOTO 800
      END IF
      CALL OPEN_FILE(ISTAT,STAT_FILE,OVERWRITE,BOK)
      CALL OPEN_FILE(IMAP,MAP_FILE,OVERWRITE,BOK)
      CALL OPEN_FILE(IFLOX,FLOX_FILE,OVERWRITE,BOK)
      CALL OPEN_FILE(IFLOZ,FLOZ_FILE,OVERWRITE,BOK)
      CALL OPEN_FILE(IFLOM,FLOM_FILE,OVERWRITE,BOK)
      CALL OPEN_FILE(IPRES,PRESS_FILE,OVERWRITE,BOK)
      CALL OPEN_FILE(IVTK,VTK_FILE,OVERWRITE,BOK)
C
  800 CALL BLANK
      CALL MESSAGE("     IO INITIALIZED")
      RETURN
C
  905 CALL INSUFFICIENT_ERROR("FILE NAME")
      CALL MESSAGE(CVAR)
      GOTO 1000
C
 1000 BOK = .FALSE.
      RETURN
C
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE OPEN_FILE(IUNIT,NAME,OVERWRITE,BOK)
C
      IMPLICIT NONE
      INTEGER :: IUNIT,ISTAT
      LOGICAL :: OVERWRITE,BOK
      CHARACTER(80)  :: STAT
      CHARACTER(300) :: CVAR
      CHARACTER(*)   :: NAME
C
C     SETTING VARS
      STAT = 'NEW'
      IF (OVERWRITE) THEN
        STAT = 'REPLACE'
      END IF
C
C     ATTEMPTING TO OPEN FILE
      IF (OVERWRITE) THEN
        OPEN (UNIT=IUNIT,IOSTAT=ISTAT,FILE=NAME,STATUS=STAT,ERR=920)
      ELSE
        OPEN (UNIT=IUNIT,IOSTAT=ISTAT,FILE=NAME,STATUS=STAT,ERR=900)
      END IF
C
      RETURN
C
C     FORMATTING
C
  500 FORMAT('IO ERROR: ',I0,' ATTEMPTING TO OPEN: ',A)
C
  600 FORMAT(' SPECIFY "OVERWRITE" IN THE INITIALIZATION ', 
     &       'FILE OR USE A DIFFERENT NAME FOR OUTPUT FILE: ',A)
C
  900 CALL BLANK
      WRITE(CVAR,500)ISTAT,TRIM(NAME)
      CALL MESSAGE(CVAR)
      GOTO 1000
C
  920 CALL BLANK
      CALL MESSAGE(" FILE: '"//TRIM(NAME)//"' ALREADY EXISTS")
      WRITE(CVAR,600)TRIM(NAME)
      CALL MESSAGE(CVAR)
      GOTO 1000
C
 1000 BOK = .FALSE.
      RETURN      
C    
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE READ_MASTER(BOK)
C
      USE TWOD_MODULE
C
      IMPLICIT NONE
      INTEGER :: IFLD,NFLD
      LOGICAL :: BOK,OUTPUT_UNIT = .FALSE.
C
      NFLD = SIZE(CFLD)
C
C     READING IN MASTER INPUT DATA
      UNIT(:) = 'SI'
      DO 
        IF     (INDEX(CFLD(1),'FRAC-PRESS') > 0) THEN
          IF (NFLD < 3) GOTO 905 
          IFLD = 2      
          READ(CFLD(IFLD),"(F100.0)",ERR = 910) FPB
          IFLD = 3
          READ(CFLD(IFLD),"(A)",ERR = 910) UNIT_IN(1)
          UNIT(1) = 'SI'
          CALL UNIT_CONV(1,UNIT_IN(1),UNIT(1),PRES_CONV,BOK)
          FPB = FPB*PRES_CONV
        ELSEIF (INDEX(CFLD(1),'OUTLET-PRES') > 0) THEN
          IF (NFLD < 3) GOTO 905  
          IFLD = 2      
          READ(CFLD(IFLD),"(F100.0)",ERR = 910) OUTPB
          IFLD = 3
          READ(CFLD(IFLD),"(A)",ERR = 910) UNIT_IN(1)
          PRESC = .TRUE.
          CALL MESSAGE("     FRACTURE FLOW IS PRESSURE CONTROLLED")
          UNIT(1) = 'SI'
          CALL UNIT_CONV(1,UNIT_IN(1),UNIT(1),PRES_CONV,BOK)
          OUTPB = OUTPB*PRES_CONV
          UNIT_IN(5) = 'M^3/SEC'
        ELSEIF (INDEX(CFLD(1),'OUTLET-RATE') > 0) THEN
          IF (NFLD < 3) GOTO 905
          IFLD = 2      
          READ(CFLD(IFLD),"(F100.0)",ERR = 910) OUTRATE
          IFLD = 3
          READ(CFLD(IFLD),"(A)",ERR = 910) UNIT_IN(5)
          RATEC = .TRUE.
          UNIT(5) = 'SI'
          CALL MESSAGE("     FRACTURE FLOW IS RATE CONTROLLED")
          CALL UNIT_CONV(5,UNIT_IN(5),UNIT(5),RATE_CONV,BOK)
          OUTRATE = OUTRATE*RATE_CONV
        ELSEIF (INDEX(CFLD(1),'FLUID-TYPE') > 0) THEN
          IFLD = 2
          IF (NFLD < IFLD) GOTO 905
          IF (INDEX(CFLD(IFLD),'GAS') > 0) THEN
            IFLUID = 1
          ELSEIF (INDEX(CFLD(IFLD),'LIQUID') > 0) THEN
            IFLUID = 2
          ELSE
            CALL MESSAGE(' INVALID FLUID TYPE: '//TRIM(CFLD(IFLD)))
            CALL MESSAGE(' VALID OPTIONS ARE: LIQUID OR GAS')
            GOTO 1000
          END IF
        ELSEIF (INDEX(CFLD(1),'FLUID-DENSITY') > 0) THEN
          IFLD = 2
          IF (NFLD < IFLD) GOTO 905
          READ(CFLD(IFLD),"(F100.0)",ERR = 910) RHO
          IFLD = 3
          READ(CFLD(IFLD),"(A)",ERR = 910) UNIT_IN(7)
          UNIT(7) = 'SI'
          CALL UNIT_CONV(7,UNIT_IN(7),UNIT(7),RHO_CONV,BOK)
          RHO = RHO*RHO_CONV
        ELSEIF (INDEX(CFLD(1),'STD-TEMP') > 0) THEN
          IFLD = 2
          IF (NFLD < 3) GOTO 905         
          READ(CFLD(IFLD),"(F100.0)",ERR = 910) STD_TEMP
          IFLD = 3
          READ(CFLD(IFLD),"(A)",ERR = 910) UNIT_IN(3)
        ELSEIF (INDEX(CFLD(1),'STD-PRESS') > 0) THEN
          IF (NFLD < 3) GOTO 905 
          IFLD = 2     
          READ(CFLD(IFLD),"(F100.0)",ERR = 910) STD_PRES
          IFLD = 3
          READ(CFLD(IFLD),"(A)",ERR = 910) UNIT_IN(1) 
          UNIT(1) = 'SI'
          CALL UNIT_CONV(1,UNIT_IN(1),UNIT(1),PRES_CONV,BOK)
          STD_PRES = STD_PRES*PRES_CONV
        ELSEIF (INDEX(CFLD(1),'OUTFLOW-SIDE') > 0) THEN
          IFLD = 2
          IF (NFLD < IFLD) GOTO 905
          OUTFLOW = CFLD(IFLD)
        ELSEIF (INDEX(CFLD(1),'MANIFOLD') > 0) THEN
          IFLD = 2
          IF (NFLD < IFLD) GOTO 905
          IF (INDEX(CFLD(IFLD),'FALSE') > 0) MANIFOLD = .FALSE.
        ELSEIF (INDEX(CFLD(1),'VOXEL') > 0) THEN
          IFLD = 3
          IF (NFLD < 4) GOTO 905        
          READ(CFLD(IFLD),"(F10.0)",ERR = 910) VOX_MET
          CFLD(5) = 'SI'
          CALL UNIT_CONV(2,CFLD(4),CFLD(5),DIM_CONV,BOK)
          VOX_MET = VOX_MET*DIM_CONV
        ELSEIF (INDEX(CFLD(1),'ROUGH') > 0) THEN
          IFLD  = 4
          IF (NFLD < IFLD) GOTO 905
          READ(CFLD(IFLD),"(F10.0)",ERR = 910) R_FACT
        ELSEIF (INDEX(CFLD(1),'MAP') > 0) THEN
          IFLD = 4
          IF (NFLD < IFLD) GOTO 905        
          READ(CFLD(IFLD),"(F10.0)",ERR = 910) AVG_FACT
        ELSEIF (INDEX(CFLD(1),'CALCULATE') > 0) THEN
          IFLD = 2
          IF (NFLD < IFLD) GOTO 905
          IF (INDEX(CFLD(2),'PERCENT') > 0) PERCENTILE = .TRUE.
          ! POPULATING PERCENTILE ARRAY
          IF (NFLD >= 3) THEN
            ALLOCATE(PERC_ARR(2,NFLD))
            PERC_ARR(:,:) = 0
            NPCT = NFLD - 2
            DO IFLD = 3,NFLD
              READ(CFLD(IFLD),"(F10.0)",ERR = 910)PERC_ARR(1,IFLD-2)
            END DO
          ELSE
            ALLOCATE(PERC_ARR(2,9))
            NPCT = 9
            PERC_ARR(1,1:9) = [1,5,10,25,50,75,90,95,99]
          END IF
        ELSEIF (INDEX(CFLD(1),'HIGH-MASK') > 0) THEN
          IFLD = 2
          IF (NFLD < 2) GOTO 905        
          READ(CFLD(IFLD),*,ERR = 910) HIGH_MASK
          PRINT *, HIGH_MASK
        ELSEIF (INDEX(CFLD(1),'LOW-MASK') > 0) THEN
          IFLD = 2
          IF (NFLD < 2) GOTO 905        
          READ(CFLD(IFLD),*,ERR = 910) LOW_MASK
        ELSEIF (INDEX(CFLD(1),'MAXIMUM') > 0) THEN
          IFLD = 4
          IF (NFLD < IFLD) GOTO 905        
          READ(CFLD(IFLD),"(I4)",ERR = 910) MAXDIM
        ELSEIF (INDEX(CFLD(1),'SOLVER') > 0) THEN
          SOLVER_TYPE = TRIM(CFLD(2))
        ELSEIF (INDEX(CFLD(1),'OUTPUT-UNITS') > 0) THEN
          IF (NFLD < 6) GOTO 905
          IFLD = 2
          READ(CFLD(IFLD),"(A)",ERR = 910) UNIT_OUT(1)
          IFLD = 3
          READ(CFLD(IFLD),"(A)",ERR = 910) UNIT_OUT(2)
          IFLD = 4
          READ(CFLD(IFLD),"(A)",ERR = 910) UNIT_OUT(3)
          IFLD = 5
          READ(CFLD(IFLD),"(A)",ERR = 910) UNIT_OUT(4)
          IFLD = 6
          READ(CFLD(IFLD),"(A)",ERR = 910) UNIT_OUT(5)
          OUTPUT_UNIT = .TRUE.
        ELSE
          CVAR = TRIM(CVAR(1:120)) !SHORTENING LENGTH TO PREVENT OVERFLOW
          CVAR = " ** WARING: UNRECOGNIZED INPUT: "//TRIM(CVAR)//" **"
          CALL MESSAGE(CVAR)
        END IF
        CALL LNPROC(IINP,MAXFLD,MAXLEN,CVAR,CFLD,LFLD,NFLD)
        IF (NFLD == 0) EXIT
      END DO
C
C     
      IF (IFLUID == 0) THEN
        CVAR = " **** FLUID TYPE MUST BE SPECFIED AS LIQUID OR GAS ****"
        CALL MESSAGE(CVAR)
        GOTO 1000
      END IF
C
C     
      IF (VOX_MET == 0) THEN
        CALL MESSAGE(" **** ERROR: VOXEL SIZE MUST BE SPECIFIED ****")
        GOTO 1000
      END IF
C
C     SETTING CONVERSION VALUES 
      IF (.NOT. OUTPUT_UNIT) UNIT_OUT = UNIT_IN
      UNIT(:) = 'SI'
      UNIT(3) = 'F'
      UNIT(7) = 'KG/M^3'
      CALL UNIT_CONV(1,UNIT_IN(1),UNIT(1),PRES_CONV,BOK)
      CALL UNIT_CONV(2,UNIT_IN(2),UNIT(2),DIM_CONV,BOK)
      CALL UNIT_CONV(4,UNIT_IN(4),UNIT(4),TIME_CONV,BOK)
      CALL UNIT_CONV(5,UNIT_IN(5),UNIT(5),RATE_CONV,BOK)
      IF (.NOT. BOK) GOTO 1000
C
      RETURN
C
  905 CALL INSUFFICIENT_ERROR("INITIALIZATION")
      CALL MESSAGE(CVAR)
      GOTO 1000
C
  910 CALL FIELD_ERROR("INITIALIZATION",IFLD)
      CALL MESSAGE(CVAR)
      GOTO 1000
C
 1000 BOK = .FALSE.
      RETURN
C     
      
C
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE UNIT_CONV(TYPE,UNITIN,UNITOUT,CONV_FACT,BOK)
C
      USE TWOD_MODULE
      IMPLICIT NONE
      REAL(8) :: CONV_FACT,TMP,RATE_DIM,RATE_TIME,RHO_DIM,RHO_MASS
      INTEGER :: TYPE,ERR_TYPE
      LOGICAL :: BOK,SI,LOOP
      CHARACTER(*) :: UNITIN,UNITOUT
      CHARACTER(80) :: TYPES(11),C80,R_UNIT
C
C @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
C
C     UNIT CONVERSION TYPES
C       1 - PRESSURE
C       2 - DISTANCE
C       3 - TEMPERATURE
C       4 - TIME
C       5 - FLOW RATE
C       6 - VISCOSITY 
C       7 - DENSITY
C     
C     USE UNITOUT = 'SI' FOR THE STANDARD UNIT OF ANY TYPE
C
C     TEMPERATURE CONVERSIONS ARE NOT FUNCTIONAL IN THIS VERSION
C
C @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
C
C     SETTING DEFAULTS
      CONV_FACT = 1
      TMP = 1
      C80 = UNITIN
      ERR_TYPE = TYPE
      SI = .FALSE.
      LOOP = .TRUE.
      IF (TRIM(UNITOUT) == 'SI') SI = .TRUE.
C
      TYPES(1) = "PRESSURE"
      TYPES(2) = "DISTANCE"
      TYPES(3) = "TEMPERATURE"
      TYPES(4) = "TIME"
      TYPES(5) = "FLOW RATE"
      TYPES(6) = "VISCOSITY"
      TYPES(7) = "DENSITY" 
      TYPES(8) = "FLOW RATE(VOLUME)"
      TYPES(9) = "FLOW RATE(TIME)"
      TYPES(10) = "DENSITY(MASS)"
      TYPES(11) = "DENSITY(VOLUME)"
C
C     PRESSURE
      IF (TYPE == 1) THEN
 100    IF (INDEX(C80,'PSI') > 0) THEN 
          CONV_FACT = PSI_PA
        ELSEIF(INDEX(C80,'BAR') > 0) THEN
          CONV_FACT = BAR_PA
        ELSEIF(INDEX(C80,'ATM') > 0) THEN
          CONV_FACT = ATM_PA
        ELSEIF(INDEX(C80,'KPA') > 0) THEN
          CONV_FACT = KPA_PA
        ELSEIF(INDEX(TRIM(C80),'PA') > 0) THEN
          CONV_FACT = 1
        ELSE
          GOTO 800
        END IF
C  
        IF (SI) THEN
          UNITOUT = 'PA'
        ELSEIF (LOOP) THEN !GETTING SI CONVERSION FOR UNITOUT
          C80 = UNITOUT
          TMP = CONV_FACT
          LOOP = .FALSE.
          GOTO 100
        ELSE
          CONV_FACT = TMP/CONV_FACT 
        END IF !CALCULATING IN -> OUT CONVERSION FACTOR
C
C     DISTANCE
      ELSEIF (TYPE == 2) THEN
 200    IF (INDEX(C80,'MICR') > 0) THEN
          CONV_FACT = MIC_MET
        ELSEIF (INDEX(C80,'MM') > 0) THEN
          CONV_FACT = MM_MET
        ELSEIF (INDEX(C80,'CM') > 0) THEN
          CONV_FACT = CM_MET
        ELSEIF (INDEX(C80,'IN') > 0) THEN
          CONV_FACT = IN_MET
        ELSEIF (INDEX(C80,'FT')+INDEX(C80,'FEET')> 0) THEN
          CONV_FACT = FT_MET
        ELSEIF (INDEX(C80,'VOX') > 0) THEN
          CONV_FACT = VOX_MET
        ELSEIF (INDEX(TRIM(C80),'M') > 0) THEN
          CONV_FACT = 1
        ELSE
          GOTO 800
        END IF
C 
        IF (SI) THEN
          UNITOUT = 'M'
        ELSEIF (LOOP) THEN !GETTING SI CONVERSION FOR UNITOUT
          C80 = UNITOUT
          TMP = CONV_FACT
          LOOP = .FALSE.
          GOTO 200
        ELSE
          CONV_FACT = TMP/CONV_FACT 
        END IF !CALCULATING IN -> OUT CONVERSION FACTOR
C
C     TEMPERATURE
      ELSEIF (TYPE == 3) THEN
        !!! THIS IS NOT FUNCTIONAL
        !!! FAHR CONV
        !!! CELC CONV
        !!! RANK CONV
        !!! KELV CONV 
C
C     TIME
      ELSEIF (TYPE == 4) THEN
 400    IF (INDEX(C80,'DAY') > 0) THEN
          CONV_FACT = DAY_SEC
        ELSEIF (INDEX(C80,'HOUR') > 0) THEN
          CONV_FACT = HR_SEC
        ELSEIF (INDEX(C80,'MIN') > 0) THEN
          CONV_FACT = MIN_SEC
        ELSEIF (INDEX(C80,'SEC') > 0) THEN
          CONV_FACT = 1
        ELSE
          GOTO 800
        END IF
C 
        IF (SI) THEN
          UNITOUT = 'SEC'
        ELSEIF (LOOP) THEN !GETTING SI CONVERSION FOR UNITOUT
          C80 = UNITOUT
          TMP = CONV_FACT
          LOOP = .FALSE.
          GOTO 400
        ELSE
          CONV_FACT = TMP/CONV_FACT 
        END IF !CALCULATING IN -> OUT CONVERSION FACTOR
C
C     RATE
      ELSEIF (TYPE == 5) THEN
        R_UNIT = UNITIN
C
C       SPLITTING RATE INTO DIST AND TIME UNITS
  500   C80 = R_UNIT(1:(INDEX(R_UNIT,'/')-1))
        ERR_TYPE = 8
        IF (INDEX(C80,'MICR') > 0) THEN
          RATE_DIM = MIC_MET
        ELSEIF (INDEX(C80,'MM') > 0) THEN
          RATE_DIM = MM_MET
        ELSEIF (INDEX(C80,'CM') > 0) THEN
          RATE_DIM = CM_MET
        ELSEIF (INDEX(C80,'IN') > 0) THEN
          RATE_DIM = IN_MET
        ELSEIF (INDEX(C80,'FT')+INDEX(C80,'FEET')> 0) THEN
          RATE_DIM = FT_MET
        ELSEIF (INDEX(C80,'VOX') > 0) THEN
          RATE_DIM = VOX_MET
        ELSEIF (INDEX(C80,'ML') > 0) THEN
          RATE_DIM = CM_MET
        ELSEIF (INDEX(TRIM(C80),'M^3')+INDEX(TRIM(C80),'MET') > 0) THEN
          RATE_DIM = 1
        ELSE
          GOTO 800
        END IF
C
        C80 = R_UNIT((INDEX(R_UNIT,'/')+1):LEN(R_UNIT))
        ERR_TYPE = 9
        IF (INDEX(C80,'DAY') > 0) THEN
          RATE_TIME = DAY_SEC
        ELSEIF (INDEX(C80,'HOUR') > 0) THEN
          RATE_TIME = HR_SEC
        ELSEIF (INDEX(C80,'MIN') > 0) THEN
          RATE_TIME = MIN_SEC
        ELSEIF (INDEX(C80,'SEC') > 0) THEN
          RATE_TIME = 1
        ELSE
          GOTO 800
        END IF
        CONV_FACT = RATE_DIM**3/RATE_TIME
C 
        IF (SI) THEN
          UNITOUT = 'M^3/SEC'
        ELSEIF (LOOP) THEN !GETTING SI CONVERSION FOR UNITOUT
          R_UNIT = UNITOUT
          TMP = CONV_FACT
          LOOP = .FALSE.
          GOTO 500
        ELSE
          CONV_FACT = TMP/CONV_FACT 
        END IF !CALCULATING IN -> OUT CONVERSION FACTOR
C
C     VISCOSITY
      ELSEIF (TYPE == 6) THEN
 600    IF (INDEX(C80,'CP')+INDEX(C80,'CENT') > 0) THEN
          CONV_FACT = CP_PASEC
        ELSEIF (INDEX(C80,'PA') + INDEX(C80,'SEC') > 0) THEN
          CONV_FACT = 1
        END IF
C 
        IF (SI) THEN
          UNITOUT = 'PA-SEC'
        ELSEIF (LOOP) THEN !GETTING SI CONVERSION FOR UNITOUT
          C80 = UNITOUT
          TMP = CONV_FACT
          LOOP = .FALSE.
          GOTO 600
        ELSE
          CONV_FACT = TMP/CONV_FACT 
        END IF !CALCULATING IN -> OUT CONVERSION FACTOR
C
C     DENSITY
      ELSEIF (TYPE == 7) THEN
        R_UNIT = UNITIN
C
C       SPLITTING DENSITY INTO MASS AND DISTANCE UNITS
 700    C80 = R_UNIT(1:(INDEX(R_UNIT,'/')-1))
        ERR_TYPE = 10
        IF (INDEX(C80,'SLUG') > 0) THEN
          RHO_MASS = SLG_KG
        ELSEIF (INDEX(C80,'LB') > 0) THEN
          RHO_MASS = LBS_KG
        ELSEIF (INDEX(C80,'KG') > 0) THEN
          RHO_MASS = 1.0
        ELSEIF (INDEX(C80,'G')+INDEX(C80,'GRAM') > 0) THEN
          RHO_MASS = GM_KG
        ELSE
          GOTO 800
        END IF
C
        C80 = R_UNIT((INDEX(R_UNIT,'/')+1):LEN(R_UNIT))
        ERR_TYPE = 11
        IF (INDEX(C80,'MICR') > 0) THEN
          RHO_DIM = MIC_MET
        ELSEIF (INDEX(C80,'MM') > 0) THEN
          RHO_DIM = MM_MET
        ELSEIF (INDEX(C80,'CM') > 0) THEN
          RHO_DIM = CM_MET
        ELSEIF (INDEX(C80,'IN') > 0) THEN
          RHO_DIM = IN_MET
        ELSEIF (INDEX(C80,'FT')+INDEX(C80,'FEET')> 0) THEN
          RHO_DIM = FT_MET
        ELSEIF (INDEX(C80,'VOX') > 0) THEN
          RHO_DIM = VOX_MET
        ELSEIF (INDEX(C80,'ML') > 0) THEN
          RHO_DIM = CM_MET
        ELSEIF (INDEX(TRIM(C80),'M^3')+INDEX(TRIM(C80),'MET') > 0) THEN
          RHO_DIM = 1.0
        ELSE
          GOTO 800
        END IF
        CONV_FACT = RHO_MASS/RHO_DIM**3
C 
        IF (SI) THEN
          UNITOUT = 'KG/M^3'
        ELSEIF (LOOP) THEN !GETTING SI CONVERSION FOR UNITOUT
          R_UNIT = UNITOUT
          TMP = CONV_FACT
          LOOP = .FALSE.
          GOTO 700
        ELSE
          CONV_FACT = TMP/CONV_FACT 
        END IF !CALCULATING IN -> OUT CONVERSION FACTOR
      END IF
C     
      RETURN
C
  800 UNITOUT = C80
      WRITE(CVAR,2000)TRIM(TYPES(ERR_TYPE)),TRIM(UNITOUT)
      CALL MESSAGE(CVAR)
      GOTO 1000
C
 1000 BOK = .FALSE.
      RETURN
C
 2000 FORMAT(1X,' *** ERROR: NO ',A,' CONVERSION FOUND FOR UNIT: ',
     &       A,' ***')
C
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE INIT_PVT(BOK)
C
C     READS THE INPUT DATA AND STORES IT INTO DEFINED VARIABLES
      USE TWOD_MODULE
      IMPLICIT NONE 
C
      REAL(8) :: PH,PL,PR_CONV
      REAL(8),ALLOCATABLE :: PR2(:),ZF2(:),VI2(:)
      INTEGER :: I,J,IFLD,NFLD
      CHARACTER(120) :: PVT_UNIT,C120
      LOGICAL :: BOK
C
C
      CALL BLANK
      CALL MESSAGE(" READING PVT DATA") 
C
C     PERFORMING  ALLOCATIONS
      ALLOCATE(PR(1000),ZF(1000),VI(1000))   
      VISC_CONV = 0.0
      PR_CONV   = 0.0
C
C     READING IN PVT DATA
C
C     READING DATA TEMPERTURE LINE
      CALL LNPROC(IPVT,MAXFLD,MAXLEN,C120,CFLD,LFLD,NFLD)
      IFLD = 2
      IF (NFLD < 2) GOTO 905
      READ(CFLD(IFLD),"(F10.0)",ERR=910) TEMP
C
C     READING HEADER LINE AND GETTING UNITS 
C     UNITS ARE ASSUMED TO BE SEPERATED BY SOME DELIMETER
C     AND THE NEXT FIELD IN LINE BEHIND THE VALUE
      CALL LNPROC(IPVT,MAXFLD,MAXLEN,C120,CFLD,LFLD,NFLD)
      IF (NFLD < 5) GOTO 905
      DO IFLD = 1,NFLD
        IF (INDEX(CFLD(IFLD),'PRESSURE') > 0) THEN
          IF (NFLD < IFLD + 1) GOTO 905
          PVT_UNIT = 'SI'
          CALL UNIT_CONV(1,CFLD(IFLD+1),PVT_UNIT,PR_CONV,BOK)
        ELSEIF (INDEX(CFLD(IFLD),'VISC') > 0) THEN
          IF (NFLD < IFLD + 1) GOTO 905
          UNIT(6) = 'SI'
          UNIT_IN(6) = TRIM(CFLD(IFLD+1))
          CALL UNIT_CONV(6,UNIT_IN(6),UNIT(6),VISC_CONV,BOK)
        END IF
      END DO      
C
      DO
        CALL LNPROC(IPVT,MAXFLD,MAXLEN,C120,CFLD,LFLD,NFLD)
        IF (INDEX(CFLD(1),'END') > 0) EXIT
        NVALS = NVALS + 1
        IFLD = 1
        READ(CFLD(IFLD),"(F100.0)",ERR=910) PR(NVALS)
        PR(NVALS) = PR(NVALS)*PR_CONV
        IFLD = 2
        IF (NFLD < 2) GOTO 905
        READ(CFLD(IFLD),"(F100.0)",ERR=910) ZF(NVALS)
        IFLD = 3
        IF (NFLD < 3) GOTO 905
        READ(CFLD(IFLD),"(F100.0)",ERR=910) VI(NVALS)
        VI(NVALS) = VI(NVALS)*VISC_CONV
      END DO
C
C     GENERATING THE PVT AND RELATED VECTORS 
      VALS = MAX(101,NVALS+1)
      ALLOCATE(PR2(VALS),ZF2(VALS),VI2(VALS))   
C
C     CONVERTING TEMP TO RANKINE
      TEMP = TEMP+TEMP_CONV
      STD_TEMP = STD_TEMP+TEMP_CONV
      STD_CONV = 1      
C
C     CREATING THE NEW PR VECTOR THAT WILL ALWAYS HAVE UNIFORM SPACING
      DPR = PR(NVALS)/(VALS-1)
      DO I = 1,VALS
        PR2(I) = DPR*(I-1)
      END DO     
C
C     CREATING THE Z AND VISCOSIY VECTORS       
      DO I = 1,VALS
        DO J = 1,NVALS
          IF (PR2(I) .LT. PR(J)) EXIT
        END DO
        IF (PR2(I) .LT. PR(1)) J = 2
        PH = PR(J); PL = PR(J-1)
        ZF2(I) = (PR2(I)-PL)*(ZF(J)-ZF(J-1))/(PH-PL)+ZF(J-1)
        VI2(I) = (PR2(I)-PL)*(VI(J)-VI(J-1))/(PH-PL)+VI(J-1)
      END DO
C
C     UPATING THEM TO THE EQUALLY SPACED VECTORS   
      DEALLOCATE(PR,ZF,VI)
      ALLOCATE(PR(VALS),ZF(VALS),VI(VALS))
      PR = PR2
      ZF = ZF2
      VI = VI2
C
C     PERFORMING FLUID TYPE SPECIFIC ACTIONS
      IF (IFLUID == 1) THEN
C
        ALLOCATE(PS(VALS),SQPS(VALS),EQSPS(VALS),EQPR(VALS))
C
        STD_CONV = (TEMP/STD_TEMP)*(1/STD_PRES)
C
C       CREATING THE PSEUDO-PRESS VECTOR
        PS(1) = PR(1)**2/(2*VI(1)*ZF(1))
        DO I = 2,VALS
          PS(I) = DPR/2*(PR(I-1)/(VI(I-1)*ZF(I-1))+PR(I)/(VI(I)*ZF(I)))
          PS(I) = PS(I)+PS(I-1)
        END DO 
C
C       DSPS IS DELTA PHI, EQSPS IS THE EQUALLY SPACED SQRT(PHI) VECTOR         
        SQPS = SQRT(PS)
        DSPS = SQRT(PS(VALS))/(VALS-1) 
        EQSPS(1) = 0
        DO I = 2,VALS
          EQSPS(I) = (I-1)*DSPS
        END DO         
C        
C       CREATING AN EQUALLY SPACED PRESSURE VECTOR FROM EQSPS
        DO I = 1,VALS
          DO J = 1,VALS-1
            IF (EQSPS(I) .LT. SQPS(J)) EXIT
          END DO
          IF (EQSPS(I) .LT. SQPS(1)) J = 2
          PH = SQPS(J); PL = SQPS(J-1)
          EQPR(I) = (EQSPS(I)-PL)*(PR(J)-PR(J-1))/(PH-PL)+PR(J-1)  
        END DO   
      END IF
C  
C     DEALLOCATING INTERMEDIATE INTERPOLATION VECTORS
      DEALLOCATE(PR2,ZF2,VI2)
C 
      RETURN
C
  905 CALL INSUFFICIENT_ERROR("PVT")
      CALL MESSAGE(C120)
      GOTO 1000
C
  910 CALL FIELD_ERROR("PVT",IFLD)
      CALL MESSAGE(C120)
      GOTO 1000
C
 1000 BOK = .FALSE.
      RETURN
C
      END SUBROUTINE 
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE READ_AP_MAP(BOK)
C
      USE TWOD_MODULE
C
      IMPLICIT NONE
      REAL(8) :: RAW_APER
      REAL(8), ALLOCATABLE ::WIDTH_SORT(:)
      INTEGER :: IFLD,I,IX,IZ !ITERATORS
      INTEGER :: NFLD,ZEROS,MASK !SIZE/COUNTERS
      CHARACTER(100000) :: DATA_LINE
      LOGICAL :: BOK
C 
      CALL BLANK
      CALL MESSAGE(" READING APERTURE MAP")
      ALLOCATE(AP_MAP(MAXDIM,MAXDIM,0:6))
C
C     FIRST LINE OF AP MAP DATA IS THE BOTTOM OF THE CORE
C     NUM OF RADIAL CELLS = NX, NUM OF LENGTH CELLS = NZ
      NFLD = 0
      NX = 0
      NZ = 0
      HOM_APER = 0
      RAW_APER = 0
      ZEROS = 0
      MASK = 0
      MAX_APER = 0
      MIN_APER = 1000
      AP_MAP(:,:,:) = -1
      DO 
        NX = NFLD
        CALL LNPROC(IAPM,MAXFLD,MAXLEN,DATA_LINE,CFLD,LFLD,NFLD)
        IF (NFLD == 0) EXIT
C
        NZ = NZ + 1
        IF (NZ > MAXDIM) GOTO 931
        DO IFLD = 1,NFLD
          IF (NFLD > MAXDIM) GOTO 930
C
          READ(CFLD(IFLD),"(F10.0)",ERR=910) AP_MAP(NZ,IFLD,0)
          RAW_APER = RAW_APER + AP_MAP(NZ,IFLD,0)         
C
C         CONDITIONALS USED TO COLLECT DATA ON MAP
          IF (AP_MAP(NZ,IFLD,0) > MAX_APER) MAX_APER = AP_MAP(NZ,IFLD,0)
          IF (AP_MAP(NZ,IFLD,0) < MIN_APER) THEN
            IF (AP_MAP(NZ,IFLD,0) > 0) MIN_APER = AP_MAP(NZ,IFLD,0)
          END IF
          IF (INT(1E9*AP_MAP(NZ,IFLD,0)) .EQ. 0) ZEROS = ZEROS + 1
        END DO
      END DO
      RAW_APER = RAW_APER/(NZ*NX)
C
C     CALCULATING PERCENTILE RANGES OF APERATURES
      IF (PERCENTILE) THEN 
        CALL MESSAGE("     CALCULATING APERTURE PERCENTILES OF MAP")
        ALLOCATE(WIDTH_SORT(NX*NZ))
C
C       POPULATING SORTABLE WIDTH ARRAY FROM AP MAP DATA
        I = 0
        DO IZ = 1,NZ
         DO IX = 1,NX
           I = I + 1
           WIDTH_SORT(I) = AP_MAP(IZ,IX,0)
         END DO
        END DO
C
C       CALCULATING PERCENTILES
        CALL CALC_PERCENTILE(WIDTH_SORT,PERC_ARR,NX*NZ,NPCT)
C
        DEALLOCATE(WIDTH_SORT)
      END IF !ENDS PERCENTILE CONDITIONAL
C
C     APPLYING THE HIGH AND LOW MASKS TO THE MAP
      DO IZ = 1,NZ
        DO IX = 1,NX
          IF (AP_MAP(IZ,IX,0) > HIGH_MASK) MASK = MASK + 1
          IF (AP_MAP(IZ,IX,0) <  LOW_MASK) MASK = MASK + 1
C
C         CONDITIONALS USED TO MASK HIGH AND LOW EXTREMA IN MAP
          IF (AP_MAP(IZ,IX,0) > HIGH_MASK) AP_MAP(IZ,IX,0) = HIGH_MASK
          IF (AP_MAP(IZ,IX,0) <  LOW_MASK) AP_MAP(IZ,IX,0) =  LOW_MASK
          HOM_APER = HOM_APER + AP_MAP(IZ,IX,0)
        END DO
      END DO
      HOM_APER = HOM_APER/(NZ*NX)
C
C     SETTING UP THE UNIFORM OUTFLOW
      IF (.NOT. MANIFOLD) THEN 
        CALL MESSAGE("     MANIFOLD WAS DISABLED FOR THIS RUN")
      ELSE IF (INDEX(OUTFLOW,'LEFT') > 0) THEN
        DO IZ = 1,NZ
          DO IX = NX,1,-1
            AP_MAP(IZ,IX+1,0) = AP_MAP(IZ,IX,0)
          END DO
          AP_MAP(IZ,1,0) = HOM_APER
        END DO
        NX = NX + 1
      ELSE IF (INDEX(OUTFLOW,'RIGHT') > 0) THEN
        DO IZ = 1,NZ
          AP_MAP(IZ,NX+1,0) = HOM_APER
        END DO
        NX = NX + 1        
      ELSE IF (INDEX(OUTFLOW,'TOP') > 0) THEN
        DO IX = 1,NX
          AP_MAP(NZ+1,IX,0) = HOM_APER
        END DO
        NZ = NZ + 1
      ELSE IF (INDEX(OUTFLOW,'BOTTOM') > 0) THEN
        DO IX = 1,NX
          DO IZ = NZ,1,-1
            AP_MAP(IZ+1,IX,0) = AP_MAP(IZ,IX,0)
          END DO
          AP_MAP(1,IX,0) = HOM_APER
        END DO
        NZ = NZ + 1
      ELSE
        CALL MESSAGE(" INVALID OUTFLOW SIDE ENTERED: "//TRIM(OUTFLOW))
        GOTO 1000
      END IF
C
C     GETTING ADDITIONAL STATS ON THE APERTURE MAP 
      CVAR = "     CALCULATING ADDITIONAL MAP STATISTICS"
      CALL MESSAGE(CVAR)
      CALL MAP_STATS
C
C     CONVERTING CT GRID SIZE TO SI 
      CALL ALLOCATE_FRAC(NX,NZ)
      DIAM = NX*VOX_MET*AVG_FACT
      LENG = NZ*VOX_MET*AVG_FACT
      HOM_APER = HOM_APER*VOX_MET
C
C     CALCULATING AVERAGE CORNER VALUES OF CELLS
C     1 = BLC, 2 = BRC, 3 = TRC, 4 = TLC
C     HANDLING CORNERS OF MAP
      AP_MAP(1,1,1)   = AP_MAP(1,1,0)
      AP_MAP(1,NX,2)  = AP_MAP(1,NX,0)
      AP_MAP(NZ,NX,3) = AP_MAP(NZ,NX,0)
      AP_MAP(NZ,1,4)  = AP_MAP(NZ,1,0)
C     CALCULATING CORNER VALUES OF MAP INTERIOR
      DO IZ = 1,NZ-1
        DO IX = 1,NX-1
          AP_MAP(IZ,IX,3) = AP_MAP(IZ,IX,0)
          AP_MAP(IZ,IX,3) = AP_MAP(IZ,IX,3) + AP_MAP(IZ+1,IX,0)   !ABOVE
          AP_MAP(IZ,IX,3) = AP_MAP(IZ,IX,3) + AP_MAP(IZ,IX+1,0)   !RIGHT
          AP_MAP(IZ,IX,3) = AP_MAP(IZ,IX,3) + AP_MAP(IZ+1,IX+1,0) !CORNER
          AP_MAP(IZ,IX,3) = AP_MAP(IZ,IX,3)/4.0 !TRC OF CELL
          AP_MAP(IZ+1,IX+1,1) = AP_MAP(IZ,IX,3) !BLC OF CORNER CELL
          AP_MAP(IZ+1,IX,2) = AP_MAP(IZ,IX,3)   !BRC OF ABOVE CELL
          AP_MAP(IZ,IX+1,4) = AP_MAP(IZ,IX,3)   !TLC OF RIGHT CELL
        END DO
      END DO
C     CALCULATING BOTTOM LEFT AND TOP LEFT CORNER OF LEFT EDGE
      DO IZ = 1,NZ-1
          AP_MAP(IZ,1,4) = AP_MAP(IZ,1,0)
          AP_MAP(IZ,1,4) = AP_MAP(IZ,1,4) + AP_MAP(IZ+1,1,0)   !ABOVE  
          AP_MAP(IZ,1,4) = AP_MAP(IZ,1,4)/2.0 !TLC OF CELL
          AP_MAP(IZ+1,1,1) = AP_MAP(IZ,1,4)   !BLC OF ABOVE CELL
      END DO
C     CALCULATING BOTTOM LEFT AND BOTTOM RIGHT CORNER OF LOWER EDGE
      DO IX = 1,NX-1
          AP_MAP(1,IX,2) = AP_MAP(1,IX,0)
          AP_MAP(1,IX,2) = AP_MAP(1,IX,2) + AP_MAP(1,IX+1,0)   !RIGHT
          AP_MAP(1,IX,2) = AP_MAP(1,IX,2)/2.0 !BRC OF CELL
          AP_MAP(1,IX+1,1) = AP_MAP(1,IX,2)   !BLC OF RIGHT CELL
      END DO
C     CALCULATING BOTTOM RIGHT AND TOP RIGHT CORNER OF RIGHT EDGE
      DO IZ = 1,NZ-1
          AP_MAP(IZ,NX,3) = AP_MAP(IZ,NX,0)
          AP_MAP(IZ,NX,3) = AP_MAP(IZ,NX,3) + AP_MAP(IZ+1,NX,0)   !ABOVE  
          AP_MAP(IZ,NX,3) = AP_MAP(IZ,NX,3)/2.0 !TRC OF CELL
          AP_MAP(IZ+1,NX,2) = AP_MAP(IZ,NX,3)   !BRC OF ABOVE CELL
      END DO
C     CALCULATING TOP LEFT AND TOP RIGHT CORNER OF UPPER EDGE
      DO IX = 1,NX-1
          AP_MAP(NZ,IX,3) = AP_MAP(NZ,IX,0)
          AP_MAP(NZ,IX,3) = AP_MAP(NZ,IX,3) + AP_MAP(NZ,IX+1,0)   !RIGHT
          AP_MAP(NZ,IX,3) = AP_MAP(NZ,IX,3)/2.0 !TRC OF CELL
          AP_MAP(NZ,IX+1,4) = AP_MAP(NZ,IX,3)   !TLC OF RIGHT CELL
      END DO 
C
C     CREATING AVERAGE WIDTH VECTOR WITH ROUGHNESS ADJUSTMENT
      CVAR = "     CONVERTING 2-D MAP ARRAY IN VOX TO VECTOR IN SI"
      CALL MESSAGE(CVAR)
      WRITE(CVAR,"(5X,'ROUGHNESS FACTOR APPLIED TO MAP ',F10.6)")R_FACT
      CALL MESSAGE(CVAR)
      I = 0
      DO IZ = 1,NZ
        DO IX = 1,NX
          I = I + 1
          ! STORING WIDTH AS THE CENTER CELL VALUE MINUS ROUGHESS
          WIDTH(I) = AP_MAP(IZ,IX,0) - R_FACT
          ! CALCULATING RIGHT (5) AND TOP (6) AVERAGE VALUES MINUS ROUGHNESS
          AP_MAP(IZ,IX,5) = 0.5*(AP_MAP(IZ,IX,2)+AP_MAP(IZ,IX,3))-R_FACT
          AP_MAP(IZ,IX,6) = 0.5*(AP_MAP(IZ,IX,4)+AP_MAP(IZ,IX,3))-R_FACT
          ! APPLYING MASK AFTER ROUGHNESS 
          IF (WIDTH(I) <= LOW_MASK) WIDTH(I) = LOW_MASK
          IF (AP_MAP(IZ,IX,5) <= LOW_MASK) AP_MAP(IZ,IX,5) = LOW_MASK
          IF (AP_MAP(IZ,IX,6) <= LOW_MASK) AP_MAP(IZ,IX,6) = LOW_MASK
          ! APPLYING VOXEL TO METER CONVERSION
          WIDTH(I) = WIDTH(I)*VOX_MET
          AP_MAP(IZ,IX,:) = AP_MAP(IZ,IX,:)*VOX_MET
        END DO
      END DO
C
      WRITE(CVAR,2150) ZEROS
      IF (ZEROS > 0) CALL BLANK
      IF (ZEROS > 0) CALL MESSAGE(TRIM(CVAR))          
C
C     OUTPUTTING DATA ABOUT MAP
      CALL BLANK
      CALL MESSAGE("     PROPERTIES OF APERTURE MAP:")
      CALL BLANK
      WRITE(CVAR,2000)'DIAMETER[M]','LENGTH[M]'
      CALL MESSAGE(TRIM(CVAR))
      WRITE(CVAR,2005) DIAM,LENG,NX,NZ
      CALL MESSAGE(TRIM(CVAR))
C
      CALL BLANK
      WRITE(CVAR,2100)MASK
      CALL MESSAGE(CVAR)
      CALL BLANK
      WRITE(CVAR,2175)'MINIMUM, NONZERO',MIN_APER
      CALL MESSAGE(CVAR)
      WRITE(CVAR,2175)'MAXIMUM',MAX_APER
      CALL MESSAGE(CVAR)
      CALL BLANK
      WRITE(CVAR,2125)'WITHOUT MASK APPLIED: ',RAW_APER
      CALL MESSAGE(CVAR)
      WRITE(CVAR,2125)'WITH MASK APPLIED:    ',HOM_APER/VOX_MET
      CALL MESSAGE(CVAR)
C
      IF (PERCENTILE) THEN
        CALL BLANK
        WRITE(CVAR,2200)
        CALL MESSAGE(CVAR)
        WRITE(CVAR,2225)'PERCENTILE','[VOX]','[MM]'
        CALL MESSAGE(CVAR)
        DO I = 1,NPCT
          WRITE(CVAR,2230)PERC_ARR(1,I),PERC_ARR(2,I),
     &                    PERC_ARR(2,I)*VOX_MET*1000
          CALL MESSAGE(CVAR)
        END DO
      END IF
C 
      RETURN
C      
  910 CALL FIELD_ERROR("APERTURE MAP",IFLD)
      CALL MESSAGE("LINE - "//DATA_LINE(1:120)//"...")
      GOTO 1000
C
  930 WRITE(CVAR,2050)'HORIZONTAL',MAXDIM
      CALL MESSAGE(CVAR)
      GOTO 1000
C
  931 WRITE(CVAR,2050)'VERTICAL',MAXDIM
      CALL MESSAGE(CVAR)
      GOTO 1000
C 
 1000 BOK = .FALSE.
      RETURN
C                      
 2000 FORMAT(1X,A17,1X,A19,9X,'NX',8X,'NZ')
 2005 FORMAT(3X,F15.6,5X,F15.6,5X,I6.5,4X,I6.5)
C
 2050 FORMAT(1X,'ERROR - MAXIMUM NUMBER OF ',A,' CELLS IS ',I0)
C
 2100 FORMAT(9X,'NUMBER OF CELLS THAT WERE MASKED: ',I0)
C
 2125 FORMAT(9X,'HOMOGENEOUS APERTURE OF FRACTURE ',A22,F15.6,' VOXELS')
C
 2150 FORMAT(5X,'*** WARNING: ',I0,' CELLS HAD AN APERTURE OF ZERO,',
     &       'FLOW EQUATION MAY FAIL IF TOO LOW OF A MASK WAS USED ***')
C
 2175 FORMAT(9X,A,' APERTURE OF FRACTURE: ',F15.6,' VOXELS')
C
 2200 FORMAT(9X,'APERTURE RANGES BY PERCENTILE')
C
 2225 FORMAT(1X,A18,1X,A19,1X,A19)
C
 2230 FORMAT(12X,F7.3,5X,F15.6,5X,F15.9)
C
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C   
      SUBROUTINE MAP_STATS
C
C     WRITTEN BY: MATTHEW STADELMAN
C
C     DATE WRITTEN: 12/22/2015
C     LAST MODIFIED: 12/31/2015
C
C     THIS PROGRAM CALCULATES VARIOUS STATISTICS ON THE APRETURE MAP
C     BEFORE ANY CONVERSIONS HAVE BEEN APPLIED
C
C ----------------------------------------------------------------------
C     VARIABLE DESCRIPTION
C
C ----------------------------------------------------------------------
      USE TWOD_MODULE
C
      IMPLICIT NONE
      REAL(8),ALLOCATABLE :: VARG(:,:)
      REAL(8) :: MAX_LEN,APER_VAR,SM,SMS,SF
      REAL(8) :: TEST(3)
      INTEGER :: K,IX,IZ
C
      SF = 10.0
      MAX_LEN = FLOAT(MIN(NX,NZ))/2.0
      K = INT(SQRT(FLOAT(NX)**2 + FLOAT(NZ)**2)*SF)
      ALLOCATE(VARG(0:K,5))
C
C     CALCULATING THE RMS OF THE FRACTURE APERTURE
      APER_RMS = 0.0
      APER_DEV = 0.0
      APER_VAR = 0.0
      SMS = 0.0 !SUM OF DIFFERENCES SQUARED
      SM = 0.0  !SUM OF DIFFERENCES
      DO IZ = 1,NZ
        DO IX = 1,NX
          APER_RMS = APER_RMS + AP_MAP(IZ,IX,0)**2
          SM = SM + (AP_MAP(IZ,IX,0) - HOM_APER)
          SMS = SMS + (AP_MAP(IZ,IX,0) - HOM_APER)**2
        END DO
      END DO  
      SM = (SM*SM)*(FLOAT(NX*NZ)**(-1))
      APER_RMS = APER_RMS*FLOAT(NX*NZ)**(-1)
      APER_VAR = (SMS - SM)*(FLOAT(NX*NZ-1)**(-1))
      APER_RMS = SQRT(APER_RMS)*VOX_MET
      APER_DEV = SQRT(APER_VAR)*VOX_MET
C
C     CALCULATING HORIZONTAL VARIOGRAM DATA TO GET X - CORRELATION LENGTH
      VARG(:,:) = 0.0
      TEST(:) = 0.0
      X_CORR = 0.0
      DO K = 1,INT(MAX_LEN)+1
        ! COMPARING TO POINT OFFSET K CELLS RIGHT OF REFERENCE POINT
        DO IX = 1,NX 
          DO IZ = 1,NZ 
            IF ((IX+K) > NX) CYCLE
            VARG(K,1) = VARG(K,1) + 1
            VARG(K,2) = VARG(K,2)+(AP_MAP(IZ,IX,0)-AP_MAP(IZ,IX+K,0))**2
          END DO 
        END DO
        ! CALCULATING AVERAGE LENGTH AND VARIANCE FOR OFFSET K
        IF (VARG(K,1) == 0) CYCLE
        VARG(K,3) =  VARG(K,2)/(VARG(K,1))
        X_CORR = FLOAT(K)*AVG_FACT*VOX_MET
        TEST(1) = ABS(VARG(K,3)/APER_VAR - 0.90)
        IF (VARG(K,3)/APER_VAR > 0.90) THEN
          IF (TEST(2) < TEST(1)) X_CORR = TEST(3)
          EXIT
        END IF
        TEST(2) = TEST(1)
        TEST(3) = X_CORR
      END DO
C
C     CALCULATING VERTICAL VARIOGRAM DATA TO GET Z - CORRELATION LENGTH
      VARG(:,:) = 0.0
      TEST(:) = 0.0
      Z_CORR = 0.0
      DO K = 1,INT(MAX_LEN)+1
        ! COMPARING TO POINT OFFSET K CELLS ABOVE REFERENCE POINT
        DO IX = 1,NX 
          DO IZ = 1,NZ 
            IF ((IZ+K) > NZ) CYCLE
            VARG(K,1) = VARG(K,1) + 1
            VARG(K,2) = VARG(K,2)+(AP_MAP(IZ,IX,0)-AP_MAP(IZ+K,IX,0))**2
          END DO 
        END DO
        ! CALCULATING AVERAGE LENGTH AND VARIANCE FOR OFFSET K
        IF (VARG(K,1) == 0) CYCLE
        VARG(K,3) =  VARG(K,2)/(VARG(K,1))
        Z_CORR = FLOAT(K)*AVG_FACT*VOX_MET
        TEST(1) = ABS(VARG(K,3)/APER_VAR - 0.90)
        IF (VARG(K,3)/APER_VAR > 0.90) THEN
          IF (TEST(2) < TEST(1)) Z_CORR = TEST(3)
          EXIT
        END IF
        TEST(2) = TEST(1)
        TEST(3) = Z_CORR
      END DO
C     
      RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C   
      SUBROUTINE CALC_PERCENTILE(VECTOR,PERC_ARR,NVALS,NPCT)
C
C     WRITTEN BY: MATTHEW STADELMAN
C
C     DATE WRITTEN: 03/02/2015
C     LAST MODIFIED: 08/05/2015
C
C     PROGRAM DESCRIPTION: SORTS AND COUNTS THE INPUT VECTOR DUPLICATE VALUES
C      AND THEN CALCULATES PERCENTILES FROM THE DATA
C     
C ----------------------------------------------------------------------
C     VARIABLE DESCRIPTION: 
C       VECTOR - INPUT VECTOR NEEDING SORTED
C       PERC_ARR - 2-D ARRAY CONTAINING PERCENTILE AND SPOT FOR THE VALUE
C        PERC(1,:) - ALL THE PERCENTILES TO BE CALCULATED
C        PERC(2,:) - ALL OF THE VECTOR VALUES FOR EACH PERCENTILE
C       NVALS -  NUMBER OF VALUES IN VECTOR
C       NPCT - NUMBER OF PERCENTILES TO CALCULATE
C
C ----------------------------------------------------------------------    
      IMPLICIT NONE
      REAL(8) :: VECTOR(*),PERC_ARR(2,*),ST,EN
      REAL(8), ALLOCATABLE :: SORT(:),COUNT(:),COUNT_VAL(:)
      INTEGER :: I,J,K,IV,N,TOT,NVALS,NPCT
C
      ALLOCATE(SORT(NVALS),COUNT(NVALS),COUNT_VAL(NVALS))
      SORT(:) = VECTOR(1:NVALS) !PREVENTS MODIFICATION OF INPUT VECTOR
      COUNT_VAL = 0
C
C     SORTING THE INPUT VECTOR USING THE HEAP SORT METHOD
      CALL HEAP_SORT(SORT,NVALS)
C
C     COUNTING DUPLICATE VALUES
      CALL CPU_TIME(ST)
      IV = 1
      COUNT_VAL(1) = SORT(1)
      COUNT(1:NVALS) = 1
      DO I = 2,NVALS
        IF (COUNT_VAL(IV) .EQ. SORT(I)) THEN 
          COUNT(IV) = COUNT(IV) + 1
          CYCLE
        ELSE
          IV = IV + 1
          COUNT_VAL(IV) = SORT(I)
        END IF
      END DO  
      CALL CPU_TIME(EN)
      N = IV
C
C     CALCULATING PERCENTILES 
      DO I = 1,NPCT
        K = CEILING(PERC_ARR(1,I)/100*FLOAT(NVALS))
        TOT = 0
        DO J = 1,N
          TOT = TOT + INT(COUNT(J))
          IF (TOT > K) EXIT
          IF (J == N) EXIT
        END DO
        PERC_ARR(2,I) = COUNT_VAL(J)
      END DO
C
      RETURN
      END SUBROUTINE  
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C 
      SUBROUTINE HEAP_SORT(VECTOR,N)
C
        IMPLICIT NONE
        REAL(8) :: VECTOR(*),VAL
        INTEGER :: I,J,L,N,IR
        L = N/2+1
        IR = N
        !THE INDEX L WILL BE DECREMENTED FROM ITS INITIAL VALUE DURING THE
        !"HIRING" (HEAP CREATION) PHASE. ONCE IT REACHES 1, THE INDEX IR 
        !WILL BE DECREMENTED FROM ITS INITIAL VALUE DOWN TO 1 DURING THE
        !"RETIREMENT-AND-PROMOTION" (HEAP SELECTION) PHASE.
C
 10     CONTINUE
        IF(L > 1)THEN
          L = L-1
          VAL = VECTOR(L)
        ELSE
          VAL = VECTOR(IR)
          VECTOR(IR) = VECTOR(1)
          IR = IR-1
          IF(IR.EQ.1)THEN
            VECTOR(1) = VAL
            RETURN
          END IF
        END IF
C
        I = L
        J = L+L
20      IF(J.LE.IR)THEN
          IF(J < IR)THEN
            IF(VECTOR(J) < VECTOR(J+1))  J = J+1
          END IF
          IF(VAL < VECTOR(J))THEN
            VECTOR(I) = VECTOR(J)
            I = J; J = J+J
          ELSE
            J = IR+1
          END IF
          GOTO 20
        END IF
C
        VECTOR(I) = VAL
        GOTO 10
C
        RETURN
      END SUBROUTINE HEAP_SORT   
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C   
      SUBROUTINE COEF(BOK)
C
C----------------------------------------------------------------------- 
C
C ----------------------------------------------------------------------
C
      USE TWOD_MODULE
      IMPLICIT NONE
      REAL(8) :: PH,PL,B,BF3,BP3,DBF,DBP,W3,THETA
      INTEGER :: I,IX,IZ
      LOGICAL :: BOK
C  
C     DEFINING VARIABLES
      DX(:) = DIAM/NX
      DZ(:) = LENG/NZ    
      TRX(:,:) = 0.0
      TRZ(:,:) = 0.0 
C
C     DEFINING AN AVERAGE HOMONGENOUS TRANSMISSIVITY
      HOM_TRX = (LENG*HOM_APER**3)/(12.0*DIAM)
      HOM_TRZ = (DIAM*HOM_APER**3)/(12.0*LENG) 
C
C     USING THE STOKES TAPERED PLATE FLOW SOLUTION TO CALCULATE THE TRANS
C     OF THE RIGHT AND TOP INTERFACE OF A GRID BLOCK
      DO IZ = 1,NZ
        DO IX = 1,NX-1
          I = (IZ-1)*NX + IX
          !
          ! SOLVING TAPERED PLATE CORRECTION FOR CELL CENTERS TO INTERFACE
          B = AP_MAP(IZ,IX,5) !WIDTH AT INTERFACE BASED ON CORNER VALUES
          DBP = DX(I)/2  !(DX(I)/2 = DISTANCE FROM CENTER CELL TO INTERFACE IF PLANAR
          THETA = ATAN(ABS(WIDTH(I)-B)/DBP) 
          W3 = (2 * WIDTH(I)**2 * B**2)/(WIDTH(I) + B)
          BP3 = W3 * 3*(TAN(THETA) - THETA)/(TAN(THETA)**3)
          IF (INT(1E9*THETA) == 0) BP3 = W3
          !
          DBF = DX(I+1)/2  !(DX(I+1)/2 = DISTANCE FROM CENTER CELL TO INTERFACE IF PLANAR
          THETA = ATAN(ABS(B-WIDTH(I+1))/DBF) 
          W3 = (2 * B**2 * WIDTH(I+1)**2)/(B + WIDTH(I+1))
          BF3 = W3 * 3*(TAN(THETA) - THETA)/(TAN(THETA)**3)
          IF (INT(1E9*THETA) == 0) BF3 = W3
          !
          TRX(IZ,IX) = (DBP/BP3 + DBP/BF3)**(-1) * (DZ(I)/12)
        END DO
      END DO
C
      DO IZ = 1,NZ-1
        DO IX = 1,NX
          I = (IZ-1)*NX + IX
          !
          ! SOLVING TAPERED PLATE CORRECTION FOR CELL CENTERS TO INTERFACE
          B = AP_MAP(IZ,IX,6) !WIDTH AT INTERFACE BASED ON CORNER VALUES
          DBP = DZ(I)/2  !(DZ(I)/2 = DISTANCE FROM CENTER CELL TO INTERFACE IF PLANAR
          THETA = ATAN(ABS(WIDTH(I)-B)/DBP) 
          W3 = (2 * WIDTH(I)**2 * B**2)/(WIDTH(I) + B)
          BP3 = W3 * 3*(TAN(THETA) - THETA)/(TAN(THETA)**3)
          IF (INT(1E9*THETA) == 0) BP3 = W3
          !
          DBF = DZ(I+NX)/2  !(DZ(I+NX)/2 = DISTANCE FROM CENTER CELL TO INTERFACE IF PLANAR
          THETA = ATAN(ABS(B-WIDTH(I+NX))/DBF) 
          W3 = (2 * B**2 * WIDTH(I+NX)**2)/(B + WIDTH(I+NX))
          BF3 = W3 * 3*(TAN(THETA) - THETA)/(TAN(THETA)**3)
          IF (INT(1E9*THETA) == 0) BF3 = W3
          !
          TRZ(IZ,IX) = (DBP/BP3 + DBP/BF3)**(-1) * (DX(I)/12)
        END DO
      END DO
C
      DO IZ = 1,NZ
        ! HANDLING SPECIAL CASE AT RIGHT SIDE OF FRACTURE
        I = (IZ-1)*NX + NX
        B = AP_MAP(IZ,NX,5) !WIDTH AT INTERFACE BASED ON CORNER VALUES
        DBP = DX(I)/2  !(DX(I)/2 = DISTANCE FROM CENTER CELL TO INTERFACE IF PLANAR
        THETA = ATAN(ABS(WIDTH(I)-B)/DBP) 
        W3 = (2 * WIDTH(I)**2 * B**2)/(WIDTH(I) + B)
        BP3 = W3 * 3*(TAN(THETA) - THETA)/(TAN(THETA)**3)
        IF (INT(1E9*THETA) == 0) BP3 = W3
        !
        TRX(IZ,NX) = (DZ(I)*BP3)/(12.0*DX(I))
      END DO
C
      DO IX = 1,NX
        ! HANDLING SPECIAL CASE AT TOP OF FRACTURE
        I = (NZ-1)*NX + IX
        B = AP_MAP(NZ,IX,6) !WIDTH AT INTERFACE BASED ON CORNER VALUES
        DBP = DZ(I)/2  !(DZ(I)/2 = DISTANCE FROM CENTER CELL TO INTERFACE IF PLANAR
        THETA = ATAN(ABS(WIDTH(I)-B)/DBP) 
        W3 = (2 * WIDTH(I)**2 * B**2)/(WIDTH(I) + B)
        BP3 = W3 * 3*(TAN(THETA) - THETA)/(TAN(THETA)**3)
        IF (INT(1E9*THETA) == 0) BP3 = W3
        !
        TRZ(NZ,IX) = (DZ(I)*BP3)/(12.0*DX(I))
      END DO
C
C     INITALIZING FRACTURE PRESSURE AND PSEUDO-PRESSURE
      FPSB = FPB
      FRAC_PR(:,:) = FPB 
      FRAC_PS(:,:) = FPSB  
      OUTPSB = OUTPB

C
C     CHECKING FLUID TYPE
      IF (IFLUID == 1) THEN !GAS 
C
C       INITALIZING FRACTURE PSEUDO-PRESSURE
        CALL PR_TO_PS(FPB,FPSB,BOK)
        FRAC_PS(:,:) = FPSB   
C
C       INTERPOLATING FOR THE PSEUDO-PRESSURE OF THE OUTFLOW 
        IF (PRESC) THEN
          CALL PR_TO_PS(OUTPB,OUTPSB,BOK)
C
C       CALCULATING INITIAL PRESSURE BOUND FOR RATE CONTROLLED FRACTURE
        ELSEIF (RATEC) THEN        
          OUTRATE = OUTRATE/STD_CONV
          IF ((INDEX(OUTFLOW,'RIGHT')+INDEX(OUTFLOW,'LEFT')) > 0) THEN
            OUTPSB = FPSB - OUTRATE/HOM_TRX
          ELSEIF ((INDEX(OUTFLOW,'TOP')+INDEX(OUTFLOW,'BOTTOM'))>0) THEN
            OUTPSB = FPSB - OUTRATE/HOM_TRZ
          END IF     
          CALL PS_TO_PR(OUTPB,OUTPSB,BOK)
        ELSE
          GOTO 900
        END IF
C
      ELSEIF (IFLUID == 2) THEN  !LIQUID 
C
C       CALCULATING THE INITIAL VISCOSITY FOR THE LIQUID  
        I = INT(FPB/DPR)+1
        IF (I > VALS) I = VALS - 1
        PH = PR(I+1); PL = PR(I)    
        HOM_VISC = (FPB-PL)*(VI(I+1)-VI(I))/(PH-PL)+VI(I)
C
C       ADUSTING TRANSIMISSIBILITY ARRAYS TO INCORPERATE VISCOSITY
        HOM_TRZ = HOM_TRZ/HOM_VISC
        HOM_TRX = HOM_TRX/HOM_VISC
        TRX(:,:) = TRX(:,:)/HOM_VISC
        TRZ(:,:) = TRZ(:,:)/HOM_VISC 
C
C       CALCULATING INITIAL PRESSURE BOUND FOR RATE CONTROLLED FRACTURE
        IF (RATEC) THEN        
          IF ((INDEX(OUTFLOW,'RIGHT')+INDEX(OUTFLOW,'LEFT')) > 0) THEN
            OUTPSB = FPSB - OUTRATE/HOM_TRX
          ELSEIF (INDEX(OUTFLOW,'TOP') > 0) THEN
            OUTPSB = FPSB - OUTRATE/HOM_TRZ
            OUTPSB = FPSB - OUTRATE/HOM_TRZ
          ELSEIF (INDEX(OUTFLOW,'BOTTOM') > 0) THEN
            OUTPSB = FPSB - OUTRATE/HOM_TRZ
            OUTPSB = FPSB - OUTRATE/HOM_TRZ
          END IF  
          IF (OUTPSB < 0) THEN
            CALL BLANK
            CALL MESSAGE(" ERROR NEGATIVE BOUNDARY PRESSURE CALCULATED")
            CALL MESSAGE(" FLOW RATE TOO HIGH")
            GOTO 1000
          END IF
          OUTPB = OUTPSB
        ELSEIF (PRESC) THEN
          OUTPSB = OUTPB
        ELSE
          GOTO 900
        END IF
      ELSE
        CALL MESSAGE("FLUID TYPE MUST BE SPECFIED AS LIQUID OR GAS")
        GOTO 1000
      END IF
C
      RETURN
C
  900 CALL MESSAGE("     ERROR - NO BOUNDARY CONDITION SPECIFIED.")
      GOTO 1000
C
 1000 BOK = .FALSE.
      RETURN
C
      END SUBROUTINE  
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------      
C  
      SUBROUTINE FLOW_BOUNDARY(BOK)
C
C     CREATES A VECTOR OF CELLS THAT HAVE A FLOW BOUNDARY ON THE
C     LEFT SIDE FOR THE 2-D FRACTURE FLOW PROGRAM
C
      USE TWOD_MODULE 
      IMPLICIT NONE 
      INTEGER :: I,IX,IZ
      LOGICAL :: BOK
C
C     
      CALL BLANK
      CALL MESSAGE(" DEFINING BOUNDARY CELL TRANSMISSIBILIES") 
C
C     HANDLING EACH OUTFLOW SIDE CASE
      IF (INDEX(OUTFLOW,'LEFT') > 0) THEN
C
C       DEFINING THE BOUNDARY CONDITIONS FOR EACH SIDE OF THE FRACTURE
        TRX(1:NZ,0) = 2*TRX(1:NZ,1)
        TRX(1:NZ,NX) = 2*TRX(1:NZ,NX) !RIGHT SIDE BOUNDARY
        TRZ(0,1:NX) = 0.0 !BOTTOM ROW
        TRZ(NZ,1:NX) = 0.0 !TOP ROW
        !
        FRAC_PS(:,0) = OUTPSB !EXTRA LEFT COUMN
        FRAC_PS(:,NX+1) = FPSB !EXTRA RIGHT COLUMN
        FRAC_PS(0,:) = FPSB !EXTRA BOTTOM ROW
        FRAC_PS(NZ+1,:) = FPSB !EXTRA TOP ROW
C  
C       DEFINING PBCELLS
        NC = NZ
        DO IZ = 1,NZ
          I = (IZ-1)*NX + 1
          PBCELLS(IZ) = I
        END DO       
      ELSE IF (INDEX(OUTFLOW,'RIGHT') > 0) THEN 
C
C       DEFINING THE BOUNDARY CONDITIONS FOR EACH SIDE OF THE FRACTURE
        TRX(1:NZ,0) = 2*TRX(1:NZ,1)
        TRX(1:NZ,NX) = 2*TRX(1:NZ,NX) !RIGHT SIDE BOUNDARY
        TRZ(0,1:NX) = 0.0 !BOTTOM ROW
        TRZ(NZ,1:NX) = 0.0 !TOP ROW
        !
        FRAC_PS(:,0) = FPSB !EXTRA LEFT COUMN
        FRAC_PS(:,NX+1) = OUTPSB !EXTRA RIGHT COLUMN
        FRAC_PS(0,:) = FPSB !EXTRA BOTTOM ROW
        FRAC_PS(NZ+1,:) = FPSB !EXTRA TOP ROW
C  
C       DEFINING PBCELLS
        NC = NZ
        DO IZ = 1,NZ
          I = (IZ-1)*NX + NX
          PBCELLS(IZ) = I
        END DO  
      ELSE IF (INDEX(OUTFLOW,'TOP') > 0) THEN  
C
C       DEFINING THE BOUNDARY CONDITIONS FOR EACH SIDE OF THE FRACTURE
        TRX(1:NZ,0) = 0.0 !LEFT SIDE BOUNDARY
        TRX(1:NZ,NX) = 0.0 !RIGHT SIDE BOUNDARY
        TRZ(0,1:NX) = 2*TRZ(1,1:NX) !BOTTOM BOUNDARY
        TRZ(NZ,1:NX) = 2*TRZ(NZ,1:NX) !EXTRA TOP ROW
        !
        FRAC_PS(:,0) = FPSB !EXTRA LEFT COUMN
        FRAC_PS(:,NX+1) = FPSB !EXTRA RIGHT COLUMN
        FRAC_PS(0,:) = FPSB !EXTRA BOTTOM ROW
        FRAC_PS(NZ+1,:) = OUTPSB !EXTRA TOP ROW
C  
C       DEFINING PBCELLS
        NC = NX
        DO IX = 1,NX
          I = (NZ-1)*NX + IX
          PBCELLS(IX) = I
        END DO  
      ELSE IF (INDEX(OUTFLOW,'BOTTOM') > 0) THEN 
C
C       DEFINING THE BOUNDARY CONDITIONS FOR EACH SIDE OF THE FRACTURE
        TRX(1:NZ,0) = 0.0 !LEFT SIDE BOUNDARY
        TRX(1:NZ,NX) = 0.0 !RIGHT SIDE BOUNDARY
        TRZ(0,1:NX) = 2*TRZ(1,1:NX) !BOTTOM BOUNDARY
        TRZ(NZ,1:NX) = 2*TRZ(NZ,1:NX) !EXTRA TOP ROW
        !
        FRAC_PS(:,0) = FPSB !EXTRA LEFT COUMN
        FRAC_PS(:,NX+1) = FPSB !EXTRA RIGHT COLUMN
        FRAC_PS(0,:) = OUTPSB !EXTRA BOTTOM ROW
        FRAC_PS(NZ+1,:) = FPSB !EXTRA TOP ROW
C  
C       DEFINING PBCELLS
        NC = NX
        DO IX = 1,NX
          PBCELLS(IX) = IX
        END DO  
      ELSE
        CALL MESSAGE(" INVALID OUTFLOW SIDE ENTERED: "//TRIM(OUTFLOW))
        GOTO 1000
      END IF 
C
      RETURN
C
 1000 BOK = .FALSE.
      RETURN
C
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE SOLVER(AD,AW,AC,AE,AU,RES)
C
      USE TWOD_MODULE
C
      IMPLICIT NONE
      REAL(8), ALLOCATABLE :: DPS(:)
      REAL(8) :: AD(*),AW(*),AC(*),AE(*),AU(*),RES(*)
      INTEGER :: I,IX,IZ
C
      ALLOCATE(DPS(NX*NZ))
      DPS = 0.0;
C
      CALL MESSAGE('     USING D4 SOLVER')
      !CALL GAUSS(AD,AW,AC,AE,AU,RES,NX,NZ,DPS) 
      CALL D4_GAUSS(AD,AW,AC,AE,AU,RES,NX,NZ,DPS)      
      !CALL JACOBI(AD,AW,AC,AE,AU,RES,NX,NZ,DPS)
      !CALL CG(AD,AW,AC,AE,AU,RES,NX,NZ,DPS)
C     
C     UPDATING THE FRACTURE PRESSURE
      DO IZ = 1,NZ
        DO IX = 1,NX
          I = (IZ-1)*NX + IX
          FRAC_PS(IZ,IX) = FRAC_PS(IZ,IX) + DPS(I)
        END DO
      END DO
C
C
      RETURN
C
C
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE PR_TO_PS(P,PSEU,BOK)
C
C     INTERPOLATES FOR THE AGRUMENTS BASED OFF OF THE PRESSURE 
      USE TWOD_MODULE
      IMPLICIT NONE
      REAL(8) :: P,PSEU
      REAL(8) :: PH,PL,SPS
      INTEGER :: I
      
      LOGICAL :: BOK
C     
      IF ((P <= 0) .OR. (P /= P)) GOTO 900
      I = INT(P/DPR)+1
      IF (I > VALS) I = VALS - 1
      PH = PR(I+1); PL = PR(I)
C     CALCULATING PSEUDO-PRESSURE
      SPS = (P-PL)*(SQPS(I+1)-SQPS(I))/(PH-PL)+SQPS(I)
      PSEU = SPS**2   
C        
      RETURN
C
  900 CALL BLANK
      CALL MESSAGE(' **** ERROR NEGATIVE PRESSURE ****')
      BOK = .FALSE.
      RETURN
C
      END SUBROUTINE 
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE PS_TO_PR(P,PSEU,BOK)
C     INTERPOLATES FOR THE PRESSURE BASED OFF OF THE SQRT OF PSEU-PRESSURE
C     FOR THE GIVEN NEWTON ITERATION
      USE TWOD_MODULE
      IMPLICIT NONE
      REAL(8) :: P,PSEU
      REAL(8) :: PH,PL,SPS
      INTEGER :: I
      LOGICAL :: BOK
      CHARACTER(80) :: C80
C      
      IF ((PSEU <= 0) .OR. (PSEU /= PSEU)) GOTO 900
      SPS = SQRT(PSEU)
      I = INT(SPS/DSPS)+1
      IF (I > VALS) I = VALS - 1
      PH = EQSPS(I+1); PL = EQSPS(I)
C     INTERPOLATING FOR THE PRESSURE 
      P = (SPS-PL)*(EQPR(I+1)-EQPR(I))/(PH-PL)+EQPR(I)
C   
      RETURN 
C
  900 CALL BLANK
      C80 = ' **** ERROR - ENCOUNTERED NEGATIVE PSEUDO-PRESSURE ****'
      CALL MESSAGE(C80)
      BOK = .FALSE.
      RETURN
C
      END SUBROUTINE  
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------      
C  
      SUBROUTINE INIT_OUTPUT(BOK)
C
C     OUTPUTS RUN INFO AND INITAL CONDITIONS TO OUTPUT FILES
      USE TWOD_MODULE
      IMPLICIT NONE
      REAL(8) :: CONV(7),X,Y,Z
      INTEGER :: I,N,IX,IZ
      LOGICAL :: BOK  
      CHARACTER(120) :: C120
C
      CONV(1) = PRES_CONV
      CONV(2) = DIM_CONV
      CONV(4) = TIME_CONV
      CONV(5) = RATE_CONV
      CONV(6) = VISC_CONV
      CONV(7) = RHO_CONV
      UNIT_OUT(6) = UNIT_IN(6)
      UNIT_OUT(7) = UNIT_IN(7)
C
      CALL BLANK
      CALL MESSAGE(" INITIALIZING OUTPUT FILES") 
      CALL MESSAGE("     INPUT CONVERSIONS APPLIED")
      CALL UNIT_CONV(1,UNIT(1),UNIT_OUT(1),PRES_CONV,BOK)
      CALL UNIT_CONV(2,UNIT(2),UNIT_OUT(2),DIM_CONV,BOK)
      CALL UNIT_CONV(4,UNIT(4),UNIT_OUT(4),TIME_CONV,BOK)
      CALL UNIT_CONV(5,UNIT(5),UNIT_OUT(5),RATE_CONV,BOK)
      CALL UNIT_CONV(6,UNIT(6),UNIT_OUT(6),VISC_CONV,BOK)
      CALL UNIT_CONV(7,UNIT(7),UNIT_OUT(7),RHO_CONV,BOK)
      IF (.NOT. BOK) GOTO 1000
C
      WRITE(C120,1990)
      CALL MESSAGE(C120)
      WRITE(C120,1980)'UNIT IN','UNIT OUT','CONVERSION'
      CALL MESSAGE(C120)
      WRITE(C120,1990)
      CALL MESSAGE(C120)
      DO I = 1,7
        IF (I == 3) CYCLE
        WRITE(C120,2000)UNIT_IN(I),UNIT(I),CONV(I)
      CALL MESSAGE(C120)
      END DO
      WRITE(C120,1990)
      CALL MESSAGE(C120)
C
      CONV(1) = PRES_CONV
      CONV(2) = DIM_CONV
      CONV(4) = TIME_CONV
      CONV(5) = RATE_CONV
      CONV(6) = VISC_CONV
      CONV(7) = RHO_CONV
C
      CALL BLANK
      CALL MESSAGE("     OUTPUT CONVERSIONS APPLIED")
      WRITE(C120,1990)
      CALL MESSAGE(C120)
      WRITE(C120,1980)'UNIT IN','UNIT OUT','CONVERSION'
      CALL MESSAGE(C120)
      WRITE(C120,1990)
      CALL MESSAGE(C120)
      DO I = 1,7
        IF (I == 3) CYCLE
        WRITE(C120,2000)UNIT(I),UNIT_OUT(I),CONV(I)
      CALL MESSAGE(C120)
      END DO
      WRITE(C120,1990)
      CALL MESSAGE(C120)
C
C     SETTING HEADERS FOR STATISTICS OUTPUT FILE
      CALL SET_HEADER(ISTAT)
C
C     CREATING THE VTK HEADERS 
      CALL BLANK
      CALL MESSAGE("     CREATING THE VTK FILE...")
      WRITE(IVTK,"('# vtk DataFile Version 3.0')")
      WRITE(IVTK,"('vtk output')")
      WRITE(IVTK,"('ASCII')")
      WRITE(IVTK,"('DATASET STRUCTURED_GRID')")
      WRITE(IVTK,"('DIMENSIONS ',I0,1X,I0,1X,I0)")NX+1,NZ+1,2
      WRITE(IVTK,"('POINTS ',I0,' float')")(NX+1)*(NZ+1)*2
C
C     OUPUTTING SURFACE POINTS FOR THE GRID
      AP_MAP = AP_MAP*DIM_CONV
      DO N = -1,1,2
        Z = 0.0
        DO IZ = 1,NZ
          X = 0.0
          Y = N*AP_MAP(IZ,1,1)/2.0
          WRITE(IVTK,"(3(F0.6,' ',:))")X,Y,Z
          DO IX = 1,NX
            I = (IZ - 1)*NX + IX
            X = X + DX(I)
            Y = N*AP_MAP(IZ,IX,2)/2.0
            WRITE(IVTK,"(3(F0.6,' ',:))")X,Y,Z
          END DO
          Z = Z + DZ(I)
        END DO
        !
        X = 0.0
        Y = N*AP_MAP(NZ,1,4)/2.0
        WRITE(IVTK,"(3(F0.6,' ',:))")X,Y,Z
        DO IX = 1,NX
          I = (NZ - 1)*NX + IX
          X = X + DX(I)
          Y = N*AP_MAP(NZ,IX,3)/2.0
          WRITE(IVTK,"(3(F0.6,' ',:))")X,Y,Z
        END DO
      END DO
      CALL MESSAGE("         VTK POINTS OUTPUT TO FILE")  
C   
      RETURN 
C
 1000 BOK = .FALSE.
      RETURN
C
 1980 FORMAT(5X,A10,4X,A10,2X,A15)
 1990 FORMAT(5X,41('-'))
 2000 FORMAT(5X,A10,' -> ',A10,': ',G15.6)    
C
      END SUBROUTINE 
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------      
C
      SUBROUTINE SET_HEADER(IUNIT)
C
      USE TWOD_MODULE
C     
      IMPLICIT NONE
      INTEGER :: IUNIT
C
      WRITE(IUNIT,*)"APERTURE MAP INPUT FILE:    "//TRIM(APM_FILE)
      WRITE(IUNIT,*)"PVT DATA INPUT FILE:    "//TRIM(PVT_FILE)
      WRITE(IUNIT,*)"NX,NZ"
      WRITE(IUNIT,"(I6,',',I6)") NX,NZ
      WRITE(IUNIT,2000) TRIM(UNIT_OUT(2)),TRIM(UNIT_OUT(2)),
     &                  TRIM(UNIT_OUT(2))
      WRITE(IUNIT,2010) LENG*DIM_CONV,DIAM*DIM_CONV,HOM_APER*DIM_CONV
      WRITE(IUNIT,2040) TRIM(UNIT_OUT(3))
      WRITE(IUNIT,2045) HOM_VISC*VISC_CONV,(TEMP-TEMP_CONV)
C
      RETURN
C
 2000 FORMAT('LENGTH [',A,'],DIAMETER [',A,'],MEAN APER [',A,'],')
C
 2010 FORMAT(4(F20.6,',',:))
C
 2040 FORMAT('AVG VISC [CP],TEMP [',A,']')
C
 2045 FORMAT(F10.7,',',F10.4)
C
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C

      SUBROUTINE LNPROC(IN,MAXFLD,MAXLEN,CVAR,CFLD,LFLD,NFLD)
C
C     PURPOSE: THIS SUBROUTINE BREAKS A RECORD INTO IT'S SUBFIELDS. 
C              THE SUBFIELDS ARE SEPARATED BY A COMMA OR ONE OR MORE 
C              BLANKS. EACH EQUAL SIGN IS TREATED AS A SEPARATE SUBFIELD.
C              ALL INFORMATION AFTER A ; IS TREATED AS A COMMENT AND IS 
C              IGNORED A RETURN WITH NFLD EQUAL ZERO INDICATES AN EOF.
C
C
C     SUBROUTINE CALLS :  NONE
C
C     DEFINITION OF ARGUMENTS:
C       IN     - UNIT NUMBER FOR READ
C       MAXFLD - MAXIMUM NUMBER OF FIELDS IN RECORD
C       MAXLEN - MAXIMUM LENGTH OF FIELDS IN RECORD
C       CVAR   - INPUT/OUTPUT DATA STRING
C       CFLD   - CHARACTER ARRAY CONTAINING SUBFIELDS
C       LFLD   - INTEGER ARRAY CONTAINING LENGTHS OF SUBFIELDS
C       NFLD   - NUMBER OF SUBFIELDS
C
C     WRITTEN BY: W. NEAL SAMS
C     LAST MODIFIED: 09/26/2013
C
      IMPLICIT NONE
      INTEGER :: IN,MAXFLD,MAXLEN,NFLD,LENG,I,J
      INTEGER :: LFLD(*)
      CHARACTER(*) :: CFLD(*),CVAR
      CHARACTER(1) :: C1
C
  100 NFLD = 0
      IF(IN > 0) READ(IN,'(A)',END=950) CVAR
      LENG = 0
      DO I = 1,LEN(TRIM(CVAR))+1
        C1 = CVAR(I:I)
        IF(C1 == ';') THEN
          IF(LENG > 0) LFLD(NFLD) = LENG
          GOTO 900
        ELSEIF(C1 == ' ') THEN
          IF(LENG > 0) THEN
            LFLD(NFLD) = LENG
            LENG = -1
          ENDIF
        ELSEIF(C1 == ',') THEN
          IF(LENG > 0) THEN
            LFLD(NFLD) = LENG
            LENG = 0
          ELSEIF(LENG == 0) THEN
            IF(NFLD == MAXFLD) GOTO 950
            NFLD = NFLD + 1
            LFLD(NFLD) = 0
            CFLD(NFLD) = ' '
          ELSE
            LENG = 0
          ENDIF
        ELSEIF(C1 == CHAR(9)) THEN !HOPEFULLY ALLOWING TAB DELIMITERS 
          IF(LENG > 0) THEN
            LFLD(NFLD) = LENG
            LENG = 0
          ELSEIF(LENG == 0) THEN
            IF(NFLD == MAXFLD) GOTO 950
            NFLD = NFLD + 1
            LFLD(NFLD) = 0
            CFLD(NFLD) = ' '
          ELSE
            LENG = 0
          ENDIF
        ELSEIF(C1 == '=') THEN
          IF(LENG > 0) LFLD(NFLD) = LENG
          IF(NFLD == MAXFLD) GOTO 950
          NFLD = NFLD + 1
          LFLD(NFLD) = 1
          CFLD(NFLD) = '='
          LENG = -1
        ELSE
          J = IACHAR(C1)
          IF(J >= 97 .AND. J <= 122) J = J - 32
          C1 = ACHAR(J)
C
          IF(LENG <= 0) THEN
            IF(NFLD == MAXFLD) GOTO 950
            NFLD = NFLD + 1
            LENG = 1
            CFLD(NFLD) = C1
          ELSEIF(LENG < MAXLEN) THEN
            LENG = LENG + 1
            CFLD(NFLD)(LENG:LENG) = C1
          ENDIF
        ENDIF
      ENDDO
  900 IF(IN > 0 .AND. NFLD == 0) GOTO 100
  950 RETURN
      END 
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE UPPER_CASE(C_IN,C_OUT)
C
C     WRITTEN BY: W. NEAL SAMS
C     DATE WRITTEN: 10/04/2013
C
      IMPLICIT NONE
      INTEGER :: I,NC
      CHARACTER(*) :: C_IN,C_OUT
C
      DO I = 1,LEN_TRIM(C_IN)
       NC = ICHAR(C_IN(I:I))
       IF(97 <= NC .AND. NC <=122) NC = NC - 32
       C_OUT(I:I) = CHAR(NC)
      ENDDO
C
      RETURN
      END
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE LOWER_CASE(C_IN,C_OUT)
C
C     WRITTEN BY: W. NEAL SAMS
C     DATE WRITTEN: 10/04/2013
C
      IMPLICIT NONE
      INTEGER :: I,NC
      CHARACTER(*) :: C_IN,C_OUT
C
      DO I = 1,LEN_TRIM(C_IN)
       NC = ICHAR(C_IN(I:I))
       IF(65 <= NC .AND. NC <=90) NC = NC + 32
       C_OUT(I:I) = CHAR(NC)
      ENDDO
C
      RETURN
      END
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE R_JUST(C_IN,C_OUT,NC)
C
C     WRITTEN BY: MATTHEW STADELMAN
C     DATE WRITTEN: 09/17/2015
C
      IMPLICIT NONE
      INTEGER :: I,NC,NW
      CHARACTER(NC) :: C_IN,C_OUT,CVAR
C     
      NW = NC - LEN_TRIM(C_IN) 
      DO I = 1,NW
        CVAR(I:I) = ' '
      END DO
      C_OUT = CVAR(1:NW)//TRIM(C_IN)
C
      RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE MESSAGE(C_OUT)
C
      USE TWOD_MODULE
C
      IMPLICIT NONE      
      CHARACTER(*) :: C_OUT
C
      WRITE(*,'(A)') TRIM(C_OUT)
      WRITE(IOUT,'(A)') TRIM(C_OUT)
C
      RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE BLANK
C
      IMPLICIT NONE
      CHARACTER(1) C1
      DATA C1/' '/
C
      CALL MESSAGE(C1)
C
      RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE ERROR_WHERE(C_IN)
C
C     WRITTEN BY: W. NEAL SAMS
C     DATE WRITTEN: 03/07/2014
C
      USE TWOD_MODULE
C
      IMPLICIT NONE
      CHARACTER(*) :: C_IN
      CHARACTER(MAXLEN) :: C_OUT
C
      CALL BLANK
      C_OUT = '     **** ERROR WHILE READING '//TRIM(C_IN)//' DATA ****'
      CALL MESSAGE(C_OUT)
C
      RETURN
      END
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE INSUFFICIENT_ERROR(CHAR_IN)
C
C     WRITTEN BY: W. NEAL SAMS
C     DATE WRITTEN: 03/07/2014
C
      USE TWOD_MODULE
C
      IMPLICIT NONE
      CHARACTER(*) CHAR_IN
      CHARACTER(MAXLEN) :: C_OUT
C
      CALL ERROR_WHERE(CHAR_IN)
      WRITE(C_OUT,2900)
      CALL MESSAGE(C_OUT)
      RETURN
C
 2900 FORMAT(5X,'**** THE FOLLOWING RECORD CONTAINS INSUFFICIENT '
     &            ,'DATA ****')
      END
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE FIELD_ERROR(CHAR_IN,IFLD)
C
C     WRITTEN BY: W. NEAL SAMS
C     DATE WRITTEN: 03/07/2014
C
      USE TWOD_MODULE
C
      IMPLICIT NONE
      INTEGER :: IFLD
      CHARACTER(*) CHAR_IN
      CHARACTER(MAXLEN) :: C_OUT
C
      CALL ERROR_WHERE(CHAR_IN)
      WRITE(C_OUT,2900) IFLD
      CALL MESSAGE(C_OUT)      
      RETURN
C
 2900 FORMAT(5X,'**** FIELD ',I4,' ON THE FOLLOWING RECORD IS IN '
     &         ,'ERROR ****')
      END
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE EOD_ERROR(CHAR_IN)
C
C     WRITTEN BY: W. NEAL SAMS
C     DATE WRITTEN: 03/08/2014
C
      USE TWOD_MODULE
C
      IMPLICIT NONE
      CHARACTER(*) :: CHAR_IN
      CHARACTER(MAXLEN) :: C_OUT
C
      CALL BLANK
      C_OUT = '     **** END OF DATA WHILE READING '//TRIM(CHAR_IN)// 
     &       ' DATA ****'
      CALL MESSAGE(C_OUT)
C
      RETURN
      END
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE QUIT(LN_NUM)
C
C     WRITTEN BY: MATTHEW STADELMAN
C     DATE WRITTEN: 12/09/2015
C
      IMPLICIT NONE
      INTEGER :: LN_NUM
      CHARACTER(10) :: NUM
      CHARACTER(120) :: C120
C
      WRITE(NUM,'(I10)')LN_NUM
      CALL BLANK
      C120 = 'QUIT CALLED ON LINE '//TRIM(NUM)
      CALL MESSAGE(C120)
      STOP
C
      RETURN
      END
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
