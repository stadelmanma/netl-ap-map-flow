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
      CONTAINS
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE CALC_PERCENTILE(VECTOR, PERC_ARR)
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
      REAL(8) :: VECTOR(:), PERC_ARR(:, :)
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
      REAL(8) :: VECTOR(:), VAL
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
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      END MODULE
