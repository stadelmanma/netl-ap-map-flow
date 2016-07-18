      PROGRAM APM_SUBROUTINES_UNIT_TEST
C
C     WRITTEN BY: MATTHEW STADELMAN
C
C     PROGRAM DESCRIPTON: HANDLES UNIT TESTING OF ERROR HANDLING
C         SUBROUTINES NOT COVERED DURING INTEGRATION TESTS AS WELL AS
C         CHECKING THE NUMERIC VALUE OF OTHER KEY ROUTINES.
C
C     DATE WRITTEN:  2016/07/14
C     LAST MODIFIED: 2016/07/18
C
C     SUBROUTINE CALLS:
C
C ----------------------------------------------------------------------
C     VARIABLE DESCRIPTION:
C
C ----------------------------------------------------------------------
C
      USE UNIT_TEST_MODULE
      USE APM_MODULE
      PROSECUTOR = 'APM_SUBROUTINES_UNIT_TEST.F'
      DEFENDANT = 'APM_SUBROUTINES.F'
      CALL INITIALIZE_TEST_MODULE
C
C     CALLING TEST ROUTINES
      !
C
C
      PRINT *, 'ALL_PASS? ',ALL_PASS
      IF (.NOT. ALL_PASS) STOP(1)
      END PROGRAM
C
C ----------------------------------------------------------------------
C     TESTING SUBROUTINES
C-----------------------------------------------------------------------
C