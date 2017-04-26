C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE QUIT
C
C     WRITTEN BY: MATTHEW STADELMAN
C
C     DATE WRITTEN:  2015/12/09
C     LAST MODIFIED: 2016/10/27
C
C     PROGRAM DESCRIPTION: QUITS THE PROGRAM PRINTING THE LINE NUMBER TO SCREEN
C         USED WHEN DEBUGGING CODE OR TESTING NEW FEATURES
C
C     SUBROUTINE CALLS: EXECUTE_COMMAND_LINE
C
C ----------------------------------------------------------------------
C     VARIABLE DESCRIPTION:
C       CMD - COMMAND USED TO PRINT FILE AND LINE NUMBER TO THE SCREEN
C
C ----------------------------------------------------------------------
C
      IMPLICIT NONE
      CHARACTER(120) :: CMD
C
C     SETTING UP COMMAND
      WRITE(CMD,2000) '$(git rev-parse --show-toplevel)/source/'
C
C     PRINTING MESSAGE AND USING GREP TO SHOW WHERE IT WAS CALLED
      WRITE(*,"(1X)")
      WRITE(*,*)' *** ALERT: QUIT SUBROUTINE CALLED ***'
      CALL EXECUTE_COMMAND_LINE(CMD)
      STOP(1)
C
 2000 FORMAT('grep -rn -e "[[:space:]]CALL QUIT" "',A,'"')
C
      RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------