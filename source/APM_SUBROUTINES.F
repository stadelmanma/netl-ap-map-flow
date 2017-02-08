C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE CALC_PERCENTILE(VECTOR,PERC_ARR,NVALS,NPCT)
C
C     WRITTEN BY: MATTHEW STADELMAN
C
C     DATE WRITTEN:  2015/03/02
C     LAST MODIFIED: 2016/02/10
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
C       COUNT - STORES THE NUMBER OF TIMES A VALUE APPEARS IN SORT
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
      REAL(8) :: VECTOR(*),PERC_ARR(2,*)
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
C     COUNTING DUPLICATE VALUES AND CREATING A UNIQUE VALUED VECTOR
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
      REAL(8) :: VECTOR(*),VAL
      INTEGER :: I,J,L,N,IR
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
      END SUBROUTINE HEAP_SORT
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE COEF
C
C     WRITTEN BY: MATTHEW STADELMAN
C
C     DATE WRITTEN:  2015/03/02
C     LAST MODIFIED: 2016/10/27
C
C     PROGRAM DESCRIPTION: INIITIALIZES ALL OF THE SIMULATION COEFFICENTS
C
C
C ----------------------------------------------------------------------
C     VARIABLE DESCRIPTION:
C       PH,PL - PRESSURE INTERPOLATION VARIABLES
C       B - APERTURE OF THE INTERFACE BEING CORRECTED
C       DBP - HALF OF THE DELTA X FROM THE "P" SIDE
C       DBF - HALF OF THE DELTA X FROM THE "F" SIDE
C       THETA - SLOPE ANGLE FROM CENTER OF CELL TO INTERFACE
C       BP3 - TAPERED PLATE CORRECTED "P" APERTURE CUBED
C       BF3 - TAPERED PLATE CORRECTED "F" APERTURE CUBED
C       BOK - CONTROL VARIABLE USED TO HALT PROGRAM IF A FATAL ERROR IS ENCOUNTERED
C
C ----------------------------------------------------------------------
C
      USE APM_MODULE
      USE MAP_MODULE
C
      IMPLICIT NONE
      REAL(8) :: B,BF3,BP3,DBF,DBP,W3,THETA
      INTEGER :: I,IX,IZ
C
C     INTIALIZING VARIABLES
      DX(:) = DIAM/NX
      DZ(:) = LENG/NZ
      TRX(:,:) = 0.0
      TRZ(:,:) = 0.0
C
C     DEFINING AN AVERAGE HOMONGENOUS TRANSMISSIVITY
      AVG_TRX = (LENG*AVG_APER**3)/(12.0*DIAM)
      AVG_TRZ = (DIAM*AVG_APER**3)/(12.0*LENG)
C
C     USING THE STOKES TAPERED PLATE FLOW SOLUTION TO CALCULATE THE TRANS
C     OF THE RIGHT AND TOP INTERFACE OF A GRID BLOCK
      DO IZ = 1,NZ
        DO IX = 1,NX-1
          I = (IZ-1)*NX + IX
          !
          ! SOLVING TAPERED PLATE CORRECTION FOR CELL CENTERS TO INTERFACE
          B = AP_POINT_MAP(IZ,IX,5) !WIDTH AT INTERFACE BASED ON CORNER VALUES
          DBP = DX(I)/2  !(DX(I)/2 = DISTANCE FROM CENTER CELL TO INTERFACE IF PLANAR
          THETA = ATAN(ABS(WIDTH(I)-B)/DBP)
          W3 = (2 * WIDTH(I)**2 * B**2)/(WIDTH(I) + B)
          BP3 = W3 * 3*(TAN(THETA) - THETA)/(TAN(THETA)**3)
          IF (INT(1E9*(TAN(THETA) - THETA)) == 0) BP3 = W3
          !
          DBF = DX(I+1)/2  !(DX(I+1)/2 = DISTANCE FROM CENTER CELL TO INTERFACE IF PLANAR
          THETA = ATAN(ABS(B-WIDTH(I+1))/DBF)
          W3 = (2 * B**2 * WIDTH(I+1)**2)/(B + WIDTH(I+1))
          BF3 = W3 * 3*(TAN(THETA) - THETA)/(TAN(THETA)**3)
          IF (INT(1E9*(TAN(THETA) - THETA)) == 0) BF3 = W3
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
          B = AP_POINT_MAP(IZ,IX,6) !WIDTH AT INTERFACE BASED ON CORNER VALUES
          DBP = DZ(I)/2  !(DZ(I)/2 = DISTANCE FROM CENTER CELL TO INTERFACE IF PLANAR
          THETA = ATAN(ABS(WIDTH(I)-B)/DBP)
          W3 = (2 * WIDTH(I)**2 * B**2)/(WIDTH(I) + B)
          BP3 = W3 * 3*(TAN(THETA) - THETA)/(TAN(THETA)**3)
          IF (INT(1E9*(TAN(THETA) - THETA)) == 0) BP3 = W3
          !
          DBF = DZ(I+NX)/2  !(DZ(I+NX)/2 = DISTANCE FROM CENTER CELL TO INTERFACE IF PLANAR
          THETA = ATAN(ABS(B-WIDTH(I+NX))/DBF)
          W3 = (2 * B**2 * WIDTH(I+NX)**2)/(B + WIDTH(I+NX))
          BF3 = W3 * 3*(TAN(THETA) - THETA)/(TAN(THETA)**3)
          IF (INT(1E9*(TAN(THETA) - THETA)) == 0) BF3 = W3
          !
          TRZ(IZ,IX) = (DBP/BP3 + DBP/BF3)**(-1) * (DX(I)/12)
        END DO
      END DO
C
      DO IZ = 1,NZ
        ! HANDLING SPECIAL CASE AT RIGHT SIDE OF FRACTURE
        I = (IZ-1)*NX + NX
        B = AP_POINT_MAP(IZ,NX,5) !WIDTH AT INTERFACE BASED ON CORNER VALUES
        DBP = DX(I)/2  !(DX(I)/2 = DISTANCE FROM CENTER CELL TO INTERFACE IF PLANAR
        THETA = ATAN(ABS(WIDTH(I)-B)/DBP)
        W3 = (2 * WIDTH(I)**2 * B**2)/(WIDTH(I) + B)
        BP3 = W3 * 3*(TAN(THETA) - THETA)/(TAN(THETA)**3)
        IF (INT(1E9*(TAN(THETA) - THETA)) == 0) BP3 = W3
        !
        TRX(IZ,NX) = (DZ(I)*BP3)/(12.0*DX(I))
      END DO
C
      DO IX = 1,NX
        ! HANDLING SPECIAL CASE AT TOP OF FRACTURE
        I = (NZ-1)*NX + IX
        B = AP_POINT_MAP(NZ,IX,6) !WIDTH AT INTERFACE BASED ON CORNER VALUES
        DBP = DZ(I)/2  !(DZ(I)/2 = DISTANCE FROM CENTER CELL TO INTERFACE IF PLANAR
        THETA = ATAN(ABS(WIDTH(I)-B)/DBP)
        W3 = (2 * WIDTH(I)**2 * B**2)/(WIDTH(I) + B)
        BP3 = W3 * 3*(TAN(THETA) - THETA)/(TAN(THETA)**3)
        IF (INT(1E9*(TAN(THETA) - THETA)) == 0) BP3 = W3
        !
        TRZ(NZ,IX) = (DZ(I)*BP3)/(12.0*DX(I))
      END DO
C
C     DIVIDING TRANSMISSIVITY BY VISCOSITY
      AVG_TRZ = AVG_TRZ/AVG_VISC
      AVG_TRX = AVG_TRX/AVG_VISC
      TRX(:,:) = TRX(:,:)/AVG_VISC
      TRZ(:,:) = TRZ(:,:)/AVG_VISC
C
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
C     WRITTEN BY: MATTHEW STADELMAN
C
C     DATE WRITTEN:  2015/03/02
C     LAST MODIFIED: 2016/07/08
C
C     PROGRAM DESCRIPTION: DEFINES FLOW AND PRESSURE BOUNDARY CONIDITIONS
C
C     SUBROUTINE CALLS: NONE
C
C ----------------------------------------------------------------------
C     VARIABLE DESCRIPTION:
C       BOK - CONTROL VARIABLE USED TO HALT PROGRAM IF A FATAL ERROR IS ENCOUNTERED
C
C ----------------------------------------------------------------------
C
      USE APM_MODULE
      USE IO_MODULE, ONLY : BLANK, MESSAGE
      USE MAP_MODULE, ONLY : NX, NZ
C
      IMPLICIT NONE
      INTEGER :: IX,IZ
      LOGICAL :: BOK
C
C
      CALL BLANK
      CALL MESSAGE(" DEFINING BOUNDARY CELL TRANSMISSIBILIES")
C
C     HANDLING EACH OUTFLOW SIDE CASE
      IF (INDEX(OUTLET_SIDE,'LEFT') > 0) THEN
C
C       DEFINING THE BOUNDARY CONDITIONS FOR EACH SIDE OF THE FRACTURE
        TRX(1:NZ,0) = 2*TRX(1:NZ,1) !LEFT SIDE BOUNDARY
        TRX(1:NZ,NX) = 2*TRX(1:NZ,NX) !RIGHT SIDE BOUNDARY
        TRZ(0,1:NX) = 0.0 !BOTTOM BOUNDARY
        TRZ(NZ,1:NX) = 0.0 !EXTRA TOP ROW
C
C       DEFINING INLET AND OUTLET
        INLET_SIDE = 'RIGHT'
        NC = NZ
        DO IZ = 1,NZ
          INLET(IZ) = (IZ-1)*NX + NX
          OUTLET(IZ) = (IZ-1)*NX + 1
        END DO
      ELSE IF (INDEX(OUTLET_SIDE,'RIGHT') > 0) THEN
C
C       DEFINING THE BOUNDARY CONDITIONS FOR EACH SIDE OF THE FRACTURE
        TRX(1:NZ,0) = 2*TRX(1:NZ,1) !LEFT SIDE BOUNDARY
        TRX(1:NZ,NX) = 2*TRX(1:NZ,NX) !RIGHT SIDE BOUNDARY
        TRZ(0,1:NX) = 0.0 !BOTTOM BOUNDARY
        TRZ(NZ,1:NX) = 0.0 !EXTRA TOP ROW
C
C       DEFINING INLET AND OUTLET
        INLET_SIDE = 'LEFT'
        NC = NZ
        DO IZ = 1,NZ
          INLET(IZ) = (IZ-1)*NX + 1
          OUTLET(IZ) = (IZ-1)*NX + NX
        END DO
      ELSE IF (INDEX(OUTLET_SIDE,'TOP') > 0) THEN
C
C       DEFINING THE BOUNDARY CONDITIONS FOR EACH SIDE OF THE FRACTURE
        TRX(1:NZ,0) = 0.0 !LEFT SIDE BOUNDARY
        TRX(1:NZ,NX) = 0.0 !RIGHT SIDE BOUNDARY
        TRZ(0,1:NX) = 2*TRZ(1,1:NX) !BOTTOM BOUNDARY
        TRZ(NZ,1:NX) = 2*TRZ(NZ,1:NX) !EXTRA TOP ROW
C
C       DEFINING INLET AND OUTLET
        INLET_SIDE = 'BOTTOM'
        NC = NX
        DO IX = 1,NX
          INLET(IX) = IX
          OUTLET(IX) = (NZ-1)*NX + IX
        END DO
      ELSE IF (INDEX(OUTLET_SIDE,'BOTTOM') > 0) THEN
C
C       DEFINING THE BOUNDARY CONDITIONS FOR EACH SIDE OF THE FRACTURE
        TRX(1:NZ,0) = 0.0 !LEFT SIDE BOUNDARY
        TRX(1:NZ,NX) = 0.0 !RIGHT SIDE BOUNDARY
        TRZ(0,1:NX) = 2*TRZ(1,1:NX) !BOTTOM BOUNDARY
        TRZ(NZ,1:NX) = 2*TRZ(NZ,1:NX) !EXTRA TOP ROW
C
C       DEFINING INLET AND OUTLET
        INLET_SIDE = 'TOP'
        NC = NX
        DO IX = 1,NX
          INLET(IX) = (NZ-1)*NX + IX
          OUTLET(IX) = IX
        END DO
      ELSE
        GOTO 1000
      END IF
C
      RETURN
C
 1000 BOK = .FALSE.
      CALL MESSAGE(" INVALID OUTLET SIDE ENTERED: "//TRIM(OUTLET_SIDE))
      RETURN
C
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
