      SUBROUTINE FRAC_FLOW(BOK)
C 
C     WRITTEN BY: MATTHEW STADELMAN
C
C     DATE WRITTEN:  2015/03/02 
C     LAST MODIFIED: 2016/02/08 
C
C     PROGRAM DESCRIPTION: SOLVES FOR THE STEADY STATE FLOW THROUGH THE 
C         FRACTURE. 
C 
C     SUBROUTINE CALLS: SOLVER, PS_TO_PR
C
C ---------------------------------------------------------------------
C     VARIABLE DESCRIPTION: 
C       AD,AW,AC,AE,AU - THE DIAGONALS THAT MAKE UP THE SOLUTION MATRIX
C       RES - RHS OF THE SOLTUION MATRIX, NET FLOW CHANGE THAT IS SOLVED FOR 
C       Q(1:4,:) - STORES THE STEADY STATE FLOW THROUGH A CELL IN ORDER OF LEFT,RIGHT,BOTTON,TOP
C       Q(5,:) - STORES THE FINAL NET MASS GAIN/LOSS FOR A CELL
C       QRIGHT,QLEFT,QTOP,QBOT - FLOW THROUGH A CELL IN THE GIVEN DIRECTION
C       BOK - CONTROL VARIABLE USED TO HALT PROGRAM IF A FATAL ERROR IS ENCOUNTERED
C
C ---------------------------------------------------------------------
C
      USE TWOD_MODULE 
C
      IMPLICIT NONE 
      REAL(8), ALLOCATABLE :: RES(:) 
      REAL(8), ALLOCATABLE :: AD(:),AW(:),AC(:),AE(:),AU(:)
      REAL(8) :: QRIGHT,QLEFT,QTOP,QBOT
      INTEGER :: I,IX,IZ,LB
      LOGICAL :: BOK
C      
C     DEFINING VARIABLES 
      LB = NX*NZ
C
C     ALLOCATING VECTORS 
      ALLOCATE(AD(LB),AW(LB),AC(LB),AE(LB),AU(LB),RES(LB))
C
C     INITALIZING ITERATION VARIABLES
      AU(:)=0.0; AW(:)=0.0; AC(:)=0.0; AE(:)=0.0; AD(:)=0.0; RES(:)=0.0    
C     
C     SWEEPING GRID TO CREATE SOLTUION MATRIX DIAGONALS
      I = 0
      DO IZ = 1,NZ
        DO IX = 1,NX
          I = (IZ-1)*NX + IX
          AC(I)  =  TRX(IZ,IX-1)+TRX(IZ,IX)+TRZ(IZ-1,IX)+TRZ(IZ,IX)
          IF (AC(I) == 0.0) THEN
            WRITE(CVAR,2000) I
            CYCLE
          END IF
          AD(I)  = -TRZ(IZ-1,IX)
          AW(I)  = -TRX(IZ,IX-1)
          AE(I)  = -TRX(IZ,IX)
          AU(I)  = -TRZ(IZ,IX) 
          QLEFT  = -TRX(IZ,IX-1)*(FRAC_PS(IZ,IX) - FRAC_PS(IZ,IX-1))
          QRIGHT = -TRX(IZ,IX)*(FRAC_PS(IZ,IX+1) - FRAC_PS(IZ,IX))
          QBOT   = -TRZ(IZ-1,IX)*(FRAC_PS(IZ,IX) - FRAC_PS(IZ-1,IX))
          QTOP   = -TRZ(IZ,IX)*(FRAC_PS(IZ+1,IX) - FRAC_PS(IZ,IX))                                   
          RES(I) = (QLEFT - QRIGHT) + (QBOT - QTOP)
        END DO
      END DO   
C
C     SOLVING FOR STEADY STATE PRESSURE SOLUTION                                                                                                                                 
      CALL SOLVER(AD,AW,AC,AE,AU,RES)
C
C     UPDATING FRACTURE PRESSURE GRID WITH NEW PRESSURES
      DO IZ = 1,NZ
        DO IX = 1,NX
          ! CONVERTING PSEDUO-PRESSURE TO PRESSURE FOR GAS SIMULATIONS
          IF (IFLUID == 1) THEN
            CALL PS_TO_PR(FRAC_PR(IZ,IX),FRAC_PS(IZ,IX),BOK)
            IF (.NOT. BOK) GOTO 1000
          ELSE
            FRAC_PR(IZ,IX) = FRAC_PS(IZ,IX)
          END IF
        END DO
      END DO
      IF (.NOT. BOK) GOTO 1000
C
C     CALCULATING THE FINAL FLOWS FOR CELLS IN THE FRACTURE
      Q(:,:) = 0.0
      DO IZ = 1,NZ
        DO IX = 1,NX
          I = (IZ-1)*NX+IX
          Q(1,I) = -TRX(IZ,IX-1)*(FRAC_PS(IZ,IX)-FRAC_PS(IZ,IX-1))!LEFT
          Q(2,I) = -TRX(IZ,IX)*(FRAC_PS(IZ,IX+1) - FRAC_PS(IZ,IX))!RIGHT
          Q(3,I) = -TRZ(IZ-1,IX)*(FRAC_PS(IZ,IX)-FRAC_PS(IZ-1,IX))!BOTTOM
          Q(4,I) = -TRZ(IZ,IX)*(FRAC_PS(IZ+1,IX) - FRAC_PS(IZ,IX))!TOP
          Q(5,I) = ((Q(1,I)-Q(2,I))+(Q(3,I)-Q(4,I))) !NET RES
        END DO 
      END DO 
C 
      RETURN
C
 1000 BOK = .FALSE.
      RETURN
C
 2000 FORMAT(2X,'ERROR - DIAGONAL ELEMENT ',I0,' IS EQUAL TO 0')
C
      END SUBROUTINE
