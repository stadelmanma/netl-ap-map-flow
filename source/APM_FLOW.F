C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
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
C       Q(1:4,:) - STORES THE STEADY STATE FLOW THROUGH A CELL IN ORDER OF LEFT,RIGHT,BOTTON,TOP
C       Q(5,:) - STORES THE FINAL NET MASS GAIN/LOSS FOR A CELL
C       BOK - CONTROL VARIABLE USED TO HALT PROGRAM IF A FATAL ERROR IS ENCOUNTERED
C
C ---------------------------------------------------------------------
C
      USE APM_MODULE
      USE PVT_MODULE, ONLY : PS_TO_PR
C
      IMPLICIT NONE
      INTEGER :: I,IX,IZ
      LOGICAL :: BOK
C
C     SOLVING FOR STEADY STATE FLOW PRESSURE DISTRIBUTION
      CALL SOLVER
C
C     HANDLING EACH OUTFLOW SIDE CASE TO SET BOUNDARY PRESSURES
      IF (INDEX(OUTLET_SIDE,'LEFT') > 0) THEN
        FRAC_PS(:,0) = OUTPSB !EXTRA LEFT COUMN
        FRAC_PS(:,NX+1) = INLPSB !EXTRA RIGHT COLUMN
        FRAC_PS(0,:) = INLPSB !EXTRA BOTTOM ROW
        FRAC_PS(NZ+1,:) = INLPSB !EXTRA TOP ROW
      ELSE IF (INDEX(OUTLET_SIDE,'RIGHT') > 0) THEN
        FRAC_PS(:,0) = INLPSB !EXTRA LEFT COUMN
        FRAC_PS(:,NX+1) = OUTPSB !EXTRA RIGHT COLUMN
        FRAC_PS(0,:) = INLPSB !EXTRA BOTTOM ROW
        FRAC_PS(NZ+1,:) = INLPSB !EXTRA TOP ROW
      ELSE IF (INDEX(OUTLET_SIDE,'TOP') > 0) THEN
        FRAC_PS(:,0) = INLPSB !EXTRA LEFT COUMN
        FRAC_PS(:,NX+1) = INLPSB !EXTRA RIGHT COLUMN
        FRAC_PS(0,:) = INLPSB !EXTRA BOTTOM ROW
        FRAC_PS(NZ+1,:) = OUTPSB !EXTRA TOP ROW
      ELSE IF (INDEX(OUTLET_SIDE,'BOTTOM') > 0) THEN
        FRAC_PS(:,0) = INLPSB !EXTRA LEFT COUMN
        FRAC_PS(:,NX+1) = INLPSB !EXTRA RIGHT COLUMN
        FRAC_PS(0,:) = OUTPSB !EXTRA BOTTOM ROW
        FRAC_PS(NZ+1,:) = INLPSB !EXTRA TOP ROW
      END IF
C
      CALL PS_TO_PR(OUTPB,OUTPSB,BOK)
      CALL PS_TO_PR(INLPB,INLPSB,BOK)
C
C     UPDATING FRACTURE INTERIOR GRID WITH NEW PRESSURES
      DO IZ = 1,NZ
        DO IX = 1,NX
          CALL PS_TO_PR(FRAC_PR(IZ,IX),FRAC_PS(IZ,IX),BOK)
        END DO
      END DO
      IF (.NOT. BOK) GOTO 1000
C
C     CALCULATING THE FINAL FLOW RATES FOR CELLS IN THE FRACTURE
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
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C