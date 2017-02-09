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
        USE IO_MODULE
        PROSECUTOR = 'IO_MODULE_UNIT_TEST.F'
        DEFENDANT = 'IO_MODULE.F'
        CALL INITIALIZE_TEST_MODULE
C
C     CALLING TEST ROUTINES
      CALL TEST_ERROR_ROUTINES
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
      SUBROUTINE TEST_ERROR_ROUTINES
        !
        ! WRITTEN BY: MATTHEW STADELMAN
        ! LAST MODIFIED: 2016/07/14
        !
        USE IO_MODULE, ONLY : APM_IOUT => IOUT, ERROR_WHERE,
     &                        INSUFFICIENT_ERROR, FIELD_ERROR
        USE UNIT_TEST_MODULE
        IMPLICIT NONE
        !
        CALL INIT_TEST
        APM_IOUT = 6
        !
        CALL ERROR_WHERE('TEST RECORD')
        CALL INSUFFICIENT_ERROR('TEST RECORD')
        CALL FIELD_ERROR('TEST RECORD', -1)
        !
        CALL END_TEST('TEST_ERROR_ROUTINES')
        !
        RETURN
      END SUBROUTINE
