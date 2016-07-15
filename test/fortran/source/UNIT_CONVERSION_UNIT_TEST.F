      PROGRAM STRING_MODULE_UNIT_TEST
C
C     WRITTEN BY: MATTHEW STADELMAN
C
C     PROGRAM DESCRIPTON: HANDLES UNIT TESTING OF THE UNIT CONVERSION MODULE.
C
C     DATE WRITTEN:  2016/07/14
C     LAST MODIFIED: 2016/07/15
C
C     SUBROUTINE CALLS:
C
C ----------------------------------------------------------------------
C     VARIABLE DESCRIPTION:
C
C ----------------------------------------------------------------------
C
      USE UNIT_TEST_MODULE
      USE STRING_MODULE
C
      IMPLICIT NONE
C
      PROSECUTOR = 'UNIT_CONVERSION_UNIT_TEST.F'
      DEFENDANT = 'UNIT_CONVERSION_MODULE.F'
      CALL INITIALIZE_TEST_MODULE
C
C     CALLING TEST ROUTINES
      !CALL TEST_SOMETHING
C
C
C
      IF (.NOT. PASSING) STOP(1)
      END PROGRAM
C
C ----------------------------------------------------------------------
C     TESTING SUBROUTINES
C-----------------------------------------------------------------------
C