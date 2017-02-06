      MODULE IO_MODULE
C
C     WRITTEN BY: MATTHEW STADELMAN
C     FILE DESCRIPTION: STORES IO RELATED VARIABLES AND SUBROUTINES.
C
C     LAST MODIFIED: 2017/02/05
C ----------------------------------------------------------------------
C               ---- VARIABLE DESCRIPTIONS ----
C   IO VARIABLES
C     SYS_OS - STORES THE TYPE OF THE SYSTEM, EITHER WINDOWS OR POSIX
C     CVAR - GENERAL USE CHARACTER VARIABLE USED TO WRITE MESSAGES TO
C         THE SCREEN AND READ INPUT
C     IINP,IAPM - UNIT NUMBERS OF INPUT FILES : INITIALIZATION FILE AND
C         THE APERTURE MAP
C     IOUT,IPRES - UNIT NUMBERS OF OUTPUT FILES: RUNTIME SUMMARY AND
C         PRESSURE MAP
C     ISTATC, ISTATY - UNIT NUMBERS FOR THE CSV STATISTICS AND YAML
C          STATISTICS FILES
C     IFLOX,IFLOZ,IFLOM - UNIT NUMBERS OF OUTPUT FILES: X-FLOW COMPONENT,
C          Z-FLOW COMPONENET AND FLOW MAGNITUDE FLOW MAPS
C     IMAP,IVTK,IBMD - UNIT NUMBERS OF OUTPUT FILES: APERTURE MAP,
C          LEGACY VTK EXPORT AND BLOCK MESH DICT
C     MASTER - STORES FILE NAME OF INITIALIZATION FILE
C     APM_FILE - STORE FILE NAMES OF APERTURE INPUT FILE
C
C ----------------------------------------------------------------------
C
      USE STRING_MODULE, ONLY : MAXLEN
      PRIVATE
C
C     INPUT IO UNIT NUMBERS
      INTEGER,SAVE :: IINP, IAPM
      CHARACTER(MAXLEN) :: APM_FILE
C
C     OUTPUT IO UNIT NUMBERS
      INTEGER,SAVE :: IOUT ,ISTATC, ISTATY, IPRES
      INTEGER,SAVE :: IFLOX, IFLOZ, IFLOM, IMAP, IVTK
C
C     MODULE EXPORTS
      PUBLIC :: APM_FILE, IINP, IAPM, IOUT ,ISTATC, ISTATY, IPRES
      PUBLIC :: IFLOX, IFLOZ, IFLOM, IMAP, IVTK
      PUBLIC :: OPEN_IO, CLOSE_IO, BLANK, MESSAGE
      PUBLIC :: ERROR_WHERE, INSUFFICIENT_ERROR, FIELD_ERROR
C
      CONTAINS
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE OPEN_IO(BOK)
C
C     WRITTEN BY: MATTHEW STADELMAN
C
C     PROGRAM DESCRIPTION: DEFINES DEFAULT OUPTUT FILE NAMES AND THEN
C         OPENS ALL OF THE INPUT AND OUTPUT FILES.
C
C     LAST MODIFIED: 2016/10/27
C
C     SUBROUTINE CALLS: LNPROC, OPEN_FILE
C
C ----------------------------------------------------------------------
C     VARIABLE DESCRIPTION:
C       NFLD - NUMBER OF FIELDS IN CFLD AND LFLD AFTER A PROCESSING A LINE
C       OVERWRITE - BOOLEAN VALUE STATING WHETHER TO ALLOW FILES TO BE OVERWITTEN
C       APM - LOGICAL TESTING FOR AN APERTURE MAP INPUT
C       BOK - CONTROL VARIABLE USED TO HALT PROGRAM IF A FATAL ERROR IS ENCOUNTERED
C       FLOX_FILE, FLOZ_FILE, FLOM_FILE - FLOW MAP FILE NAMES
C
C ----------------------------------------------------------------------
C
      USE STRING_MODULE, ONLY : MAXFLD, LNPROC, LOWER_CASE
C
      IMPLICIT NONE
      INTEGER :: I, IFLD, NFLD, LFLD(MAXFLD)
      LOGICAL :: BOK, APM, OVERWRITE
      CHARACTER(1) :: SEP
      CHARACTER(MAXLEN) :: PATH
      CHARACTER(MAXLEN) :: MASTER
      CHARACTER(MAXLEN) :: SUM_FILE, STAT_FILE, FLOW_FILE, PRESS_FILE
      CHARACTER(MAXLEN) :: MAP_FILE, VTK_FILE
      CHARACTER(MAXLEN) :: FLOX_FILE, FLOZ_FILE, FLOM_FILE
      CHARACTER(MAXLEN) :: STATC_FILE, STATY_FILE
      CHARACTER(MAXLEN) :: CVAR, CFLD(MAXFLD)
      CHARACTER(MAXLEN), ALLOCATABLE :: OPENED_FILES(:)
C
C     CHECKING FLAG TO DETERMINE PATH SEPARATOR
      SEP = '/'
      IF (WIN64 == 1) SEP = '\'
C
C     VARIABLE INITIALIZATIONS
      APM = .FALSE.
      OVERWRITE = .FALSE.
      ! INPUT UNIT NUMBERS
      IINP  = 10
      IAPM  = 12
      ! OUTPUT UNIT NUMBERS
      ISTATC = IAPM  + 3
      ISTATY = ISTATC + 1
      IMAP  = ISTATY + 1
      IFLOX = IMAP  + 1
      IFLOZ = IFLOX + 1
      IFLOM = IFLOZ + 1
      IPRES = IFLOM + 1
      IVTK  = IPRES + 1
      !
      ALLOCATE(OPENED_FILES(IVTK))
      OPENED_FILES(:) = ''
C
C     DEFAULT FILE NAMES
      PATH = '.'
      WRITE(SUM_FILE, 2100)TRIM(PATH), SEP, 'fracture-log.txt'
      WRITE(STAT_FILE, 2100)TRIM(PATH), SEP, 'fracture-stat.csv'
      WRITE(MAP_FILE, 2100)TRIM(PATH), SEP, 'fracture-aperture.csv'
      WRITE(FLOW_FILE, 2100)TRIM(PATH), SEP, 'fracture-flow.csv'
      WRITE(PRESS_FILE, 2100)TRIM(PATH), SEP, 'fracture-press.csv'
      WRITE(VTK_FILE, 2100)TRIM(PATH), SEP, 'fracture-data.vtk'
C
C     CHECKING FOR A COMMAND LINE INP FILE TO PARSE
      NFLD = COMMAND_ARGUMENT_COUNT()
      IF (NFLD > 0) THEN
        CALL GET_COMMAND_ARGUMENT(1, MASTER)
        WRITE(*, "(A)") ''
        WRITE(*, "(A)") ' USING SUPPLIED INPUT FILE '//TRIM(MASTER)
      ELSE
        WRITE(*, "(A)") 'FATAL ERROR - NO INPUT FILE SUPPLIED'
        GOTO 1000
      END IF
C
      OPEN(UNIT=IINP, FILE=MASTER, ACTION='READ', STATUS='OLD')
      WRITE(*, "(A)") ''
      WRITE(*, "(A)") ' READING INITIALIZATION FILE'
C
C     READING IN FILE NAMES
      DO
        CALL LNPROC(IINP,MAXFLD,MAXLEN,CVAR,CFLD,LFLD,NFLD,'SAME')
        IF (NFLD == 0) EXIT
        IF (INDEX(CFLD(1), 'APER-MAP') > 0) THEN
          IFLD = 2
          IF (NFLD < 2) GOTO 905
          APM_FILE = CFLD(IFLD)
          APM = .TRUE.
        ELSEIF (INDEX(CFLD(1), 'SUMMARY-FILE') > 0) THEN
          IFLD = 2
          IF (NFLD < 2) GOTO 905
          SUM_FILE = CFLD(IFLD)
        ELSEIF (INDEX(CFLD(1), 'STAT-FILE') > 0) THEN
          IFLD = 2
          IF (NFLD < 2) GOTO 905
          STAT_FILE = CFLD(IFLD)
        ELSEIF (INDEX(CFLD(1), 'APER-FILE') > 0) THEN
          IFLD = 2
          IF (NFLD < 2) GOTO 905
          MAP_FILE = CFLD(IFLD)
        ELSEIF (INDEX(CFLD(1), 'FLOW-FILE') > 0) THEN
          IFLD = 2
          IF (NFLD < 2) GOTO 905
          FLOW_FILE = CFLD(IFLD)
        ELSEIF (INDEX(CFLD(1), 'PRESS-FILE') > 0) THEN
          IFLD = 2
          IF (NFLD < 2) GOTO 905
          PRESS_FILE = CFLD(IFLD)
        ELSEIF (INDEX(CFLD(1), 'VTK-FILE') > 0) THEN
          IFLD = 2
          IF (NFLD < 2) GOTO 905
          VTK_FILE = CFLD(IFLD)
          I = INDEX(VTK_FILE, '.', BACK=.TRUE.)
          CALL LOWER_CASE(VTK_FILE(I:), VTK_FILE(I:))
        ELSEIF (INDEX(CFLD(1), 'OVERWRITE') > 0) THEN
          OVERWRITE = .TRUE.
        ELSE
          BACKSPACE(UNIT=IINP)
          EXIT
        END IF
      END DO
C
C     OPENING APERTURE MAP
      IF (APM) THEN
        OPEN(UNIT=IAPM, FILE=APM_FILE, STATUS='OLD')
      ELSE
        CVAR = 'FATAL ERROR - NO APERTURE MAP INPUT FILE PROVIDED'
        CALL MESSAGE(CVAR)
        GOTO 1000
      END IF
C
C     CREATING ADDITIONAL FLOW FILES USING ROOT NAME
      I = INDEX(FLOW_FILE, '.', .TRUE.)
      FLOX_FILE = FLOW_FILE(1:I-1)//'-x'//FLOW_FILE(I:)
      FLOZ_FILE = FLOW_FILE(1:I-1)//'-z'//FLOW_FILE(I:)
      FLOM_FILE = FLOW_FILE(1:I-1)//'-m'//FLOW_FILE(I:)
C
C     CREATING ADDITIONAL STAT FILES USING ROOT NAME
      I = INDEX(STAT_FILE, '.', .TRUE.)
      STATC_FILE = STAT_FILE(1:I)//'csv'
      STATY_FILE = STAT_FILE(1:I)//'yaml'
C
C     OPENING OUTPUT FILES
      CALL OPEN_FILE(IAPM+2, SUM_FILE, OVERWRITE, OPENED_FILES, BOK)
      IOUT  = IAPM + 2 !UPDATING IOUT IF LOG FILE WAS SUCCESSFULLY OPENED
      CALL OPEN_FILE(ISTATC, STATC_FILE, OVERWRITE, OPENED_FILES, BOK)
      CALL OPEN_FILE(ISTATY, STATY_FILE, OVERWRITE, OPENED_FILES, BOK)
      CALL OPEN_FILE(IMAP, MAP_FILE, OVERWRITE, OPENED_FILES, BOK)
      CALL OPEN_FILE(IFLOX, FLOX_FILE, OVERWRITE, OPENED_FILES, BOK)
      CALL OPEN_FILE(IFLOZ, FLOZ_FILE, OVERWRITE, OPENED_FILES, BOK)
      CALL OPEN_FILE(IFLOM, FLOM_FILE, OVERWRITE, OPENED_FILES, BOK)
      CALL OPEN_FILE(IPRES, PRESS_FILE, OVERWRITE, OPENED_FILES, BOK)
      CALL OPEN_FILE(IVTK, VTK_FILE, OVERWRITE, OPENED_FILES, BOK)
      IF (.NOT. BOK) GOTO 1000
C
      CALL MESSAGE('     IO INITIALIZED')
      RETURN
C
  905 CALL INSUFFICIENT_ERROR('FILE NAME')
      CALL MESSAGE(CVAR)
      GOTO 1000
C
 1000 BOK = .FALSE.
      ! REMOVING ANY SUCCESSFULLY OPENED FILES
      DO I = 1, SIZE(OPENED_FILES)
          IF (TRIM(OPENED_FILES(I)) == '') CYCLE
          WRITE(CVAR, 2000)TRIM(OPENED_FILES(I))
          CLOSE(I)
          CALL EXECUTE_COMMAND_LINE(CVAR)
      END DO
      !
      RETURN
C
 2000 FORMAT('rm "', A, '"')
C
 2100 FORMAT(A, A, A)
C
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE CLOSE_IO
C
C     WRITTEN BY: MATTHEW STADELMAN
C
C     PROGRAM DESCRIPTION: CLOSES ALL OUTPUT FILES
C
C     LAST MODIFIED: 2016/10/12
C
C     SUBROUTINE CALLS: NONE
C ----------------------------------------------------------------------
C     VARIABLE DESCRIPTION:
C
C ----------------------------------------------------------------------
C
      IMPLICIT NONE
C
      CLOSE(ISTATC)
      CLOSE(ISTATY)
      CLOSE(IMAP)
      CLOSE(IFLOX)
      CLOSE(IFLOZ)
      CLOSE(IFLOM)
      CLOSE(IPRES)
      CLOSE(IVTK)
      !
      CALL BLANK
      CALL MESSAGE(" OUTPUT FILES CLOSED")
      CLOSE(IOUT)
C
      RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE OPEN_FILE(IUNIT, NAME, OVERWRITE, OPENED_FILES, BOK)
C
C     WRITTEN BY: MATTHEW STADELMAN
C
C     PROGRAM DESCRIPTION: HANDLES OPENING OF OUPUT FILES WITH ERROR CHECKING
C
C     LAST MODIFIED: 2016/10/27
C
C     SUBROUTINE CALLS: NONE
C
C ----------------------------------------------------------------------
C     VARIABLE DESCRIPTION:
C       IUNIT - UNIT NUMBER OF FILE TO OPEN
C       IO - ERROR STATUS NUMBER IF OPENING OF FILE FAILS
C       OVERWRITE - BOOLEAN VALUE STATING WHETHER TO ALLOW FILE TO BE OVERWITTEN
C       BOK - CONTROL VARIABLE USED TO HALT PROGRAM IF A FATAL ERROR IS ENCOUNTERED
C       STAT - HOW TO OPEN FILE
C       NAME - FILE TO OPEN'S NAME
C       CVAR - GENERAL PURPOSE OUTPUT STRING
C
C ----------------------------------------------------------------------
C
      IMPLICIT NONE
      INTEGER :: IUNIT, IO
      LOGICAL :: OVERWRITE, BOK
      CHARACTER(80)  :: FSTAT
      CHARACTER(300) :: CVAR
      CHARACTER(*)   :: NAME, OPENED_FILES(*)
C
C     SETTING VARS
      FSTAT = 'NEW'
      IF (OVERWRITE) FSTAT = 'REPLACE'
C
C     ATTEMPTING TO OPEN FILE
      IF (OVERWRITE) THEN
        OPEN (UNIT=IUNIT, IOSTAT=IO, FILE=NAME, STATUS=FSTAT, ERR=900)
      ELSE
        OPEN (UNIT=IUNIT, IOSTAT=IO, FILE=NAME, STATUS=FSTAT, ERR=920)
      END IF
      OPENED_FILES(IUNIT) = NAME
C
      RETURN
C
C     FORMATTING
C
  500 FORMAT('IO ERROR: ', I0, ' ATTEMPTING TO OPEN: ', A)
C
  600 FORMAT(' SPECIFY "OVERWRITE" IN THE INITIALIZATION ',
     &       'FILE OR USE A DIFFERENT NAME FOR OUTPUT FILE: ', A)
C
  900 WRITE(*, "(1X)")
      WRITE(CVAR, 500) IO, TRIM(NAME(1:120))
      WRITE(*, "(A)") CVAR
      GOTO 1000
C
  920 WRITE(*, "(1X)")
      WRITE(*, "('FILE: ', A, ' ALREADY EXISTS')") TRIM(NAME(1:120))
      WRITE(CVAR, 600) TRIM(NAME)
      WRITE(*, "(A)") CVAR
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
      SUBROUTINE MESSAGE(C_OUT)
C
C     WRITTEN BY: MATTHEW STADELMAN
C
C     DATE WRITTEN:  2015/03/02
C     LAST MODIFIED: 2016/07/14
C
C     PROGRAM DESCRIPTION: PRINTS MESSAGES TO SCREEN AND SCREEN LOG FILE
C
C     SUBROUTINE CALLS: NONE
C
C ----------------------------------------------------------------------
C     VARIABLE DESCRIPTION:
C       C_OUT - STRING TO PRINT
C
C ----------------------------------------------------------------------
C
      IMPLICIT NONE
      CHARACTER(*) :: C_OUT
C
      WRITE(*, '(A)') TRIM(C_OUT)
      IF (IOUT /= 6) WRITE(IOUT, '(A)') TRIM(C_OUT)
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
C     WRITTEN BY: W. NEAL SAMS
C     DATE WRITTEN: 10/04/2013
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
      IMPLICIT NONE
      CHARACTER(*) :: C_IN
      CHARACTER(MAXLEN) :: C_OUT
C
      CALL BLANK
      C_OUT = '     **** ERROR WHILE READING '//TRIM(C_IN)//' DATA ****'
      CALL MESSAGE(C_OUT)
C
      RETURN
      END SUBROUTINE
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
      IMPLICIT NONE
      CHARACTER(*) CHAR_IN
      CHARACTER(MAXLEN) :: C_OUT
C
      CALL ERROR_WHERE(CHAR_IN)
      WRITE(C_OUT, 2900)
      CALL MESSAGE(C_OUT)
      RETURN
C
 2900 FORMAT(5X, '**** THE FOLLOWING RECORD CONTAINS INSUFFICIENT '
     &            , 'DATA ****')
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE FIELD_ERROR(CHAR_IN, IFLD)
C
C     WRITTEN BY: W. NEAL SAMS
C     DATE WRITTEN: 03/07/2014
C
      IMPLICIT NONE
      INTEGER :: IFLD
      CHARACTER(*) CHAR_IN
      CHARACTER(MAXLEN) :: C_OUT
C
      CALL ERROR_WHERE(CHAR_IN)
      WRITE(C_OUT, 2900) IFLD
      CALL MESSAGE(C_OUT)
      RETURN
C
 2900 FORMAT(5X, '**** FIELD ', I4, ' ON THE FOLLOWING RECORD IS IN '
     &         , 'ERROR ****')
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      END MODULE
