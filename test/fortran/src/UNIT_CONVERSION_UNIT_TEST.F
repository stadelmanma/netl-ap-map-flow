      PROGRAM STRING_MODULE_UNIT_TEST
C
C     WRITTEN BY: MATTHEW STADELMAN
C
C     PROGRAM DESCRIPTON: HANDLES UNIT TESTING OF THE UNIT CONVERSION MODULE.
C
C     DATE WRITTEN:  2016/07/14
C     LAST MODIFIED: 2017/03/05
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
      CALL TEST_GET_CONV_FACT
      CALL TEST_CONV_DIST
      CALL TEST_CONV_MASS
      CALL TEST_CONV_TIME
      CALL TEST_CONV_DENS
      CALL TEST_CONV_RATE
      CALL TEST_CONV_PRES
      CALL TEST_CONV_VISC
C
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
      SUBROUTINE TEST_COVERT_VALUE
        !
        ! WRITTEN BY: MATTHEW STADELMAN
        ! LAST MODIFIED: 2016/07/15
        !
        USE UNIT_TEST_MODULE
        USE UNIT_CONVERSION_MODULE
        !
        IMPLICIT NONE
        REAL(8) :: TEST_VAL, CORR_VAL
        LOGICAL :: BOK
        CHARACTER(10) :: UNIT
        !
        CALL INIT_TEST
        !
        ! REGULAR CONVERSION
        TEST_VAL = 1.0D0
        CORR_VAL = 1000
        BOK = .TRUE.
        UNIT = 'MM'
        CALL CONVERT_VALUE('DIST','M',UNIT,TEST_VAL,BOK)
        CALL ASSERT_EQUALS(TEST_VAL, CORR_VAL, 'COVERT_VALUE')
        !
        ! HITTING FAILING CASE
        BOK = .TRUE.
        UNIT = 'MM'
        CALL CONVERT_VALUE('DIST','BAD UNIT',UNIT,TEST_VAL,BOK)
        CALL ASSERT_EQUALS(BOK, .FALSE., 'COVERT_VALUE-FAIL1')
        !
        CALL END_TEST('TEST_COVERT_VALUE')
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
        !
        IMPLICIT NONE
        REAL(8) :: TEST_VAL, CORR_VAL
        LOGICAL :: BOK
        CHARACTER(20) :: UOUT
        !
        CALL INIT_TEST
        !
        ! CONVERSION FACTOR TO SI
        TEST_VAL = 1.0D0
        CORR_VAL = 1.0D-3
        BOK = .TRUE.
        UOUT = 'SI'
        CALL CALC_CONV_FACT('DIST','MM',UOUT,TEST_VAL,BOK)
        CALL ASSERT_EQUALS(TEST_VAL, CORR_VAL, 'CALC_CONV_FACT-SI_VAL')
        CALL ASSERT_EQUALS(UOUT, 'M', 'CALC_CONV_FACT-SI_USTR')
        !
        ! REGULAR CONVERSION FACTOR
        TEST_VAL = 1.0D0
        CORR_VAL = 12.0D0
        BOK = .TRUE.
        UOUT = 'IN'
        CALL CALC_CONV_FACT('DIST','FT',UOUT,TEST_VAL,BOK)
        CALL ASSERT_EQUALS(TEST_VAL,CORR_VAL,'CALC_CONV_FACT-NONSI_VAL')
        !
        ! HITTING FAILING CASES
        BOK = .TRUE.
        UOUT = 'SI'
        CALL CALC_CONV_FACT('BAD TYPE','SI',UOUT,TEST_VAL,BOK)
        CALL ASSERT_EQUALS(BOK, .FALSE., 'CALC_CONV_FACT-TYPE_FAIL')
        !
        BOK = .TRUE.
        UOUT = 'SI'
        CALL CALC_CONV_FACT('DIST','BAD UNIT',UOUT,TEST_VAL,BOK)
        CALL ASSERT_EQUALS(BOK, .FALSE., 'CALC_CONV_FACT-SI_FAIL')
        !
        BOK = .TRUE.
        UOUT = 'IN'
        CALL CALC_CONV_FACT('DIST','BAD UNIT',UOUT,TEST_VAL,BOK)
        CALL ASSERT_EQUALS(BOK, .FALSE., 'CALC_CONV_FACT-NONSI_FAIL1')
        !
        BOK = .TRUE.
        UOUT = 'BAD UNIT'
        CALL CALC_CONV_FACT('DIST','FT',UOUT,TEST_VAL,BOK)
        CALL ASSERT_EQUALS(BOK, .FALSE., 'CALC_CONV_FACT-NONSI_FAIL2')
        !
        CALL END_TEST('TEST_CALC_CONV_FACT')
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
        !
        IMPLICIT NONE
        INTEGER :: I, TID
        CHARACTER(10) :: SI_CHK(100,2)
        CHARACTER(22) :: TEST1 = 'SET_TYPE_ID-INDEX_CHK-'
        CHARACTER(24) :: TEST2 = 'SET_TYPE_ID-SI_USTR_CHK-'
        !
        CALL INIT_TEST
        !
        WRITE(SI_CHK(10,:),"(A)") 'DIST','M'
        WRITE(SI_CHK(20,:),"(A)") 'MASS','KG'
        WRITE(SI_CHK(30,:),"(A)") 'TIME','SEC'
        WRITE(SI_CHK(40,:),"(A)") 'DENS','KG/M^3'
        WRITE(SI_CHK(50,:),"(A)") 'FLOW','M^3/SEC'
        WRITE(SI_CHK(60,:),"(A)") 'PRES','PA'
        WRITE(SI_CHK(70,:),"(A)") 'VISC','PA*SEC'
        !
        ! CHECKING ALL OF THE IDS AND THEIR RESPECTIVE SI UNIT STRING
        DO I = 10,70,10
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
        CALL END_TEST('TEST_SET_TYPE_ID')
        !
        RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
      SUBROUTINE TEST_GET_CONV_FACT
        !
        ! WRITTEN BY: MATTHEW STADELMAN
        ! LAST MODIFIED: 2016/07/15
        !
        USE UNIT_TEST_MODULE
        USE UNIT_CONVERSION_MODULE
        !
        IMPLICIT NONE
        REAL(8) :: FACT
        INTEGER :: I
        CHARACTER(11) :: SI_CHK(100)
        CHARACTER(23) :: TEST1 = 'GET_CONV_FACT-FACT_CHK-'
        !
        CALL INIT_TEST
        !
        WRITE(SI_CHK(10),"(A)") 'M'
        WRITE(SI_CHK(20),"(A)") 'KG'
        WRITE(SI_CHK(30),"(A)") 'SEC'
        WRITE(SI_CHK(40),"(A)") 'KG/M^3'
        WRITE(SI_CHK(50),"(A)") 'M^3/SEC'
        WRITE(SI_CHK(60),"(A)") 'PA'
        WRITE(SI_CHK(70),"(A)") 'PA*SEC'
        WRITE(SI_CHK(80),"(A)") 'BAD TYPE ID'
        !
        ! CHECKING ALL OF THE IDS AND THEIR RESPECTIVE CONVERSION FACTOR
        DO I = 10,80,10
          CALL GET_CONV_FACT(I, SI_CHK(I), FACT)
          IF (I == 80) THEN
            CALL ASSERT_EQUALS(FACT, -1.0D0, TEST1//'FAIL-'//SI_CHK(I))
          ELSE
            CALL ASSERT_EQUALS(FACT, 1.0D0, TEST1//SI_CHK(I))
          END IF
        END DO
        !
        CALL END_TEST('TEST_GET_CONV_FACT')
        !
        RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
      SUBROUTINE TEST_CONV_DIST
        !
        ! WRITTEN BY: MATTHEW STADELMAN
        ! LAST MODIFIED: 2016/07/15
        !
        USE UNIT_TEST_MODULE
        USE UNIT_CONVERSION_MODULE
        !
        IMPLICIT NONE
        REAL(8) :: FACT
        INTEGER :: I
        REAL(8) ::        VALS(8)
        CHARACTER(11) :: UNITS(8)
        CHARACTER(20) :: TEST = 'CONV_DIST-FACT_CHK-'
        VOX_MET = 20.0D-6
        !
        CALL INIT_TEST
        !
        WRITE(UNITS(1),"(A)") 'MICR'; VALS(1)=1.0E-6
        WRITE(UNITS(2),"(A)") 'MM';   VALS(2)=1.0D-3
        WRITE(UNITS(3),"(A)") 'CM';   VALS(3)=1.0D-2
        WRITE(UNITS(4),"(A)") 'IN';   VALS(4)=2.540D-2
        WRITE(UNITS(5),"(A)") 'FT';   VALS(5)=3.0480D-1
        WRITE(UNITS(6),"(A)") 'FEET'; VALS(6)=3.0480D-1
        WRITE(UNITS(7),"(A)") 'VOX';  VALS(7)=20.0D-6
        WRITE(UNITS(8),"(A)") 'M';    VALS(8)=1.0D0
        !
        ! CHECKING ALL OF THE UNITS AND THEIR RESPECTIVE TO SI CONVERSION
        DO I = 1,SIZE(UNITS)
          CALL CONV_DIST(UNITS(I), FACT)
          CALL ASSERT_EQUALS(FACT, VALS(I), TEST//UNITS(I))
        END DO
        !
        ! HITTING THE FAILING CASE
        CALL CONV_DIST('BAD UNIT', FACT)
        CALL ASSERT_EQUALS(FACT, -1.0D0, TEST//'BAD UNIT')
        !
        CALL END_TEST('TEST_CONV_DIST')
        !
        RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
      SUBROUTINE TEST_CONV_MASS
        !
        ! WRITTEN BY: MATTHEW STADELMAN
        ! LAST MODIFIED: 2016/07/15
        !
        USE UNIT_TEST_MODULE
        USE UNIT_CONVERSION_MODULE
        !
        IMPLICIT NONE
        REAL(8) :: FACT
        INTEGER :: I
        REAL(8) ::        VALS(4)
        CHARACTER(11) :: UNITS(4)
        CHARACTER(20) :: TEST = 'CONV_MASS-FACT_CHK-'
        !
        CALL INIT_TEST
        !
        WRITE(UNITS(1),"(A)") 'SLUG'; VALS(1)=1.459390D1
        WRITE(UNITS(2),"(A)") 'LB';   VALS(2)=4.53592370D-1
        WRITE(UNITS(3),"(A)") 'KG';   VALS(3)=1.0D0
        WRITE(UNITS(4),"(A)") 'G';    VALS(4)=1.0D-3
        !
        ! CHECKING ALL OF THE UNITS AND THEIR RESPECTIVE TO SI CONVERSION
        DO I = 1,SIZE(UNITS)
          CALL CONV_MASS(UNITS(I), FACT)
          CALL ASSERT_EQUALS(FACT, VALS(I), TEST//UNITS(I))
        END DO
        !
        ! HITTING THE FAILING CASE
        CALL CONV_MASS('BAD UNIT', FACT)
        CALL ASSERT_EQUALS(FACT, -1.0D0, TEST//'BAD UNIT')
        !
        CALL END_TEST('TEST_CONV_MASS')
        !
        RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
      SUBROUTINE TEST_CONV_TIME
        !
        ! WRITTEN BY: MATTHEW STADELMAN
        ! LAST MODIFIED: 2016/07/15
        !
        USE UNIT_TEST_MODULE
        USE UNIT_CONVERSION_MODULE
        !
        IMPLICIT NONE
        REAL(8) :: FACT
        INTEGER :: I
        REAL(8) ::        VALS(5)
        CHARACTER(11) :: UNITS(5)
        CHARACTER(20) :: TEST = 'CONV_TIME-FACT_CHK-'
        !
        CALL INIT_TEST
        !
        WRITE(UNITS(1),"(A)") 'DAY';  VALS(1)=8.6400D4
        WRITE(UNITS(2),"(A)") 'HOUR'; VALS(2)=3.600D3
        WRITE(UNITS(3),"(A)") 'HR';   VALS(3)=3.600D3
        WRITE(UNITS(4),"(A)") 'MIN';  VALS(4)=6.0D1
        WRITE(UNITS(5),"(A)") 'SEC';  VALS(5)=1.0D0
        !
        ! CHECKING ALL OF THE UNITS AND THEIR RESPECTIVE TO SI CONVERSION
        DO I = 1,SIZE(UNITS)
          CALL CONV_TIME(UNITS(I), FACT)
          CALL ASSERT_EQUALS(FACT, VALS(I), TEST//UNITS(I))
        END DO
        !
        ! HITTING THE FAILING CASE
        CALL CONV_TIME('BAD UNIT', FACT)
        CALL ASSERT_EQUALS(FACT, -1.0D0, TEST//'BAD UNIT')
        !
        CALL END_TEST('TEST_CONV_TIME')
        !
        RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
      SUBROUTINE TEST_CONV_DENS
        !
        ! WRITTEN BY: MATTHEW STADELMAN
        ! LAST MODIFIED: 2016/07/15
        !
        USE UNIT_TEST_MODULE
        USE UNIT_CONVERSION_MODULE
        !
        IMPLICIT NONE
        REAL(8) :: FACT
        INTEGER :: I
        REAL(8) ::        VALS(3)
        CHARACTER(11) :: UNITS(3)
        CHARACTER(20) :: TEST = 'CONV_DENS-FACT_CHK-'
        !
        CALL INIT_TEST
        !
        WRITE(UNITS(1),"(A)") 'G/CM^3';  VALS(1)=1.0D3
        WRITE(UNITS(2),"(A)") 'LB/FT^3'; VALS(2)=LBS_KG/FT_MET**3
        WRITE(UNITS(3),"(A)") 'KG/M^3';  VALS(3)=1.0D0
        !
        ! CHECKING ALL OF THE UNITS AND THEIR RESPECTIVE TO SI CONVERSION
        DO I = 1,SIZE(UNITS)
          CALL CONV_DENS(UNITS(I), FACT)
          CALL ASSERT_EQUALS(FACT, VALS(I), TEST//UNITS(I))
        END DO
        !
        ! HITTING THE FAILING CASE
        CALL CONV_DENS('BAD/UNIT', FACT)
        CALL ASSERT_EQUALS(FACT, 1.0D0, TEST//'BAD UNIT')
        !
        CALL END_TEST('TEST_CONV_DENS')
        !
        RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
      SUBROUTINE TEST_CONV_RATE
        !
        ! WRITTEN BY: MATTHEW STADELMAN
        ! LAST MODIFIED: 2016/07/15
        !
        USE UNIT_TEST_MODULE
        USE UNIT_CONVERSION_MODULE
        !
        IMPLICIT NONE
        REAL(8) :: FACT
        INTEGER :: I
        REAL(8) ::        VALS(2)
        CHARACTER(11) :: UNITS(2)
        CHARACTER(20) :: TEST = 'CONV_RATE-FACT_CHK-'
        !
        CALL INIT_TEST
        !
        WRITE(UNITS(1),"(A)") 'ML/SEC';  VALS(1)=1.0D-6
        WRITE(UNITS(2),"(A)") 'M^3/SEC'; VALS(2)=1.0D0
        !
        ! CHECKING ALL OF THE UNITS AND THEIR RESPECTIVE TO SI CONVERSION
        DO I = 1,SIZE(UNITS)
          CALL CONV_RATE(UNITS(I), FACT)
          CALL ASSERT_EQUALS(FACT, VALS(I), TEST//UNITS(I))
        END DO
        !
        ! HITTING THE FAILING CASE
        CALL CONV_RATE('BAD/UNIT', FACT)
        CALL ASSERT_EQUALS(FACT, 1.0D0, TEST//'BAD UNIT')
        !
        CALL END_TEST('TEST_CONV_RATE')
        !
        RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
      SUBROUTINE TEST_CONV_PRES
        !
        ! WRITTEN BY: MATTHEW STADELMAN
        ! LAST MODIFIED: 2016/07/15
        !
        USE UNIT_TEST_MODULE
        USE UNIT_CONVERSION_MODULE
        !
        IMPLICIT NONE
        REAL(8) :: FACT
        INTEGER :: I
        REAL(8) ::        VALS(5)
        CHARACTER(11) :: UNITS(5)
        CHARACTER(20) :: TEST = 'CONV_PRES-FACT_CHK-'
        !
        CALL INIT_TEST
        !
        WRITE(UNITS(1),"(A)") 'PSI'; VALS(1)=6894.757293178D0
        WRITE(UNITS(2),"(A)") 'BAR'; VALS(2)=1.0D5
        WRITE(UNITS(3),"(A)") 'ATM'; VALS(3)=101325.0D0
        WRITE(UNITS(4),"(A)") 'KPA'; VALS(4)=1.0D3
        WRITE(UNITS(5),"(A)") 'PA';  VALS(5)=1.0D0
        !
        ! CHECKING ALL OF THE UNITS AND THEIR RESPECTIVE TO SI CONVERSION
        DO I = 1,SIZE(UNITS)
          CALL CONV_PRES(UNITS(I), FACT)
          CALL ASSERT_EQUALS(FACT, VALS(I), TEST//UNITS(I))
        END DO
        !
        ! HITTING THE FAILING CASE
        CALL CONV_PRES('BAD UNIT', FACT)
        CALL ASSERT_EQUALS(FACT, -1.0D0, TEST//'BAD UNIT')
        !
        CALL END_TEST('TEST_CONV_PRES')
        !
        RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
      SUBROUTINE TEST_CONV_VISC
        !
        ! WRITTEN BY: MATTHEW STADELMAN
        ! LAST MODIFIED: 2016/07/15
        !
        USE UNIT_TEST_MODULE
        USE UNIT_CONVERSION_MODULE
        !
        IMPLICIT NONE
        REAL(8) :: FACT
        INTEGER :: I
        REAL(8) ::        VALS(3)
        CHARACTER(11) :: UNITS(3)
        CHARACTER(20) :: TEST = 'CONV_VISC-FACT_CHK-'
        !
        CALL INIT_TEST
        !
        WRITE(UNITS(1),"(A)") 'CP';    VALS(1)=1.0D-3
        WRITE(UNITS(2),"(A)") 'CENTI'; VALS(2)=1.0D-3
        WRITE(UNITS(3),"(A)") 'PA*SEC';   VALS(3)=1.0D0
        !
        ! CHECKING ALL OF THE UNITS AND THEIR RESPECTIVE TO SI CONVERSION
        DO I = 1,SIZE(UNITS)
          CALL CONV_VISC(UNITS(I), FACT)
          CALL ASSERT_EQUALS(FACT, VALS(I), TEST//UNITS(I))
        END DO
        !
        ! HITTING THE FAILING CASE
        CALL CONV_VISC('BAD UNIT', FACT)
        CALL ASSERT_EQUALS(FACT, -1.0D0, TEST//'BAD UNIT')
        !
        CALL END_TEST('TEST_CONV_VISC')
        !
        RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
