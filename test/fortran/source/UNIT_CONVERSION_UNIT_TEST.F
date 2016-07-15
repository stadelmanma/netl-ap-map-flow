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
      USE UNIT_CONVERSION_MODULE
C
      IMPLICIT NONE
C
      PROSECUTOR = 'UNIT_CONVERSION_UNIT_TEST.F'
      DEFENDANT = 'UNIT_CONVERSION_MODULE.F'
      CALL INITIALIZE_TEST_MODULE
C
C     CALLING TEST ROUTINES
      CALL TEST_COVERT_VALUE
      CALL TEST_CALC_CONV_FACT
      CALL TEST_SET_TYPE_ID
      CALL TEST_CONV_TEMP
C
C
C
      PRINT *, 'PASSING? ',PASSING
      IF (.NOT. PASSING) STOP(1)
      END PROGRAM
C
C ----------------------------------------------------------------------
C     TESTING SUBROUTINES
C-----------------------------------------------------------------------
C
      SUBROUTINE TEST_COVERT_VALUE
        !
        ! WRITTEN BY: MATTHEW STADELMAN
        ! LAST MODIFIED: 2016/07/15
        !
        USE UNIT_TEST_MODULE
        USE UNIT_CONVERSION_MODULE
        IMPLICIT NONE
        REAL(8) :: TEST_VAL, CORR_VAL
        LOGICAL :: BOK
        !
        ! REGULAR CONVERSION
        TEST_VAL = 1.0D0
        CORR_VAL = 1000
        BOK = .TRUE.
        CALL CONVERT_VALUE('DIST','M','MM',TEST_VAL,BOK)
        CALL ASSERT_EQUALS(TEST_VAL, CORR_VAL, 'COVERT_VALUE')
        !
        ! TEMPERATURE CONVERSIONS
        TEST_VAL = 0.0D0
        CORR_VAL = 459.67D0
        BOK = .TRUE.
        CALL CONVERT_VALUE('TEMP','F','R',TEST_VAL,BOK)
        CALL ASSERT_EQUALS(TEST_VAL, CORR_VAL, 'COVERT_VALUE-TEMP')
        !
        ! HITTING FAILING CASES
        BOK = .TRUE.
        CALL CONVERT_VALUE('DIST','BAD UNIT','MM',TEST_VAL,BOK)
        CALL ASSERT_EQUALS(BOK, .FALSE., 'COVERT_VALUE-FAIL1')
        !
        BOK = .TRUE.
        CALL CONVERT_VALUE('TEMP','K','BAD UNIT',TEST_VAL,BOK)
        CALL ASSERT_EQUALS(BOK, .FALSE., 'COVERT_VALUE-FAIL2')
        !
        RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
      SUBROUTINE TEST_CALC_CONV_FACT
        !
        ! WRITTEN BY: MATTHEW STADELMAN
        ! LAST MODIFIED: 2016/07/15
        !
        USE UNIT_TEST_MODULE
        USE UNIT_CONVERSION_MODULE
        IMPLICIT NONE
        REAL(8) :: TEST_VAL, CORR_VAL
        LOGICAL :: BOK
        CHARACTER(20) :: UOUT
        !
        ! CONVERSION FACTOR TO SI
        TEST_VAL = 1.0D0
        CORR_VAL = 1.0D-3
        WRITE(UOUT,"(A)") 'SI'
        BOK = .TRUE.
        CALL CALC_CONV_FACT('DIST','MM',UOUT,TEST_VAL,BOK)
        CALL ASSERT_EQUALS(TEST_VAL, CORR_VAL, 'CALC_CONV_FACT-SI_VAL')
        CALL ASSERT_EQUALS(UOUT, 'M', 'CALC_CONV_FACT-SI_USTR')
        !
        ! REGULAR CONVERSION FACTOR
        TEST_VAL = 1.0D0
        CORR_VAL = 12.0D0
        BOK = .TRUE.
        CALL CALC_CONV_FACT('DIST','FT','IN',TEST_VAL,BOK)
        CALL ASSERT_EQUALS(TEST_VAL,CORR_VAL,'CALC_CONV_FACT-NONSI_VAL')
        !
        ! HITTING FAILING CASES
        BOK = .TRUE.
        CALL CALC_CONV_FACT('BAD TYPE','SI','SI',TEST_VAL,BOK)
        CALL ASSERT_EQUALS(BOK, .FALSE., 'CALC_CONV_FACT-TYPE_FAIL')
        !
        WRITE(UOUT,"(A)") 'SI'
        BOK = .TRUE.
        CALL CALC_CONV_FACT('DIST','BAD UNIT',UOUT,TEST_VAL,BOK)
        CALL ASSERT_EQUALS(BOK, .FALSE., 'CALC_CONV_FACT-SI_FAIL')
        !
        BOK = .TRUE.
        CALL CALC_CONV_FACT('DIST','BAD UNIT','IN',TEST_VAL,BOK)
        CALL ASSERT_EQUALS(BOK, .FALSE., 'CALC_CONV_FACT-NONSI_FAIL1')
        !
        BOK = .TRUE.
        CALL CALC_CONV_FACT('DIST','FT','BAD UNIT',TEST_VAL,BOK)
        CALL ASSERT_EQUALS(BOK, .FALSE., 'CALC_CONV_FACT-NONSI_FAIL2')
        !
        RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
      SUBROUTINE TEST_SET_TYPE_ID
        !
        ! WRITTEN BY: MATTHEW STADELMAN
        ! LAST MODIFIED: 2016/07/15
        !
        USE UNIT_TEST_MODULE
        USE UNIT_CONVERSION_MODULE
        IMPLICIT NONE
        INTEGER :: I, TID
        LOGICAL :: BOK
        CHARACTER(10) :: SI_CHK(100,2)
        CHARACTER(22) :: TEST1 = 'SET_TYPE_ID-INDEX_CHK-'
        CHARACTER(24) :: TEST2 = 'SET_TYPE_ID-SI_USTR_CHK-'
        !
        WRITE(SI_CHK(10,:),"(A)") 'DIST','M'
        WRITE(SI_CHK(20,:),"(A)") 'MASS','KG'
        WRITE(SI_CHK(30,:),"(A)") 'TEMP','K'
        WRITE(SI_CHK(40,:),"(A)") 'TIME','SEC'
        WRITE(SI_CHK(50,:),"(A)") 'DENS','KG/M^3'
        WRITE(SI_CHK(60,:),"(A)") 'FLOW','M^3/SEC'
        WRITE(SI_CHK(70,:),"(A)") 'PRES','PA'
        WRITE(SI_CHK(80,:),"(A)") 'VISC','PA*SEC'
        !
        ! CHECKING ALL OF THE IDS AND THEIR RESPECTIVE SI UNIT STRING
        DO I = 10,80,10
          CALL SET_TYPE_ID(SI_CHK(I,1), TID)
          CALL ASSERT_EQUALS(TID, I, TEST1//SI_CHK(I,1))
          CALL ASSERT_EQUALS(SI_UNITS(TID),SI_CHK(I,2),
     &                       TEST2//SI_CHK(I,1))
        END DO
        !
        ! TESTING THE FAILING CASE
        CALL SET_TYPE_ID('BAD TYPE', TID)
        CALL ASSERT_EQUALS(TID, -1, 'SET_TYPE_ID-INDEX_CHK-BAD-TYPE')
        !
        RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
      SUBROUTINE TEST_CONV_TEMP
        !
        ! WRITTEN BY: MATTHEW STADELMAN
        ! LAST MODIFIED: 2016/07/15
        !
        USE UNIT_TEST_MODULE
        USE UNIT_CONVERSION_MODULE
        IMPLICIT NONE
        REAL(8) :: TEST_VAL, CORR_VAL
        LOGICAL :: BOK
        !
        TEST_VAL = 0.0D0
        CORR_VAL = 459.67D0
        BOK = .TRUE.
        CALL CONV_TEMP('F','R',TEST_VAL,BOK)
        CALL ASSERT_EQUALS(TEST_VAL, CORR_VAL, 'CONV_TEMP: F->R')
        !
        TEST_VAL = 0.0D0
        CORR_VAL = -459.67D0
        BOK = .TRUE.
        CALL CONV_TEMP('R','F',TEST_VAL,BOK)
        CALL ASSERT_EQUALS(TEST_VAL, CORR_VAL, 'CONV_TEMP: R->F')
        !
        TEST_VAL = 0.0D0
        CORR_VAL = 273.15D0
        BOK = .TRUE.
        CALL CONV_TEMP('C','K',TEST_VAL,BOK)
        CALL ASSERT_EQUALS(TEST_VAL, CORR_VAL, 'CONV_TEMP: C->K')
        !
        TEST_VAL = 0.0D0
        CORR_VAL = -273.15D0
        BOK = .TRUE.
        CALL CONV_TEMP('K','C',TEST_VAL,BOK)
        CALL ASSERT_EQUALS(TEST_VAL, CORR_VAL, 'CONV_TEMP K->C')
        !
        ! HITTING FAILING CASES
        BOK = .TRUE.
        CALL CONV_TEMP('BAD UNIT','K',TEST_VAL,BOK)
        CALL ASSERT_EQUALS(BOK, .FALSE., 'CONV_TEMP-FAIL1')
        !
        BOK = .TRUE.
        CALL CONV_TEMP('K','BAD UNIT',TEST_VAL,BOK)
        CALL ASSERT_EQUALS(BOK, .FALSE., 'CONV_TEMP-FAIL2')
        !
      END SUBROUTINE
C
C ----------------------------------------------------------------------