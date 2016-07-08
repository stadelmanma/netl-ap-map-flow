C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE SOLVER
C
C     WRITTEN BY: MATTHEW STADELMAN
C     LAST MODIFIED: 2016/06/30
C
C     PROGRAM DESCRIPTION: CREATES THE COEFFICENT MATRIX AND SOLVES FOR THE
C         PRESSURE.
C
C     SUBROUTINE CALLS: D4_GAUSS
C
C ----------------------------------------------------------------------
C     VARIABLE DESCRIPTION:
C       X - VECTOR THAT STORES THE CHANGE IN PRESSURE TO REACH STEADY-STATE CONDITIONS
C       RHS - RHS OF THE SOLTUION MATRIX, NET FLOW CHANGE THAT IS SOLVED FOR
C
C ----------------------------------------------------------------------
C
      USE APM_MODULE
C
      IMPLICIT NONE
      REAL(8), ALLOCATABLE :: X(:)
      REAL(8) :: ST,EN
      INTEGER :: I,IX,IZ
C
C     ALLOCATING VECTORS
      CALL ALLOCATE_COEF(NX*NZ)
C
C     INITIALIZING  VARIABLES
      RHS(:) = 0.0
      SOLV_NX = NX
      SOLV_NZ = NZ
      X_OFFSET = 0
      Z_OFFSET = 0
C
C     SWEEPING GRID TO POPULATE COEFFICIENT ARRAYS
      I = 0
      DO IZ = 1,NZ
        DO IX = 1,NX
          I = (IZ-1)*NX + IX
          TT(I,1)  = -TRX(IZ,IX-1) !LEFT
          TT(I,2)  = -TRX(IZ,IX) !RIGHT
          TT(I,3)  = -TRZ(IZ-1,IX) !DOWN
          TT(I,4)  = -TRZ(IZ,IX) !TOP
          CC(I)  =  -SUM(TT(I,:))
        END DO
      END DO
C
C     SETTING UP THE BOUNDARY CONDITIONS
      CALL DEFINE_BOUNDARY_CONDITIONS
C
C     CALLING THE SOLVER ALGORITHM
      CALL BLANK
      CALL MESSAGE('     USING D4 GAUSS SOLVER')
      CALL CPU_TIME(ST)
      !
      ALLOCATE(X(SOLV_NX*SOLV_NZ))
      X(:) = 0.0
      !
      CALL D4_REORDER
      CALL D4_SOLVER(X)
      CALL CPU_TIME(EN)
      WRITE(CVAR,"(5X,'REQUIRED TIME FOR SOLUTION: ',F13.6)")(EN-ST)
      CALL MESSAGE(CVAR)
C
C     UPDATING THE FRACTURE PRESSURE
      DO IZ = 1,NZ
        DO IX = 1,NX
          I = (IZ + Z_OFFSET - 1)*SOLV_NX + IX + X_OFFSET
          FRAC_PS(IZ,IX) = X(I)
        END DO
      END DO
C
      CALL DEALLOCATE_COEF
      DEALLOCATE(X)
C
      RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
C ----------------------------------------------------------------------
C
      SUBROUTINE DEFINE_BOUNDARY_CONDITIONS
C
C     WRITTEN BY: MATTHEW STADELMAN
C     DATE WRITTEN: 06/30/2016
C
      USE APM_MODULE
C
      IMPLICIT NONE
C
C     SETTING PRESSURE BCs
      IF (OUTPSB .GE. 0) THEN
        CALL ADD_BOUND_COND(OUTFLOW, OUTPSB)
      END IF
      !
      IF (FPSB .GE. 0) THEN
        CALL ADD_BOUND_COND(INLET_SIDE, FPSB)
      END IF
C
C     DEFINING GROUP FLOW BCs
      ALLOCATE (NEUMANNG_ROW(SOLV_NX*SOLV_NZ))
      ALLOCATE (NEUMANNG_COL(SOLV_NX*SOLV_NZ))
      !
      IF (INJRATE .GT. 0.0) THEN !INLET FLOW RATE BC
        CALL ADD_NGBOUND_COND(INLET_SIDE, INJRATE)
      END IF
      !
      IF (OUTRATE .GT. 0.0) THEN !OUTLET FLOW RATE BC
        CALL ADD_NGBOUND_COND(OUTFLOW, -OUTRATE)
      END IF
C
C     IF PRESSURE CONTROLLED THEN GROUP BCs SHOULD NOT AFFECT SOLUTION
      IF (PRESC) THEN
        NEUMANNG_CC = 1.0
        NEUMANNG_COL(:) = 0.0
        NEUMANNG_ROW(:) = 0.0
        NEUMANNG_RHS = 0.0
      END IF
C
      RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
C ----------------------------------------------------------------------
C
      SUBROUTINE ADD_BOUND_COND(SIDE, BC_VALUE)
C
C     WRITTEN BY: MATTHEW STADELMAN
C     DATE WRITTEN: 07/05/2016
C
      USE APM_MODULE
C
      IMPLICIT NONE
      REAL(8), ALLOCATABLE :: NEW_CC(:),NEW_TT(:,:),NEW_RHS(:)
      REAL(8) :: BC_VALUE
      INTEGER, ALLOCATABLE :: BC_SLICE(:), MV_SLICE(:)
      INTEGER :: IB, IZ, OLD_NX, OLD_NZ, NXZ
      CHARACTER(*) :: SIDE
C
C     DETERMINING NEW DIMENSIONS OF SOLVER ARRAYS
      OLD_NX = SOLV_NX
      OLD_NZ = SOLV_NZ
      IF (INDEX(SIDE,'BOTTOM') > 0) THEN
        SOLV_NZ = SOLV_NZ + 1
        Z_OFFSET = Z_OFFSET + 1
        ALLOCATE(BC_SLICE(OLD_NX),MV_SLICE(OLD_NX*OLD_NZ))
        FORALL (IB = 1:OLD_NX) BC_SLICE(IB) = IB
        FORALL (IB = 1:OLD_NX*OLD_NZ) MV_SLICE(IB) = OLD_NX+IB
      ELSE IF (INDEX(SIDE,'TOP') > 0) THEN
        SOLV_NZ = SOLV_NZ + 1
        ALLOCATE(BC_SLICE(OLD_NX),MV_SLICE(OLD_NX*OLD_NZ))
        FORALL (IB = 1:OLD_NX) BC_SLICE(IB) = OLD_NX*OLD_NZ+IB
        FORALL (IB = 1:OLD_NX*OLD_NZ) MV_SLICE(IB) = IB
      ELSE IF (INDEX(SIDE,'LEFT') > 0) THEN
        SOLV_NX = SOLV_NX + 1
        X_OFFSET = X_OFFSET + 1
        ALLOCATE(BC_SLICE(OLD_NZ),MV_SLICE(OLD_NX*OLD_NZ))
        DO IZ = 0,OLD_NZ-1
            BC_SLICE(IZ+1) = IZ*SOLV_NX+1
            FORALL(IB = 1:OLD_NX) MV_SLICE(IZ*OLD_NX+IB)=IZ*SOLV_NX+IB+1
        END DO
      ELSE IF (INDEX(SIDE,'RIGHT') > 0) THEN
        SOLV_NX = SOLV_NX + 1
        ALLOCATE(BC_SLICE(OLD_NZ),MV_SLICE(OLD_NX*OLD_NZ))
        DO IZ = 0,OLD_NZ-1
            BC_SLICE(IZ+1) = IZ*SOLV_NX+SOLV_NX
            FORALL(IB = 1:OLD_NX) MV_SLICE(IZ*OLD_NX+IB)=IZ*SOLV_NX+IB
        END DO
      ELSE
        CALL MESSAGE('INVALID BOUNDARY SIDE GIVEN: '//SIDE)
        RETURN
      END IF
C
C     ALLOCATING TEMP ARRAYS TO NEW SIZE
      NXZ = SOLV_NZ * SOLV_NX
      ALLOCATE(NEW_CC(NXZ), NEW_TT(NXZ, 4), NEW_RHS(NXZ))
      NEW_CC(:) = 0.0
      NEW_TT(:,:) = 0.0
      NEW_RHS(:) = 0.0
C
C     POPULATING TEMP ARRAYS
      NEW_CC(BC_SLICE) = 1.0
      NEW_CC(MV_SLICE) = CC(:)
      NEW_TT(BC_SLICE, :) = 0.0
      NEW_TT(MV_SLICE, :) = TT(:,:)
      NEW_RHS(BC_SLICE) = BC_VALUE
      NEW_RHS(MV_SLICE) = RHS(:)
C
C     RESIZING OLD ARRAYS
      DEALLOCATE(CC,TT,RHS)
      ALLOCATE(CC(NXZ),TT(NXZ, 4),RHS(NXZ))
      !
      CC(:) = NEW_CC(:)
      TT(:,:) = NEW_TT(:,:)
      RHS(:) = NEW_RHS(:)
C
      RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
C ----------------------------------------------------------------------
C
      SUBROUTINE ADD_NGBOUND_COND(SIDE, BC_VALUE)
C
C     WRITTEN BY: MATTHEW STADELMAN
C     DATE WRITTEN: 07/06/2016
C
      USE APM_MODULE
C
      IMPLICIT NONE
      REAL(8) :: BC_VALUE
      INTEGER, ALLOCATABLE :: BC_SLICE(:)
      INTEGER :: I, IB, ID
      CHARACTER(*) :: SIDE

C
C     DETERMINING INDICIES TO MODIFY
      IF (INDEX(SIDE,'BOTTOM') > 0) THEN
        ALLOCATE(BC_SLICE(SOLV_NX))
        ID = 3
        FORALL (IB = 1:SOLV_NX) BC_SLICE(IB) = IB
      ELSE IF (INDEX(SIDE,'TOP') > 0) THEN
        ALLOCATE(BC_SLICE(SOLV_NX))
        ID = 4
        FORALL (IB = 1:SOLV_NX) BC_SLICE(IB) = (SOLV_NZ-1)*SOLV_NX+IB
      ELSE IF (INDEX(SIDE,'LEFT') > 0) THEN
        ALLOCATE(BC_SLICE(SOLV_NZ))
        ID = 1
        FORALL (IB = 0:SOLV_NZ-1) BC_SLICE(IB+1) = IB*SOLV_NX+1
      ELSE IF (INDEX(SIDE,'RIGHT') > 0) THEN
        ALLOCATE(BC_SLICE(SOLV_NZ))
        ID = 2
        FORALL (IB = 0:SOLV_NZ-1) BC_SLICE(IB+1) = IB*SOLV_NX+SOLV_NX
      ELSE
        CALL MESSAGE('INVALID BOUNDARY SIDE GIVEN: '//SIDE)
        RETURN
      END IF
C
C     UPDATING COEFF VECTORS
      NEUMANNG_ROW(:) = 0.0
      NEUMANNG_COL(:) = 0.0
      DO I = 1,SIZE(BC_SLICE)
        IB = BC_SLICE(I)
        NEUMANNG_COL(IB) = TT(IB,ID)
        NEUMANNG_ROW(IB) = TT(IB,ID)
        TT(IB,ID) = 0.0
      END DO
      NEUMANNG_CC = -SUM(NEUMANNG_ROW)
      NEUMANNG_RHS = BC_VALUE
C
      DEALLOCATE(BC_SLICE)
      RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
C ----------------------------------------------------------------------
C
      SUBROUTINE D4_REORDER
C
C     WRITTEN BY: W. NEAL SAMS
C     DATE WRITTEN: 02/29/2016
C
      USE APM_MODULE
C
      IMPLICIT NONE
      INTEGER :: NXZ
      INTEGER :: IBR,IB,IPASS,IDIAG,I,J
      INTEGER :: ID,JD,IL,IR,IBRU,JBR
C
      NXZ = SOLV_NX*SOLV_NZ
      ALLOCATE (INAT(NXZ),INO(NXZ))
      ALLOCATE (LINK_D4(NXZ,4))
      FORALL (IB = 1:NXZ) INO(IB) = 0
C
C     REORDER CELL NUMBERING
C
      IBR = 0
      DO IPASS = 1,2
        IF(SOLV_NX >= SOLV_NZ) THEN
           DO IDIAG = IPASS+1,SOLV_NX+SOLV_NZ,2
             DO I = 1,SOLV_NX
               J = IDIAG - I
               IF(J > SOLV_NZ) CYCLE
               IF(J < 1) EXIT
               IB = SOLV_NX*(J-1) + I
               IBR = IBR + 1
               INO(IB) = IBR
             END DO
           END DO
        ELSE
          DO IDIAG = IPASS+1,SOLV_NX+SOLV_NZ,2
            DO J = 1,SOLV_NZ
              I = IDIAG - J
              IF(I > SOLV_NX) CYCLE
              IF(I < 1) EXIT
              IB = SOLV_NX*(J-1) + I
              IBR = IBR + 1
              INO(IB) = IBR
            END DO
          END DO
        END IF
        IBR_MAX(IPASS) = IBR
      END DO
      NUM_TOP = IBR_MAX(1)
      NUM_BOTTOM = IBR_MAX(2) - IBR_MAX(1)
      NUM_TOTAL = IBR_MAX(2)
C
C     SET POINTERS TO ADJACENT CELLS
C
      IB = 0
      DO J = 1,SOLV_NZ
        DO I = 1,SOLV_NX
          IB = IB + 1
          IBR = INO(IB)
          IF(IBR > 0) THEN
            INAT(IBR) = IB
            DO ID = 1,4
              LINK_D4(IBR,ID) = 0
            END DO
            IF(I >  1) LINK_D4(IBR,1) = INO(IB-1)
            IF(I < SOLV_NX) LINK_D4(IBR,2) = INO(IB+1)
            IF(J >  1) LINK_D4(IBR,3) = INO(IB-SOLV_NX)
            IF(J < SOLV_NZ) LINK_D4(IBR,4) = INO(IB+SOLV_NX)
          END IF
        END DO
      END DO
C
C     DETERMINE STORAGE REQUIREMENTS
C
      ALLOCATE (IBASE_UPPER(NUM_TOP+1:NUM_TOTAL+1))
      IR = 0
      MAX_BAND = 0
      IBASE_UPPER(NUM_TOP+1) = 0
      DO IBR = NUM_TOP+1,NUM_TOTAL
        IL = IBR
        DO ID = 1,4
          IBRU = LINK_D4(IBR,ID)
          IF(IBRU > 0) THEN
            DO JD = 1,4
              JBR = LINK_D4(IBRU,JD)
              IF(JBR > 0) THEN
                IF(JBR < IL) IL = JBR
                IF(JBR > IR) IR = JBR
              END IF
            END DO
          END IF
        END DO
        IF(IBR - IL > MAX_BAND) MAX_BAND = IBR - IL
        IF(IR - IBR > MAX_BAND) MAX_BAND = IR - IBR
        IBASE_UPPER(IBR+1) = IBASE_UPPER(IBR) + IR - IBR
      END DO
C
      ALLOCATE (ROW(-MAX_BAND:MAX_BAND))
      ALLOCATE (UPPER_D4(IBASE_UPPER(NUM_TOTAL+1)))
C
      RETURN
C
      END SUBROUTINE
!
! ----------------------------------------------------------------------
! @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
! ----------------------------------------------------------------------
!
      SUBROUTINE D4_SOLVER(X)
!
!     WRITTEN BY: W. NEAL SAMS
!     DATE WRITTEN: 02/29/2016
!
!     MODIFIED BY: MATTHEW STADELMAN
!     MODFIED ON: 07/08/2016 TO IMPLEMENT GROUP BCs
!
      USE APM_MODULE
!
      IMPLICIT NONE
      REAL(8),ALLOCATABLE :: NG_D4COL(:),NG_D4ROW(:)
      REAL(8) :: X(*)
      REAL(8) :: TEMP_RHS,TEMP_NGCOL,FACTOR,NEUMANNG_X
      INTEGER :: IBR,IBRU,JBR,IB,IBU,NXZ
      INTEGER :: ICOL,JCOL,IL,ID,JD,IUP
!
      NXZ = SOLV_NX * SOLV_NZ
      ALLOCATE(NG_D4COL(NXZ), NG_D4ROW(-NXZ:0))
!
!     ELIMINATION ON THE LOWER HALF OF THE MATRIX ROW BY ROW
!
      DO IBR = NUM_TOP+1,NUM_TOTAL
        IB = INAT(IBR) !INAT MAPS D4 ORDER TO LEXI ORDER
        TEMP_RHS = RHS(IB)
        TEMP_NGCOL = NEUMANNG_COL(IB)
!
!     ELIMINATE THE LOWER LEFT QUADRANT OF THE MATRIX AND FILL IN
!     THE LOWER RIGHT QUADRANT OF THE MATRIX.
!
        ROW(:) = 0.0
        ROW(0) = CC(IB)
        IL = 0
        DO ID = 1,4
          IBRU = LINK_D4(IBR,ID)
          IF(IBRU > 0) THEN
            IBU = INAT(IBRU)
            FACTOR = TT(IB,ID)/CC(IBU)
            DO JD = 1,4
              JBR = LINK_D4(IBRU,JD)
              IF(JBR > 0) THEN
                ICOL = JBR - IBR
                IF(ICOL < IL) IL = ICOL
                ROW(ICOL) = ROW(ICOL) - FACTOR*TT(IBU,JD)
              END IF
            END DO
            TEMP_NGCOL = TEMP_NGCOL - FACTOR*NEUMANNG_COL(IBU)
            TEMP_RHS = TEMP_RHS - FACTOR*RHS(IBU)
          END IF
        END DO
!
!     ELIMINATE ELEMENTS TO THE LEFT OF THE DIAGONAL
!
        DO ICOL = IL,-1
          FACTOR = ROW(ICOL)
          JBR = IBR + ICOL
          JCOL = ICOL
          DO IUP = IBASE_UPPER(JBR)+1,IBASE_UPPER(JBR+1)
            JCOL = JCOL + 1
            ROW(JCOL) = ROW(JCOL) - FACTOR*UPPER_D4(IUP)
          END DO
          TEMP_NGCOL = TEMP_NGCOL - FACTOR*NG_D4COL(JBR)
          TEMP_RHS = TEMP_RHS - FACTOR*X(INAT(JBR))
        END DO
!
!     NORMALIZE AND STORE UPPER TRIANGLE
!
        FACTOR = 1.0/ROW(0)
        ICOL = 0
        DO IUP = IBASE_UPPER(IBR)+1,IBASE_UPPER(IBR+1)
          ICOL = ICOL + 1
          UPPER_D4(IUP) = FACTOR*ROW(ICOL)
        END DO
        NG_D4COL(IBR) = FACTOR*TEMP_NGCOL
        X(IB) = FACTOR*TEMP_RHS
      END DO
!
!     ELIMINATING THE NEUMANN GROUP ROW
!
      FORALL (IB = 1:NXZ) NG_D4ROW(INO(IB)-NXZ-1) = NEUMANNG_ROW(IB)
      NG_D4ROW(0) = NEUMANNG_CC
      ! HANDLING UPPER HALF
      DO IBR = 1,NUM_TOP
        IB = INAT(IBR)
        IBU = IBR - SOLV_NX*SOLV_NZ - 1
        !
        FACTOR = NG_D4ROW(IBU)/CC(IB)
        DO JD = 1,4
          JBR = LINK_D4(IBR,JD)
          IF(JBR > 0) THEN
            IBU = JBR - SOLV_NX*SOLV_NZ - 1
            NG_D4ROW(IBU) = NG_D4ROW(IBU) - FACTOR*TT(IB,JD)
          END IF
        END DO
        NEUMANNG_CC = NEUMANNG_CC - FACTOR*NEUMANNG_COL(IB)
        NEUMANNG_RHS = NEUMANNG_RHS - FACTOR*RHS(IB)
      END DO
      ! HANDLING LOWER HALF
      IL = -NUM_TOP !+ 1! I'M NOT ENTIRELY CONVINCED THIS +1 IS VALID I THINK IT MIGHT SKIP A ROW
      DO ICOL = IL,-1
        FACTOR = NG_D4ROW(ICOL)
        JBR = SOLV_NX*SOLV_NZ + ICOL + 1
        JCOL = ICOL
        DO IUP = IBASE_UPPER(JBR)+1,IBASE_UPPER(JBR+1)
          JCOL = JCOL + 1
          NG_D4ROW(JCOL) = NG_D4ROW(JCOL)-FACTOR*UPPER_D4(IUP)
        END DO
        NEUMANNG_CC = NEUMANNG_CC - FACTOR*NG_D4COL(JBR)
        NEUMANNG_RHS = NEUMANNG_RHS - FACTOR*X(INAT(JBR))
      END DO
      NEUMANNG_X = NEUMANNG_RHS/NEUMANNG_CC
!
!     BACK SUBSTITUTION ON LOWER HALF
!
      X(NXZ) = X(NXZ) - NG_D4COL(INO(NXZ))*NEUMANNG_X
      DO IBR = NUM_TOTAL-1,NUM_TOP+1,-1
        IB = INAT(IBR)
        TEMP_RHS = X(IB)
        TEMP_RHS = TEMP_RHS - NG_D4COL(IBR)*NEUMANNG_X
        JBR = IBR
        DO IUP = IBASE_UPPER(IBR)+1,IBASE_UPPER(IBR+1)
          JBR = JBR + 1
          TEMP_RHS = TEMP_RHS - UPPER_D4(IUP)*X(INAT(JBR))
        END DO
        X(IB) = TEMP_RHS
      END DO
!
!     BACK SUBSTITUTION ON UPPER HALF
!
      DO IBR = 1,NUM_TOP
        IB = INAT(IBR)
        TEMP_RHS = RHS(IB)
        TEMP_RHS = TEMP_RHS - NEUMANNG_COL(IB)*NEUMANNG_X
        DO ID = 1,4
          JBR = LINK_D4(IBR,ID)
          IF(JBR > 0) TEMP_RHS = TEMP_RHS - TT(IB,ID)*X(INAT(JBR))
        END DO
        X(IB) = TEMP_RHS/CC(IB)
      END DO
!
      PRINT *, "X VECTOR:"
      WRITE(*,"(4X,*(G10.3,1X,:))") X(1:NXZ)
      PRINT *, NEUMANNG_X
!
!     SETTING FLOW RATE DETERMINED INLET OR OUTLET PRESSURE
      IF (.NOT. PRESC) THEN
        IF (INJRATE .GT. 0.0) THEN !INLET FLOW RATE BC
          FPSB = NEUMANNG_X
        END IF
        !
        IF (OUTRATE .GT. 0.0) THEN !OUTLET FLOW RATE BC
          OUTPSB = NEUMANNG_X
        END IF
      END IF
!
      RETURN
      END SUBROUTINE
!
! ----------------------------------------------------------------------
! @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
! ----------------------------------------------------------------------
!