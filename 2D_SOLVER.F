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
            WRITE(*,"(I3,1X,I3,1X,I3,1X,E10.4)")IB,IA,IU,UPPER(IU)
          ENDDO
          RHS(IB) = RHS(IB)/ROW(0)
          PRINT *, " "
          !
        ENDDO
      ENDDO
      !
      CALL CPU_TIME(EN)
      WRITE(*,"(1X,'REQUIRED TIME FOR ELIMINATION:',F11.6)")(EN-ST)
      !
      PRINT *, ""
      PRINT *, ""

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
      DEALLOCATE (ROW, UPPER)
C
      RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE D4_GAUSS(AW,AD,AC,AU,AE,RHS,NX,NZ,X)
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
      REAL(8), ALLOCATABLE :: ROW_VALS(:,:)
      REAL(8) :: AD(*), AW(*), AC(*), AE(*), AU(*), RHS(*), X(*)
      INTEGER, ALLOCATABLE :: ROW_COLS(:,:)
      INTEGER :: I,IB,IX,IZ,ROW,COL
      INTEGER :: NX, NZ
C
      ALLOCATE(ROW_COLS(NX*NZ,0:4),ROW_VALS(NX*NZ,0:4))
      ROW_COLS(:,:) = 0
      ROW_VALS(:,:) = 0
C
C     MAPPING THE DIAGONALS INTO THE D4 ORDERING SCHEME
      CALL D4_MAPPER(AW,AD,AC,AU,AE,NX,NZ,ROW_COLS,ROW_VALS)
C
C     PERFORMING GAUSSIAN ELIMINATION ON THE MATRIX
      PRINT *, "WIP"
C
      RETURN
C
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE D4_MAPPER(AW,AD,AC,AU,AE,NX,NZ,ROW_COLS,ROW_VALS)
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
      INTEGER, ALLOCATABLE :: D4_MAP(:)
      INTEGER :: I,IB,IX,IZ,ROW,COL
      INTEGER :: NX, NZ
      !
      REAL(8) :: ROW_VALS(NX*NZ,0:4)
      INTEGER :: ROW_COLS(NX*NZ,0:4)
C
      ALLOCATE(D4_MAP(NZ*NX))
      D4_MAP(:)   = 0
      ROW_COLS(:,:) = 0
      ROW_VALS(:,:) = 0
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
      PRINT *, ""
      DO IZ = NZ,1,-1
        I = NX*(IZ-1) 
        WRITE(*,"(*(I3,' ',:))")D4_MAP(I+1:I+NX)
      END DO
C
C     MAPPING DIAGONAL VALUES TO ROW ARRAYS
      IB = 1
      ! MAPPING BLC BLOCK
      ROW_COLS(IB,0) = D4_MAP(IB)
      ROW_COLS(IB,1) = D4_MAP(IB+NX)
      ROW_COLS(IB,2) = D4_MAP(IB+1)
      ROW_VALS(IB,0) = AC(IB)
      ROW_VALS(IB,1) = AU(IB)
      ROW_VALS(IB,2) = AE(IB)       
      ! MAPPING BOTTOM ROW OF BLOCKS
      DO IX = 2,NX-1
        IB = IX
        ROW_COLS(IB,0) = D4_MAP(IB)
        ROW_COLS(IB,1) = D4_MAP(IB-1)
        ROW_COLS(IB,2) = D4_MAP(IB+NX)
        ROW_COLS(IB,3) = D4_MAP(IB+1)
        ROW_VALS(IB,0) = AC(IB)
        ROW_VALS(IB,1) = AW(IB)
        ROW_VALS(IB,2) = AU(IB)
        ROW_VALS(IB,3) = AE(IB)         
      END DO
      ! MAPPING BRC BLOCK
      IB = NX
      ROW_COLS(IB,0) = D4_MAP(IB)
      ROW_COLS(IB,1) = D4_MAP(IB-1)
      ROW_COLS(IB,2) = D4_MAP(IB+NX)
      ROW_VALS(IB,0) = AC(IB)
      ROW_VALS(IB,1) = AW(IB)
      ROW_VALS(IB,2) = AU(IB)
      !
      DO IZ = 1,NZ-2
        ! MAPPING LEFT COLUMN BLOCKS
        IB = NX*IZ + 1
        ROW_COLS(IB,0) = D4_MAP(IB)
        ROW_COLS(IB,1) = D4_MAP(IB-NX)
        ROW_COLS(IB,2) = D4_MAP(IB+NX)
        ROW_COLS(IB,3) = D4_MAP(IB+1)
        ROW_VALS(IB,0) = AC(IB)
        ROW_VALS(IB,1) = AD(IB)
        ROW_VALS(IB,2) = AU(IB)
        ROW_VALS(IB,3) = AE(IB) 
        DO IX = 2,NX-1
          ! MAPPING INTERNAL BLOCKS
          IB = NX*IZ + IX
          ROW_COLS(IB,0) = D4_MAP(IB)
          ROW_COLS(IB,1) = D4_MAP(IB-1)
          ROW_COLS(IB,2) = D4_MAP(IB-NX)
          ROW_COLS(IB,3) = D4_MAP(IB+NX)
          ROW_COLS(IB,4) = D4_MAP(IB+1)
          ROW_VALS(IB,0) = AC(IB)
          ROW_VALS(IB,1) = AW(IB) 
          ROW_VALS(IB,2) = AD(IB)
          ROW_VALS(IB,3) = AU(IB)
          ROW_VALS(IB,4) = AE(IB)        
        END DO
        ! MAPPING RIGHT COLUMN BLOCKS
        IB = NX*IZ + NX 
        ROW_COLS(IB,0) = D4_MAP(IB)
        ROW_COLS(IB,1) = D4_MAP(IB-1)
        ROW_COLS(IB,2) = D4_MAP(IB-NX)
        ROW_COLS(IB,3) = D4_MAP(IB+NX)
        ROW_VALS(IB,0) = AC(IB)
        ROW_VALS(IB,1) = AW(IB) 
        ROW_VALS(IB,2) = AD(IB)
        ROW_VALS(IB,3) = AU(IB)
      END DO
      ! MAPPING TLC BLOCK
      IB = NX*(NZ - 1) + 1
      ROW_COLS(IB,0) = D4_MAP(IB)
      ROW_COLS(IB,1) = D4_MAP(IB-NX)
      ROW_COLS(IB,2) = D4_MAP(IB+1)
      ROW_VALS(IB,0) = AC(IB)
      ROW_VALS(IB,1) = AD(IB)
      ROW_VALS(IB,2) = AE(IB)   
      DO IX = 2,NX-1
        ! MAPPING TOP ROW BLOCKS
        IB = NX*(NZ - 1) + IX
        ROW_COLS(IB,0) = D4_MAP(IB)
        ROW_COLS(IB,1) = D4_MAP(IB-1)
        ROW_COLS(IB,2) = D4_MAP(IB-NX)
        ROW_COLS(IB,3) = D4_MAP(IB+1)
        ROW_VALS(IB,0) = AC(IB)
        ROW_VALS(IB,1) = AW(IB)
        ROW_VALS(IB,2) = AD(IB)
        ROW_VALS(IB,3) = AE(IB) 
      END DO
      ! MAPPING TRC BLOCK
      IB = NX*(NZ - 1) + NX
      ROW_COLS(IB,0) = D4_MAP(IB)
      ROW_COLS(IB,1) = D4_MAP(IB-1)
      ROW_COLS(IB,2) = D4_MAP(IB-NX)
      ROW_VALS(IB,0) = AC(IB)
      ROW_VALS(IB,1) = AW(IB)
      ROW_VALS(IB,2) = AD(IB)
C
      RETURN
C
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE JACOBI(AW,AD,AC,AU,AE,RHS,NX,NZ,X)
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
      SUBROUTINE CG(AW,AD,AC,AU,AE,RHS,NX,NZ,X)
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


