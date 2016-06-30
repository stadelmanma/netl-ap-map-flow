C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE SOLVER
C
C     WRITTEN BY: MATTHEW STADELMAN
C
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
C       QRIGHT,QLEFT,QTOP,QBOT - FLOW THROUGH A CELL IN THE GIVEN DIRECTION
C
C ----------------------------------------------------------------------
C
      USE APM_MODULE
C
      IMPLICIT NONE
      REAL(8), ALLOCATABLE :: RHS(:), X(:)
      REAL(8) :: QRIGHT,QLEFT,QTOP,QBOT,ST,EN
      INTEGER :: I,IX,IZ
C
C     ALLOCATING VECTORS
      CALL ALLOCATE_COEF(NX*NZ)
C
C     INITIALIZING  VECTORS
      ALLOCATE(RHS(NX*NZ), X(NX*NZ))
      RHS(:) = 0.0
      X(:) = 0.0
C
C     SWEEPING GRID TO POPULATE COEFFICIENT ARRAYS
      I = 0
      DO IZ = 1,NZ
        DO IX = 1,NX
          I = (IZ-1)*NX + IX
          CC(I)  =  TRX(IZ,IX-1)+TRX(IZ,IX)+TRZ(IZ-1,IX)+TRZ(IZ,IX)
          TT(I,3)  = -TRZ(IZ-1,IX)
          TT(I,1)  = -TRX(IZ,IX-1)
          TT(I,2)  = -TRX(IZ,IX)
          TT(I,4)  = -TRZ(IZ,IX)
          QLEFT  = -TRX(IZ,IX-1)*(FRAC_PS(IZ,IX) - FRAC_PS(IZ,IX-1))
          QRIGHT = -TRX(IZ,IX)*(FRAC_PS(IZ,IX+1) - FRAC_PS(IZ,IX))
          QBOT   = -TRZ(IZ-1,IX)*(FRAC_PS(IZ,IX) - FRAC_PS(IZ-1,IX))
          QTOP   = -TRZ(IZ,IX)*(FRAC_PS(IZ+1,IX) - FRAC_PS(IZ,IX))
          RHS(I) = (QLEFT - QRIGHT) + (QBOT - QTOP)
        END DO
      END DO
C
C     CALLING THE SOLVER ALGORITHM
      CALL BLANK
      CALL MESSAGE('     USING D4 GAUSS SOLVER')
      CALL D4_REORDER
      CALL CPU_TIME(ST)
      CALL D4_SOLVER(RHS,X)
      CALL CPU_TIME(EN)
      WRITE(CVAR,"(5X,'REQUIRED TIME FOR SOLUTION: ',F13.6)")(EN-ST)
      CALL MESSAGE(CVAR)
C
C     UPDATING THE FRACTURE PRESSURE
      DO IZ = 1,NZ
        DO IX = 1,NX
          I = (IZ-1)*NX + IX
          FRAC_PS(IZ,IX) = FRAC_PS(IZ,IX) + X(I)
        END DO
      END DO
C
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
      NXZ = NX*NZ
      ALLOCATE (INAT(NXZ),INO(NXZ))
      ALLOCATE (LINK_D4(NXZ,4))
      FORALL (IB = 1:NXZ) INO(IB) = 0
C
C     REORDER CELL NUMBERING
C
      IBR = 0
      DO IPASS = 1,2
        IF(NX >= NZ) THEN
           DO IDIAG = IPASS+1,NX+NZ,2
             DO I = 1,NX
               J = IDIAG - I
               IF(J > NZ) CYCLE
               IF(J < 1) EXIT
               IB = NX*(J-1) + I
               IBR = IBR + 1
               INO(IB) = IBR
             END DO
           END DO
        ELSE
          DO IDIAG = IPASS+1,NX+NZ,2
            DO J = 1,NZ
              I = IDIAG - J
              IF(I > NX) CYCLE
              IF(I < 1) EXIT
              IB = NX*(J-1) + I
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
      DO J = 1,NZ
        DO I = 1,NX
          IB = IB + 1
          IBR = INO(IB)
          IF(IBR > 0) THEN
            INAT(IBR) = IB
            DO ID = 1,4
              LINK_D4(IBR,ID) = 0
            END DO
            IF(I >  1) LINK_D4(IBR,1) = INO(IB-1)
            IF(I < NX) LINK_D4(IBR,2) = INO(IB+1)
            IF(J >  1) LINK_D4(IBR,3) = INO(IB-NX)
            IF(J < NZ) LINK_D4(IBR,4) = INO(IB+NX)
          END IF
        END DO
      END DO
      DEALLOCATE (INO)
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
      SUBROUTINE D4_SOLVER(RHS,X)
!
!     WRITTEN BY: W. NEAL SAMS
!     DATE WRITTEN: 02/29/2016
!
      USE APM_MODULE
!
      IMPLICIT NONE
      REAL(8) :: RHS(*), X(*)
      REAL(8) :: TEMP_RHS,FACTOR
      INTEGER :: IBR,IBRU,JBR,IB,IBU
      INTEGER :: ICOL,JCOL,IL,ID,JD,IUP
!
!     ELIMINATION ON THE LOWER HALF OF THE MATRIX ROW BY ROW
!
      DO IBR = NUM_TOP+1,NUM_TOTAL
        IB = INAT(IBR)
        TEMP_RHS = RHS(IB)
!
!     ELIMINATE THE LOWER LEFT QUADRANT OF THE MATRIX AND FILL IN
!     THE LOWER RIGHT QUADRANT OF THE MATRIX.
!
        DO ICOL = -MAX_BAND,MAX_BAND
          ROW(ICOL) = 0.0
        END DO
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
        X(IB) = FACTOR*TEMP_RHS
      END DO
!
!     BACK SUBSTITUTION ON LOWER HALF
!
      DO IBR = NUM_TOTAL-1,NUM_TOP+1,-1
        IB = INAT(IBR)
        TEMP_RHS = X(IB)
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
        DO ID = 1,4
          JBR = LINK_D4(IBR,ID)
          IF(JBR > 0) TEMP_RHS = TEMP_RHS - TT(IB,ID)*X(INAT(JBR))
        END DO
        X(IB) = TEMP_RHS/CC(IB)
      END DO
!
      RETURN
C
      END SUBROUTINE
!
! ----------------------------------------------------------------------
! @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
! ----------------------------------------------------------------------
!