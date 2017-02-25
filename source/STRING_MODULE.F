      MODULE STRING_MODULE
C
C     WRITTEN BY: MATTHEW STADELMAN
C     FILE DESCRIPTION: STORES VARIABLES AND SUBROUTINES FOR
C         MANIPULATING STRINGS.
C
C     LAST MODIFIED: 2017/02/25
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
C
      CONTAINS
C
C     ------------------------------------------------------------------
      SUBROUTINE UPPER_CASE(C_IN, C_OUT)
        !
        ! WRITTEN BY: W. NEAL SAMS
        ! DATE WRITTEN: 10/04/2013
        ! MODIFIED BY: MATTHEW STADELMAN
        ! LAST MODIFIED: 02/25/2017
        !
        IMPLICIT NONE
        CHARACTER(*), INTENT(IN OUT) :: C_IN
        CHARACTER(*), INTENT(OUT), OPTIONAL :: C_OUT
        CHARACTER(LEN_TRIM(C_IN)) :: TMP
        !
        INTEGER :: I,NC
        !
        DO I = 1,LEN_TRIM(C_IN)
         NC = ICHAR(C_IN(I:I))
         IF(97 <= NC .AND. NC <=122) NC = NC - 32
         TMP(I:I) = CHAR(NC)
        ENDDO
        !
        IF (.NOT. PRESENT(C_OUT)) THEN
          C_IN = TMP
        ELSE
          C_OUT = TMP
        END IF
        !
        RETURN
      END SUBROUTINE
C     ------------------------------------------------------------------
      SUBROUTINE LOWER_CASE(C_IN, C_OUT)
        !
        ! WRITTEN BY: W. NEAL SAMS
        ! DATE WRITTEN: 10/04/2013
        ! MODIFIED BY: MATTHEW STADELMAN
        ! LAST MODIFIED: 02/25/2017
        !
        IMPLICIT NONE
        CHARACTER(*), INTENT(IN OUT) :: C_IN
        CHARACTER(*), INTENT(OUT), OPTIONAL :: C_OUT
        CHARACTER(LEN_TRIM(C_IN)) :: TMP
        !
        INTEGER :: I,NC
        !
        DO I = 1,LEN_TRIM(C_IN)
         NC = ICHAR(C_IN(I:I))
         IF(65 <= NC .AND. NC <=90) NC = NC + 32
         TMP(I:I) = CHAR(NC)
        ENDDO
        !
        IF (.NOT. PRESENT(C_OUT)) THEN
          C_IN = TMP
        ELSE
          C_OUT = TMP
        END IF
        !
        RETURN
      END SUBROUTINE
C     ------------------------------------------------------------------
      SUBROUTINE R_JUST(C_IN, C_OUT)
        !
        ! WRITTEN BY: MATTHEW STADELMAN
        ! DATE WRITTEN: 2015/09/17
        ! LAST MODIFIED: 2017/02/25
        !
        IMPLICIT NONE
        CHARACTER(*), INTENT(IN OUT) :: C_IN
        CHARACTER(*), INTENT(OUT), OPTIONAL :: C_OUT
        !
        INTEGER :: I, NW
        CHARACTER(LEN(C_IN)) :: TMP
        !
        ! ADDING WHITESPACE TO FRONT OF STRING
        NW = LEN(C_IN) - LEN_TRIM(C_IN)
        FORALL(I = 1:NW) TMP(I:I) = ' '
        !
        ! APPENDING REMAINDER OF STRING
        TMP = TMP(1:NW) // TRIM(C_IN)
        !
        IF (.NOT. PRESENT(C_OUT)) THEN
          C_IN = TMP
        ELSE
          C_OUT = TMP
        END IF
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
        !
        INTEGER, INTENT(IN) :: IN,MAXFLD,MAXLEN
        INTEGER, INTENT(OUT) :: NFLD, LFLD(:)
        CHARACTER(*), INTENT(OUT) :: CFLD(:), CVAR
        CHARACTER(*), INTENT(IN), OPTIONAL :: CASE
        !
        INTEGER :: LENG, I
        LOGICAL :: QUOTED = .FALSE.
        CHARACTER(80) :: SET_CASE
        CHARACTER(1) :: C1
        !
        SET_CASE = 'UPPER'
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
        DO I = 1,LEN_TRIM(CVAR)+1
          C1 = CVAR(I:I)
          !
          IF (QUOTED) THEN
            IF (C1 == '"') THEN
              QUOTED = .FALSE.
            ELSE
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
            IF(LENG > 0) THEN
              LFLD(NFLD) = LENG
              LENG = -1
            ENDIF
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
