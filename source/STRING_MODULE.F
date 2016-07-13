      MODULE STRING_MODULE
C
C     WRITTEN BY: MATTHEW STADELMAN
C     FILE DESCRIPTION: STORES VARIABLES AND SUBROUTINES FOR
C         MANIPULATING STRINGS.
C
C     LAST MODIFIED: 2016/07/12
C ----------------------------------------------------------------------
C               ---- VARIABLE DESCRIPTIONS ----
C   LNPROC PARAMETERS
C     MAXFLD - MAXIMUM NUMBER OF FIELDS A LINE AND HAVE
C     MAXLEN - MAXIMUM LENGTH OF A CHARACTER VARIABLE IN THE PROGRAM
C     LFLD - STORES THE LENGTH OF EACH CHARACTER STRING IN CFLD
C     CFLD - STORES THE STRING IN EACH FIELD
C
C ----------------------------------------------------------------------
C
      PUBLIC
C
C     LNPROC PARAMETERS
      INTEGER :: MAXFLD, MAXLEN
      PARAMETER (MAXFLD = 100,MAXLEN = 256)
      INTEGER,SAVE :: LFLD(MAXFLD)
      CHARACTER(MAXLEN),SAVE :: CFLD(MAXFLD)
C
      CONTAINS
C
C     ------------------------------------------------------------------
      SUBROUTINE UPPER_CASE(C_IN,C_OUT)
        !
        ! WRITTEN BY: W. NEAL SAMS
        ! DATE WRITTEN: 10/04/2013
        !
        IMPLICIT NONE
        INTEGER :: I,NC
        CHARACTER(*) :: C_IN,C_OUT
        !
        DO I = 1,LEN_TRIM(C_IN)
         NC = ICHAR(C_IN(I:I))
         IF(97 <= NC .AND. NC <=122) NC = NC - 32
         C_OUT(I:I) = CHAR(NC)
        ENDDO
        !
        RETURN
      END SUBROUTINE
C     ------------------------------------------------------------------
      SUBROUTINE LOWER_CASE(C_IN,C_OUT)
        !
        ! WRITTEN BY: W. NEAL SAMS
        ! DATE WRITTEN: 10/04/2013
        !
        IMPLICIT NONE
        INTEGER :: I,NC
        CHARACTER(*) :: C_IN,C_OUT
        !
        DO I = 1,LEN_TRIM(C_IN)
         NC = ICHAR(C_IN(I:I))
         IF(65 <= NC .AND. NC <=90) NC = NC + 32
         C_OUT(I:I) = CHAR(NC)
        ENDDO
        !
        RETURN
      END SUBROUTINE
C     ------------------------------------------------------------------
      SUBROUTINE R_JUST(C_IN,C_OUT,NC)
        !
        ! WRITTEN BY: MATTHEW STADELMAN
        ! DATE WRITTEN: 2015/09/17
        !
        IMPLICIT NONE
        INTEGER :: I,NC,NW
        CHARACTER(NC) :: C_IN,C_OUT,CVAR
       !
        NW = NC - LEN_TRIM(C_IN)
        DO I = 1,NW
          CVAR(I:I) = ' '
        END DO
        C_OUT = CVAR(1:NW)//TRIM(C_IN)
        !
        RETURN
      END SUBROUTINE
C     ------------------------------------------------------------------
      SUBROUTINE LNPROC(IN,MAXFLD,MAXLEN,CVAR,CFLD,LFLD,NFLD,CASE)
        !
        ! PURPOSE: THIS SUBROUTINE BREAKS A RECORD INTO IT'S SUBFIELDS.
        !          THE SUBFIELDS ARE SEPARATED BY A COMMA OR ONE OR MORE
        !          BLANKS. EACH EQUAL SIGN IS TREATED AS A SEPARATE SUBFIELD.
        !          ALL INFORMATION AFTER A ; IS TREATED AS A COMMENT AND IS
        !          IGNORED A RETURN WITH NFLD EQUAL ZERO INDICATES AN EOF.
        !          IF A DOUBLE QUOTE (") IS ENCOUNTED ALL DATA BETWEEN THE
        !          QUOTES IS TREATED AS IS WITH NO DELIMITERS UNTIL A SECOND
        !          DOUBLE QUOTE.
        !
        !
        ! SUBROUTINE CALLS :  NONE
        !
        ! DEFINITION OF ARGUMENTS:
        ! IN     - UNIT NUMBER FOR READ
        ! MAXFLD - MAXIMUM NUMBER OF FIELDS IN RECORD
        ! MAXLEN - MAXIMUM LENGTH OF FIELDS IN RECORD
        ! CVAR   - INPUT/OUTPUT DATA STRING
        ! CFLD   - CHARACTER ARRAY CONTAINING SUBFIELDS
        ! LFLD   - INTEGER ARRAY CONTAINING LENGTHS OF SUBFIELDS
        ! NFLD   - NUMBER OF SUBFIELDS
        !
        ! WRITTEN BY:  W. NEAL SAMS
        ! MODIFIED BY: MATTHEW A. STADELMAN
        ! LAST MODIFIED: 07/12/2016
        !
        IMPLICIT NONE
        INTEGER :: IN,MAXFLD,MAXLEN,NFLD,LENG,I,J
        INTEGER :: LFLD(*)
        LOGICAL :: QUOTED = .FALSE.
        CHARACTER(80) :: SET_CASE = 'UPPER'
        CHARACTER(*),INTENT(IN),OPTIONAL :: CASE
        CHARACTER(*) :: CFLD(*),CVAR
        CHARACTER(1) :: C1
        !
        IF (PRESENT(CASE)) SET_CASE = TRIM(CASE)
        CALL UPPER_CASE(SET_CASE,SET_CASE)
        !
  100   NFLD = 0
        !
        ! READING AND SETTING CASE OF LINE
        IF(IN > 0) READ(IN,'(A)',END=950) CVAR
        IF (INDEX(SET_CASE,'UP') > 0) CALL UPPER_CASE(CVAR,CVAR)
        IF (INDEX(SET_CASE,'LO') > 0) CALL LOWER_CASE(CVAR,CVAR)
        !
        LENG = 0
        DO I = 1,LEN(TRIM(CVAR))+1
          C1 = CVAR(I:I)
          !
          IF (QUOTED) THEN
            IF (C1 == '"') THEN
              QUOTED = .FALSE.
            ELSE
              J = IACHAR(C1)
              IF(J >= 97 .AND. J <= 122) J = J - 32
              C1 = ACHAR(J)
              !
              IF(LENG <= 0) THEN
                IF(NFLD == MAXFLD) GOTO 950
                NFLD = NFLD + 1
                LENG = 1
                CFLD(NFLD) = C1
              ELSEIF(LENG < MAXLEN) THEN
                LENG = LENG + 1
                CFLD(NFLD)(LENG:LENG) = C1
              ENDIF
            END IF
          !
          ELSEIF(C1 == ';') THEN
            IF(LENG > 0) LFLD(NFLD) = LENG
            GOTO 900
          ELSEIF(C1 == '"') THEN
              QUOTED = .TRUE.
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
          ELSEIF(C1 == CHAR(9)) THEN !TAB DELIMITER
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
            !
            IF(LENG <= 0) THEN
              IF(NFLD == MAXFLD) GOTO 950
              NFLD = NFLD + 1
              LENG = 1
              CFLD(NFLD) = C1
            ELSEIF(LENG < MAXLEN) THEN
              LENG = LENG + 1
              CFLD(NFLD)(LENG:LENG) = C1
            ENDIF
          ENDIF !END CHAR TESTING LOOP
        END DO
        !
  900   IF(IN > 0 .AND. NFLD == 0) GOTO 100
        !
  950   RETURN
      END SUBROUTINE
C     ------------------------------------------------------------------
      END MODULE