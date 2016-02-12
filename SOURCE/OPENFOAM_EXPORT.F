      PROGRAM OPENFOAM_EXPORT
C
C     WRITTEN BY: MATTHEW STADELMAN
C     PROGRAM DESCRIPTON:
C
C ---------------------------------------------------------------------
C     VARIABLE DESCRIPTION:
C     BOK - LOGICAL FLOW CONTROL VARIABLE
C
C ----------------------------------------------------------------------
C   
      USE TWOD_MODULE 
C      
      IMPLICIT NONE
      LOGICAL :: BOK
C
C     INITIALIZING THE MODEL 
      BOK   = .TRUE.
      CALL INITIALIZE_EXPORT(BOK)
      IF (.NOT. BOK) GOTO 1000
C
C     OUTPUT BLOCK MESH FILE
      CALL OUTPUT_BlockMeshDict(BOK)
      IF (.NOT. BOK) GOTO 1000
C
      STOP
C
 1000 CALL BLANK
      CALL MESSAGE('     **** EXITING PROGRM ****')
C
      END PROGRAM
