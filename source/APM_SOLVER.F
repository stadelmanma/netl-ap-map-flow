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
C       QRIGHT,QLEFT,QTOP,QBOT - FLOW THROUGH A CELL IN THE GIVEN DIRECTION
C
C ----------------------------------------------------------------------
C
      USE APM_MODULE
C
      IMPLICIT NONE
      REAL(8), ALLOCATABLE :: RHS(:), X(:)
      REAL(8) :: QRIGHT,QLEFT,QTOP,QBOT
      REAL(8) :: ST,EN
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
          TT(I,3)  = -TRZ(IZ-1,IX) !DOWN
          TT(I,1)  = -TRX(IZ,IX-1) !LEFT
          TT(I,2)  = -TRX(IZ,IX) !RIGHT
          TT(I,4)  = -TRZ(IZ,IX) !TOP
          !QLEFT  = -TRX(IZ,IX-1)*(FRAC_PS(IZ,IX) - FRAC_PS(IZ,IX-1))
          !QRIGHT = -TRX(IZ,IX)*(FRAC_PS(IZ,IX+1) - FRAC_PS(IZ,IX))
          !QBOT   = -TRZ(IZ-1,IX)*(FRAC_PS(IZ,IX) - FRAC_PS(IZ-1,IX))
          !QTOP   = -TRZ(IZ,IX)*(FRAC_PS(IZ+1,IX) - FRAC_PS(IZ,IX))
          !RHS(I) = (QLEFT - QRIGHT) + (QBOT - QTOP)
          print *, i, CC(i), tt(i,:)
        END DO
      END DO
C
C     SETTING UP THE GROUP BC ARRAYS
      CALL DEFINE_BOUNDARY_CONDITIONS
      ! HARD DIRICHLET BCs
      !FORALL (I = 1:NC) RHS(INLET(I)) = FPSB
      !FORALL (I = 1:NC) RHS(OUTLET(I)) = OUTPSB
      !FORALL (I = 1:NC) CC(INLET(I)) = 1.0
      !FORALL (I = 1:NC) CC(OUTLET(I)) = 1.0
      !FORALL (I = 1:NC) TT(INLET(I),:) = 0.0
      !FORALL (I = 1:NC) TT(OUTLET(I),:) = 0.0
      !print *, '\n\n\n\n'
      !print *, inlet_col
      !print *, '\n\n\n\n'
      !print *, outlet_col
C
C     CALLING THE SOLVER ALGORITHM
      CALL BLANK
      CALL MESSAGE('     USING D4 GAUSS SOLVER')
      CALL D4_REORDER
C
      CALL CPU_TIME(ST)
      !CALL D4_SOLVER(RHS,X)
      CALL GAUSS(RHS,X)
      CALL CPU_TIME(EN)
      WRITE(CVAR,"(5X,'REQUIRED TIME FOR SOLUTION: ',F13.6)")(EN-ST)
      CALL MESSAGE(CVAR)
C
C     UPDATING THE FRACTURE PRESSURE
      DO IZ = 1,NZ
        DO IX = 1,NX
          I = (IZ-1)*NX + IX
          FRAC_PS(IZ,IX) = X(I)!FRAC_PS(IZ,IX) + X(I)
        END DO
      END DO
C
      !CALL DEALLOCATE_COEF
      DEALLOCATE(RHS,X)
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
      REAL(8) GROUP_TRANS
      INTEGER :: I
C
      INLET_ROW(:) = 0.0
      OUTLET_ROW(:) = 0.0
      INLET_COL(:) = 0.0
      OUTLET_COL(:) = 0.0
C
C     SETTING ARTIFICIAL TRANS FOR GROUP BC CELL
      GROUP_TRANS = (AVG_TRX + AVG_TRZ)/2000
      INLET_CC = GROUP_TRANS * FLOAT(NC)
      OUTLET_CC = GROUP_TRANS * FLOAT(NC)
C
C     SETTING ROW AND COLUMN VECTOR VALUES FOR INLET AND OUTLET
      FORALL (I = 1:NC) INLET_ROW(INLET(I)) = -GROUP_TRANS
      FORALL (I = 1:NC) OUTLET_ROW(OUTLET(I)) = -GROUP_TRANS
      FORALL (I = 1:NC) INLET_COL(INLET(I)) = -GROUP_TRANS
      FORALL (I = 1:NC) OUTLET_COL(OUTLET(I)) = -GROUP_TRANS
      FORALL (I = 1:NC) CC(INLET(I)) = CC(INLET(I)) + GROUP_TRANS
      FORALL (I = 1:NC) CC(OUTLET(I)) = CC(OUTLET(I))  + GROUP_TRANS
C
C     DEFINING BC TYPE LOGIC
      IF (INJRATE .GT. 0.0) THEN !INLET FLOW RATE BC
        INLET_RHS = INJRATE
      END IF
C
      IF (OUTRATE .GT. 0.0) THEN !OUTLET FLOW RATE BC
        OUTLET_RHS = OUTRATE
      END IF
C
      IF (FPSB .GE. 0.0) THEN !INLET PRESSURE BC
        INLET_CC = 1.0
        INLET_ROW(:) = 0.0
        INLET_RHS = FPSB
      END IF
C
      IF (OUTPSB .GE. 0.0) THEN !OUTLET PRESSURE BC
        OUTLET_CC = 1.0
        OUTLET_ROW(:) = 0.0
        OUTLET_RHS = OUTPSB
      END IF
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
!     MODIFIED BY: MATTHEW STADELMAN
!     MODFIED ON: 06/30/2016 TO IMPLEMENT GROUP BCs
!
      USE APM_MODULE
!
      IMPLICIT NONE
      REAL(8),ALLOCATABLE :: INLET_D4COL(:),INLET_D4ROW(:)
      REAL(8),ALLOCATABLE :: OUTLET_D4COL(:),OUTLET_D4ROW(:)
      REAL(8) :: RHS(*), X(*)
      REAL(8) :: TEMP_RHS,TEMP_INCOL,TEMP_OUTCOL,FACTOR,INLET_X,OUTLET_X
      INTEGER :: IBR,IBRU,JBR,IB,IBU
      INTEGER :: ICOL,JCOL,IL,ID,JD,IUP
!
      ALLOCATE(INLET_D4COL(NX*NZ),OUTLET_D4COL(NX*NZ))
      ALLOCATE(INLET_D4ROW(-NX*NZ:1),OUTLET_D4ROW(-NX*NZ-1:0))
      INLET_D4COL(:) = INLET_COL(:)
      OUTLET_D4COL(:) = OUTLET_COL(:)
!
!     ELIMINATING THE INLET AND OUTLET ROWS IN LEXOGRAPHICAL ORDER
!
      FORALL (IB = 1:NX*NZ) INLET_D4ROW(-IB) = INLET_ROW(IB)
      INLET_D4ROW(0) = INLET_CC
      FORALL (IB = 1:NX*NZ) OUTLET_D4ROW(-IB-1) = OUTLET_ROW(IB)
      OUTLET_D4ROW(0) = OUTLET_CC
      DO IB = 1, NX*NZ
!
!       HANDLING INLET ROW
        FACTOR = INLET_D4ROW(-IB)/CC(IB)
        DO ID = 1,4
          IF (LINK_D4(INO(IB),ID) == 0) CYCLE
          ICOL = -INAT(LINK_D4(INO(IB),ID))
          INLET_D4ROW(ICOL) = INLET_D4ROW(ICOL) - FACTOR*TT(IB,ID)
        END DO
        INLET_CC = INLET_CC - FACTOR*INLET_COL(IB)
        INLET_RHS = INLET_RHS - FACTOR*RHS(IB)
!
!       HANDLING OUTLET ROW
        FACTOR = OUTLET_D4ROW(-IB)/CC(IB)
        DO ID = 1,4
          IF (LINK_D4(INO(IB),ID) == 0) CYCLE
          ICOL = -INAT(LINK_D4(INO(IB),ID)) - 1 !- 1 TO ACCOUNT FOR INLET
          OUTLET_D4ROW(ICOL) = OUTLET_D4ROW(ICOL) - FACTOR*TT(IB,ID)
        END DO
        OUTLET_CC = OUTLET_CC - FACTOR*OUTLET_COL(IB)
        OUTLET_RHS = OUTLET_RHS - FACTOR*RHS(IB)
      END DO
      INLET_X = INLET_RHS/INLET_CC
      OUTLET_X = OUTLET_RHS/OUTLET_CC
!
!     ELIMINATION ON THE LOWER HALF OF THE MATRIX ROW BY ROW
!
      DO IBR = NUM_TOP+1,NUM_TOTAL
        IB = INAT(IBR) !INAT MAPS D4 ORDER TO LEXI ORDER
        TEMP_RHS = RHS(IB)
        TEMP_INCOL = INLET_COL(IB)
        TEMP_OUTCOL = OUTLET_COL(IB)
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
            TEMP_INCOL = TEMP_INCOL - FACTOR*INLET_D4COL(IBU)
            TEMP_OUTCOL = TEMP_OUTCOL - FACTOR*OUTLET_D4COL(IBU)
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
          TEMP_INCOL = TEMP_INCOL - FACTOR*INLET_D4COL(INAT(JBR))
          TEMP_OUTCOL = TEMP_OUTCOL - FACTOR*OUTLET_D4COL(INAT(JBR))
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
        INLET_D4COL(IB) = FACTOR*TEMP_INCOL
        OUTLET_D4COL(IB) = FACTOR*TEMP_OUTCOL
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
        TEMP_RHS = TEMP_RHS - INLET_D4COL(IB)*INLET_X
        TEMP_RHS = TEMP_RHS - OUTLET_D4COL(IB)*OUTLET_X
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
        TEMP_RHS = TEMP_RHS - INLET_COL(IB)*INLET_X
        TEMP_RHS = TEMP_RHS - OUTLET_COL(IB)*OUTLET_X
        X(IB) = TEMP_RHS/CC(IB)
      END DO
!
      !CALL QUIT(365)
!
      RETURN
C
      END SUBROUTINE
!
! ----------------------------------------------------------------------
! @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
! ----------------------------------------------------------------------
!
      SUBROUTINE GAUSS(RHS,X)
C
C     BANDED GAUSS SOLVER
C     WRITTEN BY: W. NEAL SAMS
C     DATE WRITTEN: 07/08/2013
C
      USE APM_MODULE
C
      IMPLICIT NONE
      REAL(8),ALLOCATABLE :: UPPER(:),B(:)
      REAL(8),ALLOCATABLE :: INLET_D4COL(:),INLET_D4ROW(:)
      REAL(8),ALLOCATABLE :: OUTLET_D4COL(:),OUTLET_D4ROW(:)
      REAL(8) :: RHS(*), X(*)
      REAL(8) :: FACTOR,INLET_X,OUTLET_X,TEMP_INCOL,TEMP_OUTCOL
      INTEGER(8) :: NXZ, IB, J, I, IA, IL, IB_UP, IU, JA, ICOL, ID
      INTEGER(8) :: IBAND
C
      NXZ = NX*NZ
      DEALLOCATE(ROW)
      ALLOCATE(ROW(-NX:NX),UPPER(NXZ*NX),B(NXZ))
!
      ALLOCATE(INLET_D4COL(NX*NZ),OUTLET_D4COL(NX*NZ))
      ALLOCATE(INLET_D4ROW(-NX*NZ:1),OUTLET_D4ROW(-NX*NZ-1:0))
      INLET_D4COL(:) = INLET_COL(:)
      OUTLET_D4COL(:) = OUTLET_COL(:)
!
      !
      IB = 0
      DO J = 1,NZ
        DO I = 1,NX
          !
          IB = IB + 1
          TEMP_INCOL = INLET_D4COL(IB)
          TEMP_OUTCOL = OUTLET_D4COL(IB)
C
C    BUILD ROW OF MATRIX
C
          ROW(:) = 0.0
          ROW(0) = CC(IB)
          IL = 0
          IF(I /= 1) THEN
            ROW(-1) = TT(IB,1)
            IL = -1
          ENDIF
          IF(J /= 1) THEN
            ROW(-NX) = TT(IB,3)
            IL = -NX
          ENDIF
          IF(I /= NX) ROW(1) = TT(IB,2)
          IF(J /= NZ) ROW(NX) = TT(IB,4)
C
C     ELIMINATE ELEMENTS TO THE LEFT OF THE DIAGONAL
C
          DO IA = IL,-1
            FACTOR = ROW(IA)
            IB_UP = IB + IA
            IU = NX*(IB_UP - 1) !WORKS BECAUSE OFF DIAGIONALS ARE NX AWAY
            DO JA = IA+1,IA+NX
              IU = IU + 1
              ROW(JA) = ROW(JA) - FACTOR*UPPER(IU)
            ENDDO
            TEMP_INCOL = TEMP_INCOL - FACTOR*INLET_D4COL(IB_UP)
            TEMP_OUTCOL = TEMP_OUTCOL - FACTOR*OUTLET_D4COL(IB_UP)
            RHS(IB) = RHS(IB) - FACTOR*RHS(IB_UP)
          ENDDO
C
C     STORE UPPER TRIANGLE
C
          IU = NX*(IB-1)
          DO IA = 1,NX
            IU = IU + 1
            UPPER(IU) = ROW(IA)/ROW(0)
          ENDDO
          INLET_D4COL(IB) = INLET_D4COL(IB)/ROW(0)
          OUTLET_D4COL(IB) = OUTLET_D4COL(IB)/ROW(0)
          RHS(IB) = RHS(IB)/ROW(0)
          !
        ENDDO
      ENDDO
!
!     ELIMINATING THE INLET AND OUTLET ROWS IN LEXOGRAPHICAL ORDER
!
      FORALL (IB = 1:NX*NZ) INLET_D4ROW(-IB) = INLET_ROW(IB)
      INLET_D4ROW(0) = INLET_CC
      FORALL (IB = 1:NX*NZ) OUTLET_D4ROW(-IB-1) = OUTLET_ROW(IB)
      OUTLET_D4ROW(0) = OUTLET_CC
      DO IB = 1, NX*NZ
!
!       HANDLING INLET ROW
        FACTOR = INLET_D4ROW(-IB)/CC(IB)
        DO ID = 1,4
          IF (LINK_D4(INO(IB),ID) == 0) CYCLE
          ICOL = -IB!-INAT(LINK_D4(INO(IB),ID))
          INLET_D4ROW(ICOL) = INLET_D4ROW(ICOL) - FACTOR*TT(IB,ID)
        END DO
        INLET_CC = INLET_CC - FACTOR*INLET_COL(IB)
        INLET_RHS = INLET_RHS - FACTOR*RHS(IB)
!
!       HANDLING OUTLET ROW
        FACTOR = OUTLET_D4ROW(-IB)/CC(IB)
        DO ID = 1,4
          IF (LINK_D4(INO(IB),ID) == 0) CYCLE
          ICOL = -IB - 1!-INAT(LINK_D4(INO(IB),ID)) - 1 !- 1 TO ACCOUNT FOR INLET
          OUTLET_D4ROW(ICOL) = OUTLET_D4ROW(ICOL) - FACTOR*TT(IB,ID)
        END DO
        OUTLET_CC = OUTLET_CC - FACTOR*OUTLET_COL(IB)
        OUTLET_RHS = OUTLET_RHS - FACTOR*RHS(IB)
      END DO
      INLET_X = INLET_RHS/INLET_CC
      OUTLET_X = OUTLET_RHS/OUTLET_CC


C
C     BACK SUBSTITUTION
C
      X(NXZ) = RHS(NXZ)
      DO IB = NXZ-1,1,-1
        IBAND = MIN(IB+NX, NXZ)
        IU = NX*(IB-1)
        FACTOR = RHS(IB)
        DO IA = IB+1,IBAND
          IU = IU + 1
          FACTOR = FACTOR - UPPER(IU)*X(IA)
        ENDDO
        FACTOR = FACTOR - INLET_D4COL(IB)*INLET_X
        FACTOR = FACTOR - OUTLET_D4COL(IB)*OUTLET_X
        X(IB) = FACTOR
      ENDDO
C
      DEALLOCATE (ROW, UPPER)
C
      RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C