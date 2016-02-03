      SUBROUTINE FRAC_FLOW(Q,N,BOK)
C 
C     WRITTEN BY: MATTHEW STADELMAN
C     PROGRAM DESCRIPTION: SOLVES FOR THE FLOW WHEN THE WELLBORE BISECTS 
C           A FRACTURE IN THE RESERVOIR. ASSUMED STEADY STATE FLOW. 
C
C ---------------------------------------------------------------------
C     VARIABLE DESCRIPTION: 
C     ITPR - VECTOR THAT STORES ITERATION PRESSURE
C     RZ - VECTOR THAT STORES THE Z VALUE FOR THE RESERVOIR 
C     RES - ARRAY THAT STORES THE RESIDUAL VALUES FOR EACH BLOCK
C     MAX_RES - HIGHEST RESIDUAL FOR THE CURRENT ITERATION STEP
C     REF - RECORDS THE HIGHEST FLOW RATE FOR THE RESERVIOR
C     QOUT,QIN - FLOW OUT OF A CELL, FLOW INTO A CELL RESPECTIVELY
C     QX - FLOW IN THE X-DIR FOR A CELL 
C     QZ - FLOW IN THE Z-DIR FOR A GIVEN CELL 
C     AD,AW,AC,AE,AU - DIAGONAL VECTORS USED TO SOLVE FOR DPS
C     IX,IZ - X ITERATOR AND Z ITERATOR RESPECTIVELY 
C     I - IS THE COLLAPSED ARRAY INDEX 
C     LB - INDEX OF LAST BLOCK
C     TT - CURRENT TIME ITERATION STEP   
C ---------------------------------------------------------------------
C
      USE TWOD_MODULE 
C
      IMPLICIT NONE 
      INTEGER :: I,N,IX,IZ,LB
      REAL(8) :: QRIGHT,QLEFT,QTOP,QBOT
      REAL(8) ::  Q(N,*)
      REAL(8), ALLOCATABLE :: RES(:) 
      REAL(8), ALLOCATABLE :: AD(:),AW(:),AC(:),AE(:),AU(:)
      LOGICAL :: BOK
C      
C     SETTING UP VARIABLES 
      LB = NX*NZ
C
C     ALLOCATING VECTORS 
      ALLOCATE(AD(LB),AW(LB),AC(LB),AE(LB),AU(LB),RES(LB))
C
C     INITALIZING ITERATION VARIABLES
      AU(:)=0.0; AW(:)=0.0; AC(:)=0.0; AE(:)=0.0; AD(:)=0.0; RES(:)=0.0    
C     
C     SWEEPING GRID
      I = 0
      DO IZ = 1,NZ
        DO IX = 1,NX
          I = (IZ-1)*NX + IX
          AD(I)  = -TRZ(IZ-1,IX)
          AW(I)  = -TRX(IZ,IX-1)
          AC(I)  =  TRX(IZ,IX-1)+TRX(IZ,IX)+TRZ(IZ-1,IX)+TRZ(IZ,IX)
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
      CALL SOLVER(AD,AW,AC,AE,AU,RES)
      DO IZ = 1,NZ
        DO IX = 1,NX
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
C     CALCULATING THE FINAL FLOWS FOR THE FRACTURE
      Q(1:N,1:LB) = 0.0
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
      END SUBROUTINE
