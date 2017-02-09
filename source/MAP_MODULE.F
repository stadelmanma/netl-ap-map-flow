      MODULE MAP_MODULE
C
C     WRITTEN BY: MATTHEW STADELMAN
C     FILE DESCRIPTION: STORES DATA MAP RELATED VARIABLES AND SUBROUTINES.
C
C     LAST MODIFIED: 2017/02/08
C ----------------------------------------------------------------------
C               ---- VARIABLE DESCRIPTIONS ----
C
C ----------------------------------------------------------------------
C
      CONTAINS
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE READ_DATA_MAP(DATA_MAP, IUNIT, MAXDIM, BOK)
C
C     WRITTEN BY: MATTHEW STADELMAN
C     LAST MODIFIED: 2017/02/06
C
C     READS A 2-D DATA MAP FROM A FILE. IF THE DATA_MAP HAS ALREADY
C     BEEN ALLOCATED IT WILL BE DEALLOCATED AND RESIZED
C
      USE IO_MODULE, ONLY : BLANK, MESSAGE, FIELD_ERROR
      USE STRING_MODULE, ONLY : LNPROC
      !
      IMPLICIT NONE
      REAL(8), ALLOCATABLE, INTENT(OUT) :: DATA_MAP(:, :)
      INTEGER, INTENT(IN) :: IUNIT, MAXDIM
      LOGICAL, INTENT(INOUT) :: BOK
      !
      REAL(8), ALLOCATABLE :: TEMP(:, :)
      INTEGER :: NX, NZ, IFLD, NFLD, LFLD(MAXDIM)
      CHARACTER(80) :: CVAR, CFLD(MAXDIM)
      CHARACTER(80 * MAXDIM) :: LINE
C
      ALLOCATE(TEMP(MAXDIM, MAXDIM))
C
C     READING THE DATA MAP FILE INTO A TEMPORARY ARRAY
      NX = 0
      NZ = 0
      NFLD = 0
      DO
        NX = NFLD
        CALL LNPROC(IUNIT, MAXDIM, LEN(LINE), LINE, CFLD, LFLD, NFLD)
        IF (NFLD == 0) EXIT
C
        NZ = NZ + 1
        IF (NZ > MAXDIM) GOTO 931
        DO IFLD = 1, NFLD
          IF (NFLD > MAXDIM) GOTO 930
          READ(CFLD(IFLD), *, ERR=910) TEMP(NZ, IFLD)
        END DO
      END DO
C
C     POPULATING THE FINAL DATA MAP WITH EXACT DIMENSIONS
      IF (ALLOCATED(DATA_MAP)) DEALLOCATE(DATA_MAP)
      ALLOCATE(DATA_MAP(NZ, NX))
      DATA_MAP(:,:) = TEMP(1:NZ, 1:NX)
C
      DEALLOCATE(TEMP)
      RETURN
C
C     ERROR HANDLING
C
  910 CALL FIELD_ERROR("APERTURE MAP", IFLD)
      CALL MESSAGE("LINE - " // LINE(1:70) // "...")
      GOTO 1000
C
  930 WRITE(CVAR, 2050) 'HORIZONTAL', MAXDIM
      CALL MESSAGE(CVAR)
      GOTO 1000
C
  931 WRITE(CVAR,2050) 'VERTICAL', MAXDIM
      CALL MESSAGE(CVAR)
      GOTO 1000
C
 1000 BOK = .FALSE.
      RETURN
C
 2050 FORMAT(1X, 'ERROR - MAXIMUM NUMBER OF ', A, ' CELLS IS ', I0)
C
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE CREATE_POINT_MAP(DATA_MAP, POINT_MAP)
C
C     WRITTEN BY: MATTHEW STADELMAN
C     LAST MODIFIED: 2017/02/07
C
C     TAKES A 2-D "CELL VALUE" DATA MAP AND CALCULATES AVERAGE CORNER
C     POINT VALUES BASED ON THE FOUR NEIGHBORING CELL VALUES. THE
C     POINT_MAP ARRAY HAS TO ALREADY BE ALLOCATED TO THE PROPER SIZE OR
C     LARGER THAN THE DATA_MAP. 1 = BLC, 2 = BRC, 3 = TRC, 4 = TLC
C
C        X--------------X--------------X
C        | 4          3 | 4          3 |
C        |              |              |
C        |      1,0     |      1,1     |
C        |              |              |
C        | 1          2 | 1          2 |
C        X--------------X--------------X
C        | 4          3 | 4          3 |
C        |              |              |
C        |      0,0     |      0,1     |
C        |              |              |
C        | 1          2 | 1          2 |
C        X--------------X--------------X
C
      IMPLICIT NONE
      REAL(8), INTENT(IN) :: DATA_MAP(:, :)
      REAL(8), INTENT(OUT) :: POINT_MAP(:, :, :)
      !
      INTEGER :: NX, NZ, IX, IZ
      NX = SIZE(DATA_MAP, DIM=2)
      NZ = SIZE(DATA_MAP, DIM=1)
C
C     CALCULATING AVERAGE CORNER VALUES OF CELLS
C
      ! HANDLING CORNERS OF MAP SINCE THEY DON'T HAVE AN NEIGHBORS
      POINT_MAP(1, 1, 1)   = DATA_MAP(1, 1)
      POINT_MAP(1, NX, 2)  = DATA_MAP(1, NX)
      POINT_MAP(NZ, NX, 3) = DATA_MAP(NZ, NX)
      POINT_MAP(NZ, 1, 4)  = DATA_MAP(NZ, 1)
      !
      ! CALCULATING CORNER VALUES OF MAP INTERIOR
      DO IX = 1, NX - 1
        DO IZ = 1, NZ - 1
          POINT_MAP(IZ,IX,3) = DATA_MAP(IZ,IX)
          POINT_MAP(IZ,IX,3) = POINT_MAP(IZ,IX,3) + DATA_MAP(IZ+1,IX)   !ABOVE
          POINT_MAP(IZ,IX,3) = POINT_MAP(IZ,IX,3) + DATA_MAP(IZ,IX+1)   !RIGHT
          POINT_MAP(IZ,IX,3) = POINT_MAP(IZ,IX,3) + DATA_MAP(IZ+1,IX+1) !CORNER
          POINT_MAP(IZ,IX,3) = POINT_MAP(IZ,IX,3)/4.0 !TRC OF CELL
          POINT_MAP(IZ+1,IX+1,1) = POINT_MAP(IZ,IX,3) !BLC OF CORNER CELL
          POINT_MAP(IZ+1,IX,2) = POINT_MAP(IZ,IX,3)   !BRC OF ABOVE CELL
          POINT_MAP(IZ,IX+1,4) = POINT_MAP(IZ,IX,3)   !TLC OF RIGHT CELL
        END DO
      END DO
      !
      ! HANDLING LEFT AND RIGHT EDGES OF MAP
      DO IZ = 1, NZ - 1
          ! CALCULATING BOTTOM LEFT AND TOP LEFT CORNER OF LEFT EDGE
          POINT_MAP(IZ,1,4) = DATA_MAP(IZ,1)
          POINT_MAP(IZ,1,4) = POINT_MAP(IZ,1,4) + DATA_MAP(IZ+1,1) !ABOVE
          POINT_MAP(IZ,1,4) = POINT_MAP(IZ,1,4)/2.0 !TLC OF CELL
          POINT_MAP(IZ+1,1,1) = POINT_MAP(IZ,1,4)   !BLC OF ABOVE CELL
          !
          ! CALCULATING BOTTOM RIGHT AND TOP RIGHT CORNER OF RIGHT EDGE
          POINT_MAP(IZ,NX,3) = DATA_MAP(IZ,NX)
          POINT_MAP(IZ,NX,3) = POINT_MAP(IZ,NX,3) + DATA_MAP(IZ+1,NX) !ABOVE
          POINT_MAP(IZ,NX,3) = POINT_MAP(IZ,NX,3)/2.0 !TRC OF CELL
          POINT_MAP(IZ+1,NX,2) = POINT_MAP(IZ,NX,3)   !BRC OF ABOVE CELL
      END DO
      !
      ! HANDLING TOP AND BOTTOM EDGES OF MAP
      DO IX = 1, NX - 1
          ! CALCULATING BOTTOM LEFT AND BOTTOM RIGHT CORNER OF LOWER EDGE
          POINT_MAP(1,IX,2) = DATA_MAP(1,IX)
          POINT_MAP(1,IX,2) = POINT_MAP(1,IX,2) + DATA_MAP(1,IX+1) !RIGHT
          POINT_MAP(1,IX,2) = POINT_MAP(1,IX,2)/2.0 !BRC OF CELL
          POINT_MAP(1,IX+1,1) = POINT_MAP(1,IX,2)   !BLC OF RIGHT CELL
          !
          ! CALCULATING TOP LEFT AND TOP RIGHT CORNER OF UPPER EDGE
          POINT_MAP(NZ,IX,3) = DATA_MAP(NZ,IX)
          POINT_MAP(NZ,IX,3) = POINT_MAP(NZ,IX,3) + DATA_MAP(NZ,IX+1) !RIGHT
          POINT_MAP(NZ,IX,3) = POINT_MAP(NZ,IX,3)/2.0 !TRC OF CELL
          POINT_MAP(NZ,IX+1,4) = POINT_MAP(NZ,IX,3)   !TLC OF RIGHT CELL
      END DO
C
      RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE MAP_STATS(DATA_MAP, STAT_KEYS, STAT_VALS)
C
C     WRITTEN BY: MATTHEW STADELMAN
C
C     DATE WRITTEN:  2015/12/22
C     LAST MODIFIED: 2017/02/07
C
C     PROGRAM DESCRIPTION: THIS PROGRAM CALCULATES VARIOUS STATISTICS
C         ON THE APRETURE MAP BEFORE ANY CONVERSIONS HAVE BEEN APPLIED
C
C     SUBROUTINE CALLS: NONE
C
C ----------------------------------------------------------------------
C     VARIABLE DESCRIPTION
C       VARG - HOLDS VARIOGRAM DATA USED TO CALCULATE CORRELATION LENGTH
C       MAX_LEN - LIMITS CORRELTION LENGTH CALCULATIONS TO ONLY APPLY
C           WITHIN A CERTAIN RADIUS
C       MAP_VAR - APERTURE DATA VARIANCE
C       SM - USED TO STORE THE SUM OF DIFFERENCES IN VARIANCE CALCULATION
C       SMS - USED TO STORE THE SUM OF DIFFERENCES SQUARED IN VARIANCE
C           CALCULATION
C
C ----------------------------------------------------------------------
C
      IMPLICIT NONE
      REAL(8), INTENT(IN) :: DATA_MAP(:, :)
      REAL(8), ALLOCATABLE, INTENT(OUT) :: STAT_VALS(:)
      CHARACTER(*), ALLOCATABLE, INTENT(OUT) :: STAT_KEYS(:)
      !
      REAL(8),ALLOCATABLE :: VARG(:,:)
      REAL(8) :: AVG_VAL, MAP_VAR, MAP_DEV, MAP_RMS, SM, SMS
      REAL(8) :: MAX_LEN, MAP_X_CORR, MAP_Z_CORR
      REAL(8) :: TEST(3)
      INTEGER :: NX, NZ,IX,IZ,K
      !
      NX = SIZE(DATA_MAP, DIM=2)
      NZ = SIZE(DATA_MAP, DIM=1)
      MAX_LEN = REAL(MIN(NX, NZ), 8) / 2.0
      AVG_VAL = SUM(DATA_MAP) / (NX * NZ)
      ALLOCATE(VARG(0:MAX(NX, NZ), 5))
C
C     CALCULATING THE RMS OF THE FRACTURE APERTURE
      MAP_RMS = 0.0
      MAP_DEV = 0.0
      MAP_VAR = 0.0
      SMS = 0.0 !SUM OF DIFFERENCES SQUARED
      SM = 0.0  !SUM OF DIFFERENCES
      DO IZ = 1,NZ
        DO IX = 1,NX
          MAP_RMS = MAP_RMS + DATA_MAP(IZ,IX)**2
          SM = SM + (DATA_MAP(IZ,IX) - AVG_VAL)
          SMS = SMS + (DATA_MAP(IZ,IX) - AVG_VAL)**2
        END DO
      END DO
      SM = (SM * SM) * REAL(NX*NZ, 8)**(-1)
      MAP_RMS = MAP_RMS * REAL(NX*NZ, 8)**(-1)
      MAP_VAR = (SMS - SM) * REAL(NX*NZ-1, 8)**(-1)
      MAP_RMS = SQRT(MAP_RMS)
      MAP_DEV = SQRT(MAP_VAR)
C
C     CALCULATING HORIZONTAL VARIOGRAM DATA TO GET X - CORRELATION LENGTH
      VARG(:,:) = 0.0
      TEST(:) = 0.0
      MAP_X_CORR = 0.0
      DO K = 1,INT(MAX_LEN)+1
        ! COMPARING TO POINT OFFSET K CELLS RIGHT OF REFERENCE POINT
        DO IX = 1,NX
          DO IZ = 1,NZ
            IF ((IX+K) > NX) CYCLE
            VARG(K,1) = VARG(K,1) + 1
            VARG(K,2) = VARG(K,2)+(DATA_MAP(IZ,IX)-DATA_MAP(IZ,IX+K))**2
          END DO
        END DO
        ! CALCULATING AVERAGE LENGTH AND VARIANCE FOR OFFSET K
        IF (VARG(K,1) == 0) CYCLE
        VARG(K,3) =  VARG(K,2)/(VARG(K,1))
        MAP_X_CORR = REAL(K, 8)
        TEST(1) = ABS(VARG(K,3)/MAP_VAR - 0.90)
        IF (VARG(K,3)/MAP_VAR > 0.90) THEN
          IF (TEST(2) < TEST(1)) MAP_X_CORR = TEST(3)
          EXIT
        END IF
        TEST(2) = TEST(1)
        TEST(3) = MAP_X_CORR
      END DO
C
C     CALCULATING VERTICAL VARIOGRAM DATA TO GET Z - CORRELATION LENGTH
      VARG(:,:) = 0.0
      TEST(:) = 0.0
      MAP_Z_CORR = 0.0
      DO K = 1,INT(MAX_LEN)+1
        ! COMPARING TO POINT OFFSET K CELLS ABOVE REFERENCE POINT
        DO IX = 1,NX
          DO IZ = 1,NZ
            IF ((IZ+K) > NZ) CYCLE
            VARG(K,1) = VARG(K,1) + 1
            VARG(K,2) = VARG(K,2)+(DATA_MAP(IZ,IX)-DATA_MAP(IZ+K,IX))**2
          END DO
        END DO
        ! CALCULATING AVERAGE LENGTH AND VARIANCE FOR OFFSET K
        IF (VARG(K,1) == 0) CYCLE
        VARG(K,3) =  VARG(K,2)/(VARG(K,1))
        MAP_Z_CORR = REAL(K, 8)
        TEST(1) = ABS(VARG(K,3)/MAP_VAR - 0.90)
        IF (VARG(K,3)/MAP_VAR > 0.90) THEN
          IF (TEST(2) < TEST(1)) MAP_Z_CORR = TEST(3)
          EXIT
        END IF
        TEST(2) = TEST(1)
        TEST(3) = MAP_Z_CORR
      END DO
C
C     SETTING VALUES IN RETURN ARRAYS
      ALLOCATE(STAT_KEYS(5), STAT_VALS(5))
      STAT_KEYS(1) = 'MAP_RMS'; STAT_VALS(1) = MAP_RMS
      STAT_KEYS(2) = 'MAP_DEV'; STAT_VALS(2) = MAP_DEV
      STAT_KEYS(3) = 'MAP_X_CORR'; STAT_VALS(3) = MAP_X_CORR
      STAT_KEYS(4) = 'MAP_Z_CORR'; STAT_VALS(4) = MAP_Z_CORR
      STAT_KEYS(5) = 'MAP_AVG_VAL'; STAT_VALS(5) = AVG_VAL
C
      RETURN
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      END MODULE
