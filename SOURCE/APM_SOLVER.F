C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE GAUSS(AD,AW,AC,AE,AU,RHS,NX,NZ,X)
C
C     BANDED GAUSS SOLVER
C     WRITTEN BY: W. NEAL SAMS
C     DATE WRITTEN: 07/08/2013
C
      IMPLICIT NONE
      REAL(8),ALLOCATABLE :: UPPER(:),ROW(:),B(:)
      REAL(8) :: AD(*), AW(*), AC(*), AE(*), AU(*), RHS(*), X(*)
      REAL(8) :: TEMP,ST,EN
      INTEGER :: NX, NZ
      INTEGER(8) :: NXZ, IB, J, I, IA, IL, IB_UP, IU, JA
      INTEGER(8) :: IBAND
      CHARACTER(120) :: C120
C
      NXZ = NX*NZ
      ALLOCATE(ROW(-NX:NX),UPPER(NXZ*NX),B(NXZ))
      !
      CALL CPU_TIME(ST)
      !
      IB = 0
      DO J = 1,NZ
        DO I = 1,NX
          !
          IB = IB + 1
C
C    BUILD ROW OF MATRIX
C
          ROW(:) = 0.0
          ROW(0) = AC(IB)
          IL = 0
          IF(I /= 1) THEN
            ROW(-1) = AW(IB)
            IL = -1
          ENDIF
          IF(J /= 1) THEN
            ROW(-NX) = AD(IB)
            IL = -NX
          ENDIF
          IF(I /= NX) ROW(1) = AE(IB)
          IF(J /= NZ) ROW(NX) = AU(IB)
C
C     ELIMINATE ELEMENTS TO THE LEFT OF THE DIAGONAL
C
          DO IA = IL,-1
            TEMP = ROW(IA)
            IB_UP = IB + IA
            IU = NX*(IB_UP - 1) !WORKS BECAUSE OFF DIAGIONALS ARE NX AWAY
            DO JA = IA+1,IA+NX
              IU = IU + 1
              ROW(JA) = ROW(JA) - TEMP*UPPER(IU)
            ENDDO
            RHS(IB) = RHS(IB) - TEMP*RHS(IB_UP)
          ENDDO
C
C     STORE UPPER TRIANGLE
C
          IU = NX*(IB-1)
          DO IA = 1,NX
            IU = IU + 1
            UPPER(IU) = ROW(IA)/ROW(0)
          ENDDO
          RHS(IB) = RHS(IB)/ROW(0)
          !
        ENDDO
      ENDDO
      !
      CALL CPU_TIME(EN)
      WRITE(C120,"(5X,'REQUIRED TIME FOR ELIMINATION: ',F13.6)")(EN-ST)
      CALL MESSAGE(C120)
      CALL CPU_TIME(ST)
C
C     BACK SUBSTITUTION
C
      X(NXZ) = RHS(NXZ)
      DO IB = NXZ-1,1,-1
        IBAND = MIN(IB+NX, NXZ)
        IU = NX*(IB-1)
        TEMP = RHS(IB)
        DO IA = IB+1,IBAND
          IU = IU + 1
          TEMP = TEMP - UPPER(IU)*X(IA)
        ENDDO
        X(IB) = TEMP
      ENDDO
      !
      CALL CPU_TIME(EN)
      WRITE(C120,"(5X,'REQUIRED TIME FOR BACK SUB: ',F13.6)")(EN-ST)
      CALL MESSAGE(C120)
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
      SUBROUTINE D4_GAUSS(AD,AW,AC,AE,AU,RHS,NX,NZ,X)
C
C     GAUSSIAN D4 ORDERED SOLVER
C     CONTROLS THE TWO SUBROUTINES THAT SOLVE FOR THE CHANGE IN PRESSURE
C
C     WRITTEN BY: MATTHEW STADELMAN
C     DATE WRITTEN: 01/29/2016
C
      USE D4_MODULE
C
      IMPLICIT NONE
      REAL(8) :: AD(*), AW(*), AC(*), AE(*), AU(*), RHS(*), X(*)
      REAL(8) :: ST,EN
      INTEGER :: I, NX, NZ, NXZ
      CHARACTER(120) :: C120
C
      !
      IF (FIRST_RUN) THEN
        !
        CALL CPU_TIME(ST)
        NXZ = NX*NZ
        CALL ALLOCATE_COEF(NXZ)
        !
        ! POPULATING COEFFICIENT ARRAYS
        FORALL (I = 1:NXZ) CC(I)   = AC(I)
        FORALL (I = 1:NXZ) TT(I,1) = AW(I)
        FORALL (I = 1:NXZ) TT(I,2) = AE(I)
        FORALL (I = 1:NXZ) TT(I,3) = AD(I)
        FORALL (I = 1:NXZ) TT(I,4) = AU(I)
        !
        CALL D4_REORDER(NX,NZ)
        !
        CALL CPU_TIME(EN)
        WRITE(*,"(5X,'REQUIRED TIME TO REORDER:',F11.6)")(EN-ST)
      END IF
      !
      CALL CPU_TIME(ST)
      !
      CALL D4_SOLVER(RHS,X)
      !
      CALL CPU_TIME(EN)
      WRITE(C120,"(5X,'REQUIRED TIME FOR SOLUTION: ',F13.6)")(EN-ST)
      CALL MESSAGE(C120)
C
      RETURN
C
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
C ----------------------------------------------------------------------
C
      SUBROUTINE D4_REORDER(NX,NZ)
C
C     WRITTEN BY: W. NEAL SAMS
C     DATE WRITTEN: 02/29/2016
C
      USE D4_MODULE
C
      IMPLICIT NONE
      INTEGER :: NX,NZ,NXZ
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
      USE D4_MODULE
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
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE JACOBI(AD,AW,AC,AE,AU,RHS,NX,NZ,X)
C
C     JACOBI ITTERATIVE SOLVER
C     Solves Ax=b where A is a square matrix of size NX*NZ
C     with four off diagonals at -nx, -1, 1, nx.
C
C     Taken from:
C     @inbook{doi:10.1137/1.9781611971446.ch6,
C     title = {6. Iterative Methods for Linear Systems},
C     booktitle = {Applied Numerical Linear Algebra},
C     chapter = {6},
C     pages = {265-360},
C     doi = {10.1137/1.9781611971446.ch6},
C     URL = {http://epubs.siam.org/doi/abs/10.1137/1.9781611971446.ch6},
C     eprint = {http://epubs.siam.org/doi/pdf/10.1137/1.9781611971446.ch6}
C     }
C
C     WRITTEN BY: SETH KING
C     DATE WRITTEN: 12/11/2015
C
C     AW = -1 off diagonals elements
C     AD = -nx off diagonal elements
C     AC = main diagonal elements
C     AU = +1 off diagonal elements
C     AE = +nx off diagonal elements
C     RHS = Right hand side of the equation (b in Ax=b)
C     NX = number of elements in x direction
C     NZ = number of elements in y direction
C     X = Solution variable (input initial guess)
C
C-------------------------------------------------------------------------
      IMPLICIT NONE
      REAL(8) :: AD(*), AW(*), AC(*), AE(*), AU(*), RHS(*), X(*)
      REAL(8) :: TEMP, RMAX, Q, QMAX, TOL
      INTEGER :: NX, NZ, IB, J, I, IT, ITMAX
C
      TOL = 1E-05
      ITMAX = 10000
      ITERATION: DO IT = 1, ITMAX
        IB = 0
        DO J = 1, NZ
          DO I = 1, NX
            IB = (J-1)*NX + I
            TEMP = RHS(IB)
            IF(I /= 1) TEMP = TEMP - AW(IB)*X(IB-1)
            IF(J /= 1) TEMP = TEMP - AD(IB)*X(IB-NX)
            IF(I /= NX) TEMP = TEMP - AE(IB)*X(IB+1)
            IF(J /= NZ) TEMP = TEMP - AU(IB)*X(IB+NX)
            X(IB) = TEMP/AC(IB)
          END DO
        END DO

        RMAX = 0.0
        QMAX = 0.0
        IB = 0
        DO J = 1, NZ
          DO I = 1, NX
            Q = 0.0
            IB = IB + 1
            TEMP = RHS(IB)
            IF(I /= 1) Q = ABS(AW(IB)*X(IB-1))
            IF(I /= 1) TEMP = TEMP - AW(IB)*X(IB-1)
            IF(Q > QMAX) QMAX = Q
            IF(J /= 1) Q = ABS(AD(IB)*X(IB-NX))
            IF(J /= 1) TEMP = TEMP - AD(IB)*X(IB-NX)
            IF(Q > QMAX) QMAX = Q
            IF(I /= NX) Q = ABS(AE(IB)*X(IB+1))
            IF(I /= NX) TEMP = TEMP - AE(IB)*X(IB+1)
            IF(Q > QMAX) QMAX = Q
            IF(J /= NZ) Q = ABS(AE(IB)*X(IB+1))
            IF(J /= NZ) TEMP = TEMP - AE(IB)*X(IB+1)
            IF(Q > QMAX) QMAX = Q
            Q = ABS(AC(IB)*X(IB))
            TEMP = TEMP - AC(IB)*X(IB)
            IF(Q > QMAX) QMAX = Q
            TEMP = ABS(TEMP)
            IF(TEMP > RMAX) RMAX = TEMP
          END DO
        END DO
        IF (RMAX/QMAX < TOL) EXIT ITERATION
      END DO ITERATION
      PRINT *,"TOL: ",TOL, "RMAX: ",RMAX/QMAX, "TOTAL ITS", IT
      RETURN
      END SUBROUTINE JACOBI
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
C-------------------------------------------------------------------------
      SUBROUTINE MATRIX_MULTIPLY(AW,AD,AC,AU,AE,X,B,NX,NZ)
C-------------------------------------------------------------------------
C
C     MATRIX VECTOR MULTIPLICATION
C     Returns b for Ax=b where A is a square matrix of size NX*NZ
C     with four off diagonals at -nx, -1, 1, nx.
C
C-------------------------------------------------------------------------
      IMPLICIT NONE
      REAL(8) :: AD(*), AW(*), AC(*), AE(*), AU(*), X(*), B(*)
      REAL(8) :: TEMP
      INTEGER :: NX, NZ, IB, I, J

      IB = 0
      DO J = 1, NZ
        DO I = 1, NX
          IB = IB + 1
          TEMP = 0
          IF(I /= 1) TEMP = TEMP + AW(IB)*X(IB-1)
          IF(J /= 1) TEMP = TEMP + AD(IB)*X(IB-NX)
          IF(I /= NX) TEMP = TEMP + AE(IB)*X(IB+1)
          IF(J /= NZ) TEMP = TEMP + AU(IB)*X(IB+NX)
          TEMP = TEMP + AC(IB)*X(IB)
          B(IB) = TEMP
        END DO
      END DO
      RETURN
C-------------------------------------------------------------------------
      END SUBROUTINE MATRIX_MULTIPLY
C-------------------------------------------------------------------------

C-------------------------------------------------------------------------
      SUBROUTINE VECTOR_MULTIPLY(X, B, NXZ)
C-------------------------------------------------------------------------
C
C     VECTOR MULTIPLICATION
C     Returns b for xTx=b
C
C-------------------------------------------------------------------------
      IMPLICIT NONE
      REAL(8) :: X(*),B
      INTEGER :: I,NXZ

      B = 0
      DO I = 1, NXZ
        B = B + X(I)*X(I)
      END DO
      RETURN
C-------------------------------------------------------------------------
      END SUBROUTINE VECTOR_MULTIPLY
C-------------------------------------------------------------------------

C-------------------------------------------------------------------------
      SUBROUTINE XAX_MULTIPLY(X, AX, B, NXZ)
C-------------------------------------------------------------------------
C
C     VECTOR MULTIPLICATION
C     Returns b for (xT)Ax=b
C
C-------------------------------------------------------------------------
      IMPLICIT NONE
      REAL(8) :: X(*), AX(*), B
      INTEGER :: NXZ, J

      B = 0
      DO J = 1, NXZ
        B = B + X(J)*AX(J)
      END DO
      RETURN
C-------------------------------------------------------------------------
      END SUBROUTINE XAX_MULTIPLY
C-------------------------------------------------------------------------

C-------------------------------------------------------------------------
      SUBROUTINE CG(AD,AW,AC,AE,AU,RHS,NX,NZ,X)
C-------------------------------------------------------------------------
C
C     CONJUGATE GRADIENT ITTERATIVE SOLVER
C     Solves Ax=b where A is a square matrix of size NX*NZ

C     with four off diagonals at -nx, -1, 1, nx.
C
C     Taken from:
C
C     WRITTEN BY: SETH KING
C     DATE WRITTEN: 12/12/2015
C
C     AW = -1 off diagonals elements
C     AD = -nx off diagonal elements
C     AC = main diagonal elements
C     AU = +1 off diagonal elements
C     AE = +nx off diagonal elements
C     RHS = Right hand side of the equation (b in Ax=b)
C     NX = number of elements in x direction
C     NZ = number of elements in y direction
C     X = Solution variable (input initial guess)
C
C-------------------------------------------------------------------------
      IMPLICIT NONE
      REAL(8) :: AD(*), AW(*), AC(*), AE(*), AU(*), RHS(*), X(*)
      REAL(8), ALLOCATABLE :: R(:), P(:), AP(:)
      REAL(8) ::  RMAX, TOL, ALPHA, BETA, RTR, TEMP
      INTEGER :: NX, NZ, NXZ, IB, IT, ITMAX

      NXZ = NX*NZ
      ITMAX = 1000
      TOL = 1E-10
      ALLOCATE( R(NXZ), P(NXZ), AP(NXZ) )

      CALL MATRIX_MULTIPLY(AD, AW, AC, AE, AU, X, AP, NX, NZ)
      FORALL(IB=1:NXZ)
        R(IB) = RHS(IB) - AP(IB)
      END FORALL
      P = R
      CALL VECTOR_MULTIPLY(R, RTR, NXZ)

      ITERATION: DO IT = 1,ITMAX
        CALL MATRIX_MULTIPLY(AD, AW, AC, AE, AU, P, AP, NX, NZ)
        CALL XAX_MULTIPLY(P, AP, TEMP, NXZ)
        ALPHA = RTR/TEMP
        FORALL(IB=1:NXZ)
          X(IB) = X(IB) + ALPHA*P(IB)
        END FORALL
        CALL MATRIX_MULTIPLY(AD,AW,AC,AE,AU,X,AP,NX,NZ)
        FORALL(IB=1:NXZ)
          R(IB) = RHS(IB) - AP(IB)
        END FORALL
        RMAX = 0
        DO IB = 1,NXZ
          IF(R(IB)>RMAX)RMAX=R(IB)
        END DO
        PRINT *, RMAX
        IF(RMAX < TOL) EXIT ITERATION
        CALL VECTOR_MULTIPLY(R, TEMP, NXZ)
        BETA = TEMP/RTR
        RTR = TEMP
        P = R + BETA*P
      END DO ITERATION
      WRITE(*,*)IT, RMAX
      DEALLOCATE( R, P, AP)
      RETURN

C-------------------------------------------------------------------------
      END SUBROUTINE CG
C-------------------------------------------------------------------------

C-------------------------------------------------------------------------
      SUBROUTINE DUMMY_SOLVE(AW,AD,AC,AU,AE,RHS,NX,NZ,X)
C-------------------------------------------------------------------------
      IMPLICIT NONE
      REAL(8) :: AD(*), AW(*), AC(*), AE(*), AU(*), RHS(*), X(*)
      REAL(8), ALLOCATABLE :: RHS_SAVE(:)
      REAL(8) :: TEMP, RMAX
      INTEGER :: NX, NZ, NXZ, IB, J, I, IFILE

      NXZ = NX*NZ
      allocate( RHS_SAVE(NXZ) )
      RHS_SAVE(1:NXZ) = RHS(1:NXZ)
      IFILE = 35
      OPEN(UNIT=IFILE, FILE='LINEAR_SYSTEM2.CSV')
      WRITE(IFILE, *)'AD , AW , AC , AU , AE , RHS, NX=', NX, ', NZ=',NZ
      DO IB = 1, NXZ
        WRITE(IFILE, 300) AD(IB),AW(IB),AC(IB),AU(IB),AE(IB),RHS(IB)
      END DO
      CLOSE(IFILE)
      CALL GAUSS(AD,AW,AC,AE,AU,RHS,NX,NZ,X)
      RMAX = 0.0
      IB = 0
      DO J = 1, NZ
        DO I = 1, NX
          IB = IB + 1
          TEMP = RHS_SAVE(IB)
          IF(I /= 1) TEMP = TEMP - AW(IB)*X(IB-1)
          IF(J /= 1) TEMP = TEMP - AD(IB)*X(IB-NX)
          IF(I /= NX) TEMP = TEMP - AE(IB)*X(IB+1)
          IF(J /= NZ) TEMP = TEMP - AU(IB)*X(IB+NX)
          TEMP = TEMP - AC(IB)*X(IB)
          TEMP = ABS(TEMP)
          IF(TEMP > RMAX) RMAX = TEMP
        END DO
      END DO
      OPEN(UNIT=IFILE, FILE='LINEAR_SOLUTION2.CSV')
      WRITE(IFILE,290)NX, NZ, RMAX
      DO IB=1,NXZ
        WRITE(IFILE, '(F15.4)')X(IB)
      END DO
      RETURN
 290  FORMAT(2(I4, ' , '),'MAX RES=',E15.4)
 300  FORMAT(6(EN15.4, ' , '))
C-------------------------------------------------------------------------
      END SUBROUTINE DUMMY_SOLVE
C-------------------------------------------------------------------------


