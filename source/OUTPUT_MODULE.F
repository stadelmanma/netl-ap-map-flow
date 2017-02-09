      MODULE OUTPUT_MODULE
C
C     WRITTEN BY: MATTHEW STADELMAN
C     FILE DESCRIPTION: STORES OUTPUT RELATED VARIABLES AND SUBROUTINES.
C
C     LAST MODIFIED: 2017/02/08
C ----------------------------------------------------------------------
C               ---- VARIABLE DESCRIPTIONS ----
C
C ----------------------------------------------------------------------
C
      PRIVATE
C
      INTERFACE CALC_PERCENTILE
        MODULE PROCEDURE CALC_PERCENTILE_1D, CALC_PERCENTILE_2D
      END INTERFACE
C
C     MODULE EXPORTS
      PUBLIC :: CALC_PERCENTILE, WRITE_PERCENTILE
      PUBLIC :: WRITE_ONED_ARRAY, WRITE_VTK_DATA
C
      CONTAINS
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE CALC_PERCENTILE_2D(DATA_MAP, PERC_ARR)
        !
        ! FLATTENS 2-D DATA MAP INTO A VECTOR AND PASSES IT OFF
        !
        IMPLICIT NONE
        REAL(8), INTENT(IN) :: DATA_MAP(:, :)
        REAL(8), INTENT(INOUT) :: PERC_ARR(:, :)
        !
        REAL(8), ALLOCATABLE :: VECTOR(:)
        INTEGER :: NVALS
        !
        NVALS = SIZE(DATA_MAP)
        ALLOCATE(VECTOR(NVALS))
        !
        ! ORDER DOESN'T MATTER HERE SO RESHAPE IS SAFE TO USE
        VECTOR = RESHAPE(DATA_MAP, [NVALS])
        CALL CALC_PERCENTILE(VECTOR, PERC_ARR)
        !
        RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE CALC_PERCENTILE_1D(VECTOR, PERC_ARR)
C
C     WRITTEN BY: MATTHEW STADELMAN
C
C     DATE WRITTEN:  2015/03/02
C     LAST MODIFIED: 2017/02/08
C
C     PROGRAM DESCRIPTION: SORTS AND COUNTS THE INPUT VECTOR DUPLICATE VALUES
C      AND THEN CALCULATES PERCENTILES FROM THE DATA
C
C     SUBROUTINE CALLS: HEAP_SORT
C
C ----------------------------------------------------------------------
C     VARIABLE DESCRIPTION:
C       VECTOR - UNSORTED INPUT VECTOR
C       SORT - COPY OF INPUT VECTOR THAT GET SORTED TO PRESREVE INPUT VECTOR'S ORDER
C       COUNTS - STORES THE NUMBER OF TIMES A VALUE APPEARS IN SORT
C       COUNT_VAL - STORES A VERSION OF SORT WITH ALL DUPLICATES REMOVED
C       PERC_ARR - 2-D ARRAY CONTAINING PERCENTILE AND SPOT FOR THE VALUE
C       PERC(1,:) - ALL THE PERCENTILES TO BE CALCULATED
C       PERC(2,:) - ALL OF THE VECTOR VALUES FOR EACH PERCENTILE
C       NVALS -  NUMBER OF VALUES IN VECTOR
C       NPCT - NUMBER OF PERCENTILES TO CALCULATE
C
C ----------------------------------------------------------------------
C
      IMPLICIT NONE
      REAL(8), INTENT(IN) :: VECTOR(:)
      REAL(8), INTENT(INOUT) :: PERC_ARR(:, :)
      !
      REAL(8), ALLOCATABLE :: SORT(:), COUNTS(:), COUNT_VAL(:)
      INTEGER :: I ,J, K, IV, N, TOT, NVALS, NPCT
      NVALS = SIZE(VECTOR)
      NPCT = SIZE(PERC_ARR, DIM=2)
C
      ALLOCATE(SORT(NVALS),COUNTS(NVALS),COUNT_VAL(NVALS))
      SORT(:) = VECTOR(1:NVALS) !PREVENTS MODIFICATION OF INPUT VECTOR
      COUNT_VAL(:) = 0
C
C     SORTING THE INPUT VECTOR USING THE HEAP SORT METHOD
      CALL HEAP_SORT(SORT)
C
C     COUNTING DUPLICATE VALUES AND CREATING A UNIQUE VALUED VECTOR
      IV = 1
      COUNT_VAL(1) = SORT(1)
      COUNTS(1:NVALS) = 1
      DO I = 2,NVALS
        IF (COUNT_VAL(IV) .EQ. SORT(I)) THEN
          COUNTS(IV) = COUNTS(IV) + 1
          CYCLE
        ELSE
          IV = IV + 1
          COUNT_VAL(IV) = SORT(I)
        END IF
      END DO
      N = IV
C
C     CALCULATING PERCENTILES
      DO I = 1,NPCT
        K = CEILING(PERC_ARR(1,I)/100*FLOAT(NVALS))
        TOT = 0
        DO J = 1,N
          TOT = TOT + INT(COUNTS(J))
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
      SUBROUTINE WRITE_PERCENTILE(PERC_ARR, TITLE, UNIT)
C
C     WRITTEN BY: MATTHEW STADELMAN
C
C     LAST MODIFIED: 2017/02/08
C
C     PROGRAM DESCRIPTION: OUTPUTS A PERCENTILE IN STANDARD FORMAT
C
C     SUBROUTINE CALLS: BLANK, MESSAGE
C
C ----------------------------------------------------------------------
C     VARIABLE DESCRIPTION:
C       UNIT - UNITS ON THE PERCENTILE VALUES
C       TITLE - HEADER OF THE PERCENTILE TABLE
C       PERC_ARR - 2-D ARRAY CONTAINING PERCENTILE % AND VALUE
C
C ----------------------------------------------------------------------
C
      USE IO_MODULE, ONLY : BLANK, MESSAGE
C
      IMPLICIT NONE
      REAL(8), INTENT(IN) :: PERC_ARR(:, :)
      CHARACTER(*), INTENT(IN) :: TITLE, UNIT
      !
      INTEGER :: I, NPCT
      CHARACTER(80) :: UNIT_STR, CVAR
      !
      NPCT = SIZE(PERC_ARR, DIM=2)
      WRITE(UNIT_STR,"('[',A,']')") TRIM(UNIT)
C
C     WRITING PERCENTLE HEADERS
      CALL BLANK
      WRITE(CVAR,2100)
      CALL MESSAGE(CVAR)
      WRITE(CVAR,2000) TRIM(TITLE)
      CALL MESSAGE(CVAR)
      WRITE(CVAR,2100)
      CALL MESSAGE(CVAR)
      WRITE(CVAR,2200) 'PERCENTILE', TRIM(UNIT_STR)
      CALL MESSAGE(CVAR)
      WRITE(CVAR,2100)
      CALL MESSAGE(CVAR)
C
C     WRITING OUT PERCENTLE DATA
      DO I = 1, NPCT
        WRITE(CVAR,2300) PERC_ARR(1, I), PERC_ARR(2, I)
        CALL MESSAGE(CVAR)
      END DO
      WRITE(CVAR,2100)
      CALL MESSAGE(CVAR)
C
      RETURN
C
C     FORMATS
C
 2000 FORMAT(9X,A,1X,'RANGES')
C
 2100 FORMAT(9X,32('-'))
C
 2200 FORMAT(1X,A18,3X,'|',A17)
C
 2300 FORMAT(9X,'|',2X,F7.3,3X,'|',1X,F15.6,1X,'|')
C
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE HEAP_SORT(VECTOR)
C
C     SUBROUTINE CALLS: NONE
C
C ----------------------------------------------------------------------
C     VARIABLE DESCRIPTION:
C       VECTOR - UNSORTED INPUT VECTOR
C       VAL - VALUE AT A GIVEN INDEX OF VECTOR
C
C ----------------------------------------------------------------------
C
      IMPLICIT NONE
      REAL(8), INTENT(INOUT) :: VECTOR(:)
      !
      REAL(8) :: VAL
      INTEGER :: I, J, L, N, IR
      N = SIZE(VECTOR)
      L = N/2+1
      IR = N
      VAL = -1.0
      ! THE INDEX L WILL BE DECREMENTED FROM ITS INITIAL VALUE DURING THE
      !"HIRING" (HEAP CREATION) PHASE. ONCE IT REACHES 1, THE INDEX IR
      ! WILL BE DECREMENTED FROM ITS INITIAL VALUE DOWN TO 1 DURING THE
      !"RETIREMENT-AND-PROMOTION" (HEAP SELECTION) PHASE.
C
      DO WHILE (IR > 1)
        IF(L > 1)THEN
          L = L-1
          VAL = VECTOR(L)
        ELSE
          VAL = VECTOR(IR)
          VECTOR(IR) = VECTOR(1)
          IR = IR-1
        END IF
C
        I = L
        J = L+L
        DO WHILE (J <= IR)
          IF(J < IR)THEN
            IF(VECTOR(J) < VECTOR(J+1))  J = J+1
          END IF
          !
          IF (VAL < VECTOR(J)) THEN
            VECTOR(I) = VECTOR(J)
            I = J; J = J+J
          ELSE
            J = IR+1
          END IF
        END DO
C
        VECTOR(I) = VAL
      END DO
      VECTOR(1) = VAL
C
      RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE WRITE_ONED_ARRAY(IUNIT, DATA_ARRAY, NX, NZ, FMT_STR)
C
C     WRITTEN BY: MATTHEW STADELMAN
C
C     LAST MODIFIED: 2016/07/13
C
C     SUBROUTINE DESCRIPTION: OUTPUTS A VECTOR INTO A 2-D DATA MAP
C
C     SUBROUTINE CALLS: NONE
C
C ----------------------------------------------------------------------
C     VARIABLE DESCRIPTION:
C       IUNIT - FILE UNIT NUMBER
C       DATA_ARRAY - DATA VECTOR TO OUTPUT
C       NX,NZ - DATA EXTENTS ALONG EACH AXIS
C       FMT_STR - FORMAT STRING TO OUTPUT DATA WITH
C
C ----------------------------------------------------------------------
C
      IMPLICIT NONE
      REAL(8), INTENT(IN) :: DATA_ARRAY(:)
      INTEGER, INTENT(IN) :: IUNIT, NX, NZ
      CHARACTER(*), INTENT(IN) :: FMT_STR
      !
      INTEGER :: IZ, I, J
C
      DO IZ = 0, NZ - 1
        I = IZ * NX + 1
        J = IZ * NX + NX
        WRITE(IUNIT, FMT_STR) DATA_ARRAY(I:J)
      END DO
      !
      RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE WRITE_VTK_DATA(IUNIT,FNAME,UNIT,DTYPE,DATA_ARRAY,NX,NZ)
C
C     WRITTEN BY: MATTHEW STADELMAN
C
C     LAST MODIFIED: 2017/02/08
C
C     SUBROUTINE DESCRIPTION: OUTPUTS A DATA VECTOR INTO THE VTK FILE
C
C     SUBROUTINE CALLS: WRITE_ONED_ARRAY
C
C ----------------------------------------------------------------------
C     VARIABLE DESCRIPTION:
C       IUNIT - FILE UNIT NUMBER TO WRITE TO
C       FNAME - FIELD NAME
C       UNIT - PHYSICAL UNITS OF DATA
C       DTYPE - PARAVEW DATA TYPE
C       DATA_ARRAY - DATA VECTOR TO OUTPUT
C       NX,NZ - DATA EXTENTS ALONG EACH AXIS
C
C ----------------------------------------------------------------------
C
      USE IO_MODULE, ONLY : MESSAGE
C
      IMPLICIT NONE
      REAL(8), INTENT(IN) :: DATA_ARRAY(:)
      INTEGER, INTENT(IN) :: IUNIT, NX, NZ
      CHARACTER(*), INTENT(IN) :: FNAME, UNIT, DTYPE
      !
      CHARACTER(80) :: FMT_STR
      FMT_STR = "(*(1(E14.6,:,' '), /, :))"
C
C     CREATING THE DATA TABLE
      WRITE(IUNIT, "(' ')")
      WRITE(IUNIT, 2000) TRIM(FNAME), TRIM(UNIT), TRIM(DTYPE)
      WRITE(IUNIT, "('LOOKUP_TABLE default')")
C
      CALL WRITE_ONED_ARRAY(IUNIT, DATA_ARRAY, NX, NZ, FMT_STR)
      CALL MESSAGE("         "//TRIM(FNAME)//" DATA OUTPUT TO VTK FILE")
C
      RETURN
C
 2000 FORMAT('SCALARS ', A, '[', A, '] ', A)
C
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      END MODULE
