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
      ALLOCATE (ROW(-NX:NX), UPPER(NXZ*NX),B(NXZ))
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
      WRITE(C120,"(5X,'REQUIRED TIME FOR ELIMINATION:',F11.6)")(EN-ST)
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
      WRITE(C120,"(5X,'REQUIRED TIME FOR BACK SUB:',F11.6)")(EN-ST) 
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
C     TRANSFORMS THE SUPPLIED REGULAR ORDERED DIAGIONALS INTO THE 
C     D4 ORDERING SCHEME AND THEN PERFORMS REGULAR GUASSIAN ELIMINATION
C     AND BACK SUBSTITUTION ON LINEAR SYSTEM. LOOSELY BASED ON 
C     USGS MODFLOW D4 SOLVER :
C     http://water.usgs.gov/software/code/ground_water/modflow/doc/ofr95288.pdf
C
C     WRITTEN BY: MATTHEW STADELMAN
C     DATE WRITTEN: 01/29/2016
C
      IMPLICIT NONE
      REAL(8), ALLOCATABLE :: ROW_VALS(:,:),ROW(:),UPPER_VALS(:,:)
      REAL(8), ALLOCATABLE :: D4_RHS(:), D4_X(:)
      REAL(8) :: AD(*), AW(*), AC(*), AE(*), AU(*), RHS(*), X(*)
      REAL(8) :: TEMP,ST,EN
      INTEGER, ALLOCATABLE :: D4_MAP(:),ROW_COLS(:,:),UPPER_COLS(:,:)
      INTEGER :: I,N,IB,IU,IX,IZ
      INTEGER :: NX, NZ
      CHARACTER(120) :: C120
C
      ALLOCATE(D4_MAP(NX*NZ),D4_RHS(NX*NZ),D4_X(NX*NZ))
      ALLOCATE(ROW_COLS(NX*NZ,0:4),ROW_VALS(NX*NZ,0:4),ROW(0:NX*NZ))
      ALLOCATE(UPPER_VALS(NX*NZ,NX+NZ),UPPER_COLS(NX*NZ,NX+NZ))
      UPPER_COLS = 0
      UPPER_VALS = 0.0
      !
      CALL CPU_TIME(ST)
      !
C
C     MAPPING THE DIAGONALS INTO THE D4 ORDERING SCHEME
      CALL MAKE_D4_MAP(D4_MAP,NX,NZ)
      !
      CALL CPU_TIME(EN)
      WRITE(*,"(1X,'REQUIRED TIME TO MAKE MAP:',F11.6)")(EN-ST)
      CALL CPU_TIME(ST)
      CALL D4_MAPPER(AD,AW,AC,AE,AU,NX,NZ,ROW_COLS,ROW_VALS,D4_MAP)
C
C     REORDERING THE RHS VECTOR TO THE D4 SCHEME
      DO IB = 1,NX*NZ
        I = D4_MAP(IB)
        D4_RHS(I) = RHS(IB)
      END DO
      D4_X(:) = 0.0
      !
      CALL CPU_TIME(EN)
      WRITE(*,"(1X,'REQUIRED TIME TO MAP DIAGS:',F11.6)")(EN-ST)
      CALL CPU_TIME(ST)
C
C     PERFORMING GAUSSIAN ELIMINATION ON THE MATRIX
      DO IZ = 0,NZ-1
        DO IX = 1,NX
          IB = NX*IZ + IX
          !
          ! BUILDING ROW OF MATRIX
          ROW(:) = 0.0
          ROW(ROW_COLS(IB,0)) = ROW_VALS(IB,0)
          DO I = 1,4
            ROW(ROW_COLS(IB,I)) = ROW_VALS(IB,I)
          END DO
          !
          ! ELIMINATING ELEMENTS LEFT OF THE DIAGONAL
          DO I = ROW_COLS(IB,1),IB-1
            TEMP = ROW(I)
            IF (ABS(TEMP) < TINY(TEMP)) CYCLE
            DO N = 1,NX+NZ
              IF (UPPER_COLS(I,N) == 0) EXIT
              IU = UPPER_COLS(I,N)
              ROW(IU) = ROW(IU) - TEMP*UPPER_VALS(I,N)
            END DO
            ROW(I) = 0.0 !JUST HERE FOR PRINTING PURPOSES
            D4_RHS(IB) = D4_RHS(IB) - TEMP*D4_RHS(I)
            !
          END DO
          !
          ! STORING UPPER TRIANGLE
          N = 1
          DO I = IB+1,NX*NZ
            IF (ROW(I) == 0.0) CYCLE
            UPPER_COLS(IB,N) = I
            UPPER_VALS(IB,N) = ROW(I)/ROW(IB)
            N = N + 1
          END DO
          D4_RHS(IB) = D4_RHS(IB)/ROW(IB)
        END DO
      END DO
      !
      CALL CPU_TIME(EN)
      WRITE(C120,"(5X,'REQUIRED TIME FOR ELIMINATION: ',F13.6)")(EN-ST)
      CALL MESSAGE(C120)
      CALL CPU_TIME(ST)
C
C     BACK SUBSTITUTION
      D4_X(NX*NZ) = D4_RHS(NX*NZ)
      DO IB = NX*NZ-1,1,-1
        TEMP = D4_RHS(IB)
        DO N = 1,NX+NZ
          IF (UPPER_COLS(IB,N) == 0) EXIT
          IU = UPPER_COLS(IB,N)
          TEMP = TEMP - UPPER_VALS(IB,N)*D4_X(IU)
        END DO
        D4_X(IB) = TEMP
      END DO
      !
      CALL CPU_TIME(EN)
      WRITE(C120,"(5X,'REQUIRED TIME FOR BACK SUB: ',F13.6)")(EN-ST) 
      CALL MESSAGE(C120)
C
C     REMAPPING VALUES BACK TO REGULAR ORDER
      DO IB = 1,NX*NZ
        I = D4_MAP(IB)
        RHS(IB) = D4_RHS(I)
        X(IB)   = D4_X(I)
      END DO
C
C     ARRAY DEALLOCATIONS
      DEALLOCATE(ROW_COLS,ROW_VALS,ROW,UPPER_COLS,UPPER_VALS)
      RETURN
C
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE MAKE_D4_MAP(D4_MAP,NX,NZ)
C
C     DESCRIPTION: MAKES THE D4 ORDERED MAP USED TO TRANSFORM THE 
C        REGULAR ORDERED MATRIX INTO D4 ORDERING
C
C     WRITTEN BY: MATTHEW STADELMAN
C     DATE WRITTEN: 01/29/2016
C
      IMPLICIT NONE
      INTEGER :: D4_MAP(*)
      INTEGER :: I,IB,IX,IZ,ROW,COL
      INTEGER :: NX, NZ
C
      D4_MAP(1:NX*NZ) = 0
C
C     CREATING D4 MAP TO REORDER EQUATIONS 
C     SETTING FIRST SET OF DIAGONALS
      ROW = 1
      COL = 1
      IX  = 1
      IZ  = 1
      IB  = 1
  100 DO WHILE (IB <= NX*NZ)
        I = NX*(IZ-1) + IX
        IF (I > NX*NZ) EXIT
        !
        D4_MAP(I) = IB
        IZ = IZ - 1
        IX = IX + 1
        IB = IB + 1
        !
        IF ((IZ < 1) .OR. (IX > NX)) THEN
          IF (ROW + 2 <= NZ) THEN
            ROW  = ROW + 2
          ELSE IF (ROW + 1 == NZ) THEN
            ROW = NZ
            COL = COL + 1
          ELSE
            COL = COL + 2
          END IF
          !
          IZ = ROW
          IX = COL
        END IF
      END DO
C     RESETTING INPUTS TO FILL ALTERNATE SET OF DIAGIONALS
      ROW = 2
      COL = 1
      IZ  = 2
      IX  = 1
      IF (IB < NX*NZ) GOTO 100
C
C
      RETURN
C
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE D4_MAPPER(AD,AW,AC,AE,AU,NX,NZ,ROW_COLS,ROW_VALS,MAP)
C
C     DESCRIPTION: TRANSFORMS THE SUPPLIED REGULAR ORDERED DIAGIONALS  
C     INTO THE D4 ORDERING SCHEME STORING THE  NON-ZERO 
C     INDICIES AND VALS IN TWO COMPRESSED ROW ARRAYS
C
C     WRITTEN BY: MATTHEW STADELMAN
C     DATE WRITTEN: 01/29/2016
C
      IMPLICIT NONE
      REAL(8) :: AD(*), AW(*), AC(*), AE(*), AU(*)
      INTEGER :: MAP(*)
      INTEGER :: I,IB,IX,IZ
      INTEGER :: NX, NZ
      !
      REAL(8) :: ROW_VALS(NX*NZ,0:4)
      INTEGER :: ROW_COLS(NX*NZ,0:4)
C
      ROW_COLS(:,:) = 0
      ROW_VALS(:,:) = 0
C
C     MAPPING DIAGONAL VALUES TO ROW ARRAYS
      IB = 1
      I  = MAP(IB)
      ! MAPPING BLC BLOCK
      ROW_COLS(I,0) = MAP(IB)
      ROW_COLS(I,1) = MAP(IB+NX)
      ROW_COLS(I,2) = MAP(IB+1)
      ROW_VALS(I,0) = AC(IB)
      ROW_VALS(I,1) = AU(IB)
      ROW_VALS(I,2) = AE(IB)       
      ! MAPPING BOTTOM ROW OF BLOCKS
      DO IX = 2,NX-1
        IB = IX
        I  = MAP(IB)
        ROW_COLS(I,0) = MAP(IB)
        ROW_COLS(I,1) = MAP(IB-1)
        ROW_COLS(I,2) = MAP(IB+NX)
        ROW_COLS(I,3) = MAP(IB+1)
        ROW_VALS(I,0) = AC(IB)
        ROW_VALS(I,1) = AW(IB)
        ROW_VALS(I,2) = AU(IB)
        ROW_VALS(I,3) = AE(IB)  
      END DO
      ! MAPPING BRC BLOCK
      IB = NX
      I  = MAP(IB)
      ROW_COLS(I,0) = MAP(IB)
      ROW_COLS(I,1) = MAP(IB-1)
      ROW_COLS(I,2) = MAP(IB+NX)
      ROW_VALS(I,0) = AC(IB)
      ROW_VALS(I,1) = AW(IB)
      ROW_VALS(I,2) = AU(IB)
      !
      DO IZ = 1,NZ-2
        ! MAPPING LEFT COLUMN BLOCKS
        IB = NX*IZ + 1
        I  = MAP(IB)
        ROW_COLS(I,0) = MAP(IB)
        ROW_COLS(I,1) = MAP(IB-NX)
        ROW_COLS(I,2) = MAP(IB+NX)
        ROW_COLS(I,3) = MAP(IB+1)
        ROW_VALS(I,0) = AC(IB)
        ROW_VALS(I,1) = AD(IB)
        ROW_VALS(I,2) = AU(IB)
        ROW_VALS(I,3) = AE(IB) 
        DO IX = 2,NX-1
          ! MAPPING INTERNAL BLOCKS
          IB = NX*IZ + IX
          I  = MAP(IB)
          ROW_COLS(I,0) = MAP(IB)
          ROW_COLS(I,1) = MAP(IB-1)
          ROW_COLS(I,2) = MAP(IB-NX)
          ROW_COLS(I,3) = MAP(IB+NX)
          ROW_COLS(I,4) = MAP(IB+1)
          ROW_VALS(I,0) = AC(IB)
          ROW_VALS(I,1) = AW(IB) 
          ROW_VALS(I,2) = AD(IB)
          ROW_VALS(I,3) = AU(IB)
          ROW_VALS(I,4) = AE(IB)        
        END DO
        ! MAPPING RIGHT COLUMN BLOCKS
        IB = NX*IZ + NX 
        I  = MAP(IB)
        ROW_COLS(I,0) = MAP(IB)
        ROW_COLS(I,1) = MAP(IB-1)
        ROW_COLS(I,2) = MAP(IB-NX)
        ROW_COLS(I,3) = MAP(IB+NX)
        ROW_VALS(I,0) = AC(IB)
        ROW_VALS(I,1) = AW(IB) 
        ROW_VALS(I,2) = AD(IB)
        ROW_VALS(I,3) = AU(IB)
      END DO
      ! MAPPING TLC BLOCK
      IB = NX*(NZ - 1) + 1
      I  = MAP(IB)
      ROW_COLS(I,0) = MAP(IB)
      ROW_COLS(I,1) = MAP(IB-NX)
      ROW_COLS(I,2) = MAP(IB+1)
      ROW_VALS(I,0) = AC(IB)
      ROW_VALS(I,1) = AD(IB)
      ROW_VALS(I,2) = AE(IB)   
      DO IX = 2,NX-1
        ! MAPPING TOP ROW BLOCKS
        IB = NX*(NZ - 1) + IX
        I  = MAP(IB)
        ROW_COLS(I,0) = MAP(IB)
        ROW_COLS(I,1) = MAP(IB-1)
        ROW_COLS(I,2) = MAP(IB-NX)
        ROW_COLS(I,3) = MAP(IB+1)
        ROW_VALS(I,0) = AC(IB)
        ROW_VALS(I,1) = AW(IB)
        ROW_VALS(I,2) = AD(IB)
        ROW_VALS(I,3) = AE(IB) 
      END DO
      ! MAPPING TRC BLOCK
      IB = NX*(NZ - 1) + NX
      I  = MAP(IB)
      ROW_COLS(I,0) = MAP(IB)
      ROW_COLS(I,1) = MAP(IB-1)
      ROW_COLS(I,2) = MAP(IB-NX)
      ROW_VALS(I,0) = AC(IB)
      ROW_VALS(I,1) = AW(IB)
      ROW_VALS(I,2) = AD(IB)
C
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


