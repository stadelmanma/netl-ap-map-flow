      PROGRAM STRING_MODULE_UNIT_TEST
C
C     WRITTEN BY: MATTHEW STADELMAN
C
C     PROGRAM DESCRIPTON: HANDLES UNIT TESTING OF THE STRING MODULE.
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
      PROSECUTOR = 'STRING_MODULE_UNIT_TEST.F'
      DEFENDANT = 'STRING_MODULE.F'
      CALL INITIALIZE_TEST_MODULE
C
C     CALLING TEST ROUTINES
      CALL TEST_UPPER_CASE
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
      SUBROUTINE TEST_UPPER_CASE
        !
        ! WRITTEN BY: MATTHEW STADELMAN
        ! LAST MODIFIED: 2016/07/14
        !
        USE UNIT_TEST_MODULE
        USE STRING_MODULE
        IMPLICIT NONE
        CHARACTER(80) :: ORIG_STR, NEW_STR
        !
        ORIG_STR = 'all lowercase'
        CALL UPPER_CASE(ORIG_STR, NEW_STR)
        !
        CALL ASSERT_EQUALS(ORIG_STR, NEW_STR, 'UPPER_CASE')
        !
        RETURN
      END SUBROUTINE