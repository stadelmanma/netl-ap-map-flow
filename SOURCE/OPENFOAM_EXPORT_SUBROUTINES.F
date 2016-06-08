C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE INITIALIZE_EXPORT(BOK)
C
      USE TWOD_MODULE
      USE UNIT_CONVERSION_MODULE
      IMPLICIT NONE
      LOGICAL :: BOK
C
C     DEFAULT VALUES
      FOAM_EXPORT = .TRUE.
      VOX_MET  = 1.0
      AVG_FACT = 1.0
      HIGH_MASK = 10000.0
      LOW_MASK = 1E-6
      R_FACT = 0.0
      UNIT(:)     = 'SI'
      UNIT_IN(1) = 'PA'
      UNIT_IN(2) = 'M'
      UNIT_IN(3) = 'FAHR'
      UNIT_IN(4) = 'SEC'
      UNIT_IN(5) = 'M^3/SEC'
      UNIT_IN(6) = 'PA*SEC'
      UNIT_IN(7) = 'KG/M^3'
C
C     INITIALIZING IO
      CALL ASSIGN_IO(BOK)
      IF (.NOT. BOK) GOTO 1000
C
C     READING INPUT FILE
      CALL READ_MASTER(BOK)
      IF (.NOT. BOK) GOTO 1000
C
C     READING APERTURE MAP
      CALL READ_AP_MAP(BOK)
      IF (.NOT. BOK) GOTO 1000
C
C     STEPPING THROUGH APERTURE MAP AND MAKING THE RESPECTIVE FIELDS
      CALL GENERATE_2DMESH
      IF (.NOT. BOK) GOTO 1000
C
      RETURN
C
C
 1000 BOK = .FALSE.
      RETURN
C
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE GENERATE_2DMESH
C
      USE TWOD_MODULE
      USE UNIT_CONVERSION_MODULE
C
      IMPLICIT NONE
      REAL(8),ALLOCATABLE :: REAL_ARRAY(:,:) !TEMP ARRAY FOR RESIZE
      INTEGER,ALLOCATABLE :: INT_ARRAY(:,:)  !TEMP ARRAY FOR RESIZE
      INTEGER,ALLOCATABLE :: POINT_MAP(:,:,:)
      INTEGER :: I,IX,IZ
      INTEGER :: IV,IB,IN,IO,IS,IFB ! SPECIFIC ITERATORS/COUNTERS
      LOGICAL :: TOP,BOT,LFT,RHT
C
C     ARRAY ALLOCATIONS
      ALLOCATE(REAL_ARRAY(0:NX*NZ*8-1,4),INT_ARRAY(0:NX*NZ*8-1,4))
      ALLOCATE(POINT_MAP(NZ+1,NX+1,4))
      ALLOCATE(VERTICIES(0:NX*NZ*8-1,3))
      ALLOCATE(BLOCKS(0:NX*NZ-1,8))
      ALLOCATE(INLET(0:NX*NZ*8-1,4),OUTLET(0:NX*NZ*8-1,4))
      ALLOCATE(FRONTBACK(0:NX*NZ*8-1,4),SIDES(0:NX*NZ*8-1,4))
C
C     INITIALIZING ARRAYS AND ITERATORS/COUNTERS
      POINT_MAP(:,:,:) = -1
      VERTICIES(:,:) = -1
      BLOCKS(:,:) = -1
      INLET(:,:) = -1
      OUTLET(:,:) = -1
      SIDES(:,:) = -1
      FRONTBACK(:,:) = -1
      INTERNAL_MESH(:) = 5 !THIS WILL BE AN INPUT EVENTUALLY
      IV  = 0
      IB  = 0
      IN  = 0
      IO  = 0
      IS  = 0
      IFB = 0
C
C     CONVERTING AP_MAP BACK TO VOXELS TO SIMPLIFY OUTPUT
      AP_MAP(1:NZ,1:NX,:) = AP_MAP(1:NZ,1:NX,:)/VOX_MET
C
      TOP = .FALSE.
      BOT = .FALSE.
      LFT = .FALSE.
      RHT = .FALSE.
      IF (INDEX(OUTFLOW,'TOP')    > 0) TOP = .TRUE.
      IF (INDEX(OUTFLOW,'BOTTOM') > 0) BOT = .TRUE.
      IF (INDEX(OUTFLOW,'LEFT')   > 0) LFT = .TRUE.
      IF (INDEX(OUTFLOW,'RIGHT')  > 0) RHT = .TRUE.
C
C     CREATING THE POINT MAP AND VERTICIES
      VERTICIES(IV,:) = (/ 0.0D0, -AP_MAP(1,1,1)/2.0, 0.0D0 /)
      POINT_MAP(1,1,1) = IV !POINT MAP WILL STORE THE LOWER SURFACE KNOWING THE UPPER IS IV+1
      IV = IV + 1
      VERTICIES(IV,:) = (/ 0.0D0, AP_MAP(1,1,1)/2.0, 0.0D0 /)
      IV = IV + 1
      !
      DO IZ = 1,NZ
        DO IX = 1,NX
          IF (IX == 1) THEN
            VERTICIES(IV,1) =  0.0D0 * AVG_FACT
            VERTICIES(IV,2) = -AP_MAP(IZ,IX,4)/2.0
            VERTICIES(IV,3) =  DBLE(IZ) * AVG_FACT
            POINT_MAP(IZ,IX,4)   = IV
            POINT_MAP(IZ+1,IX,1) = IV
            IV = IV + 1
            VERTICIES(IV,1) =  0.0D0 * AVG_FACT
            VERTICIES(IV,2) =  AP_MAP(IZ,IX,4)/2.0
            VERTICIES(IV,3) =  DBLE(IZ) * AVG_FACT
            IV = IV + 1
          END IF
          !
          IF (IZ == 1) THEN
            VERTICIES(IV,1) =  DBLE(IX) * AVG_FACT
            VERTICIES(IV,2) = -AP_MAP(IZ,IX,2)/2.0
            VERTICIES(IV,3) =  0.0D0 * AVG_FACT
            POINT_MAP(IZ,IX,2)   = IV
            POINT_MAP(IZ,IX+1,1) = IV
            IV = IV + 1
            VERTICIES(IV,1) =  DBLE(IX) * AVG_FACT
            VERTICIES(IV,2) =  AP_MAP(IZ,IX,2)/2.0
            VERTICIES(IV,3) =  0.0D0 * AVG_FACT
            IV = IV + 1
          END IF
          !
          VERTICIES(IV,1) =  DBLE(IX) * AVG_FACT
          VERTICIES(IV,2) = -AP_MAP(IZ,IX,3)/2.0
          VERTICIES(IV,3) =  DBLE(IZ) * AVG_FACT
          POINT_MAP(IZ,IX,3)   = IV
          POINT_MAP(IZ+1,IX,2) = IV
          POINT_MAP(IZ,IX+1,4) = IV
          POINT_MAP(IZ+1,IX+1,1) = IV
          IV = IV + 1
          VERTICIES(IV,1) =  DBLE(IX) * AVG_FACT
          VERTICIES(IV,2) =  AP_MAP(IZ,IX,3)/2.0
          VERTICIES(IV,3) =  DBLE(IZ) * AVG_FACT
          IV = IV + 1
        END DO !END NX
      END DO !END NZ
C
C     POPULATING BLOCK ARRAY
      DO IZ = 1,NZ
        DO IX = 1,NX
          BLOCKS(IB,1) = POINT_MAP(IZ,IX,1)     !BACK BOTTOM LEFT
          BLOCKS(IB,2) = POINT_MAP(IZ,IX,2)     !BACK BOTTOM RIGHT
          BLOCKS(IB,3) = POINT_MAP(IZ,IX,2) + 1 !FRONT BOTTOM RIGHT
          BLOCKS(IB,4) = POINT_MAP(IZ,IX,1) + 1 !FRONT BOTTOM LEFT
          BLOCKS(IB,5) = POINT_MAP(IZ,IX,4)     !BACK TOP LEFT
          BLOCKS(IB,6) = POINT_MAP(IZ,IX,3)     !BACK TOP RIGHT
          BLOCKS(IB,7) = POINT_MAP(IZ,IX,3) + 1 !FRONT TOP RIGHT
          BLOCKS(IB,8) = POINT_MAP(IZ,IX,4) + 1 !FRONT TOP LEFT
          IB = IB + 1
        END DO !END NX
      END DO !END NZ
C
C     CREATING INLET, OUTLET, SIDES AND FRONTBACK ARRAYS
      IB = 0
      DO IX = 1,NX !GOING ALONG Z = 0 EDGE
        IF (TOP) THEN
          INLET(IN,1) =  BLOCKS(IB,1)
          INLET(IN,2) =  BLOCKS(IB,2)
          INLET(IN,3) =  BLOCKS(IB,3)
          INLET(IN,4) =  BLOCKS(IB,4)
          IN = IN + 1
        ELSE IF (BOT) THEN
          OUTLET(IO,1) =  BLOCKS(IB,1)
          OUTLET(IO,2) =  BLOCKS(IB,2)
          OUTLET(IO,3) =  BLOCKS(IB,3)
          OUTLET(IO,4) =  BLOCKS(IB,4)
          IO = IO + 1
        ELSE IF ((LFT) .OR. (RHT)) THEN
          SIDES(IS,1) =  BLOCKS(IB,1)
          SIDES(IS,2) =  BLOCKS(IB,2)
          SIDES(IS,3) =  BLOCKS(IB,3)
          SIDES(IS,4) =  BLOCKS(IB,4)
          IS = IS + 1
        END IF
        IB = IB + 1
      END DO
      !
      IB = (NZ - 1)*NX
      DO IX = 1,NX !GOING ALONG Z = NZ EDGE
        IF (TOP) THEN
          OUTLET(IO,1) =  BLOCKS(IB,5)
          OUTLET(IO,2) =  BLOCKS(IB,6)
          OUTLET(IO,3) =  BLOCKS(IB,7)
          OUTLET(IO,4) =  BLOCKS(IB,8)
          IO = IO + 1
        ELSE IF (BOT) THEN
          INLET(IN,1) =  BLOCKS(IB,5)
          INLET(IN,2) =  BLOCKS(IB,6)
          INLET(IN,3) =  BLOCKS(IB,7)
          INLET(IN,4) =  BLOCKS(IB,8)
          IN = IN + 1
        ELSE IF ((LFT) .OR. (RHT)) THEN
          SIDES(IS,1) =  BLOCKS(IB,5)
          SIDES(IS,2) =  BLOCKS(IB,6)
          SIDES(IS,3) =  BLOCKS(IB,7)
          SIDES(IS,4) =  BLOCKS(IB,8)
          IS = IS + 1
        END IF
        IB = IB + 1
      END DO
      !
      DO IZ = 0,NZ-1 !GOING ALONG X = 0 EDGE
        IB = (IZ*NX)
        IF ((TOP) .OR. (BOT)) THEN
          SIDES(IS,1) =  BLOCKS(IB,1)
          SIDES(IS,2) =  BLOCKS(IB,4)
          SIDES(IS,3) =  BLOCKS(IB,8)
          SIDES(IS,4) =  BLOCKS(IB,5)
          IS = IS + 1
        ELSE IF (LFT) THEN
          OUTLET(IO,1) =  BLOCKS(IB,1)
          OUTLET(IO,2) =  BLOCKS(IB,4)
          OUTLET(IO,3) =  BLOCKS(IB,8)
          OUTLET(IO,4) =  BLOCKS(IB,5)
          IO = IO + 1
        ELSE IF (RHT) THEN
          INLET(IN,1) =  BLOCKS(IB,1)
          INLET(IN,2) =  BLOCKS(IB,4)
          INLET(IN,3) =  BLOCKS(IB,8)
          INLET(IN,4) =  BLOCKS(IB,5)
          IN = IN + 1
        END IF
      END DO
      !
      DO IZ = 0,NZ-1 !GOING ALONG X = NX EDGE
        IB = (IZ*NX) + NX - 1
        IF ((TOP) .OR. (BOT)) THEN
          SIDES(IS,1) =  BLOCKS(IB,2)
          SIDES(IS,2) =  BLOCKS(IB,3)
          SIDES(IS,3) =  BLOCKS(IB,7)
          SIDES(IS,4) =  BLOCKS(IB,6)
          IS = IS + 1
        ELSE IF (LFT) THEN
          OUTLET(IO,1) =  BLOCKS(IB,2)
          OUTLET(IO,2) =  BLOCKS(IB,3)
          OUTLET(IO,3) =  BLOCKS(IB,7)
          OUTLET(IO,4) =  BLOCKS(IB,6)
          IO = IO + 1
        ELSE IF (RHT) THEN
          INLET(IN,1) =  BLOCKS(IB,2)
          INLET(IN,2) =  BLOCKS(IB,3)
          INLET(IN,3) =  BLOCKS(IB,7)
          INLET(IN,4) =  BLOCKS(IB,6)
          IN = IN + 1
        END IF
      END DO
      !
      DO IZ = 0,NZ-1
        DO IX = 0,NX-1
          IB = (IZ*NX) + IX
          ! BACK FACE
          FRONTBACK(IFB,1) = BLOCKS(IB,1)
          FRONTBACK(IFB,2) = BLOCKS(IB,2)
          FRONTBACK(IFB,3) = BLOCKS(IB,6)
          FRONTBACK(IFB,4) = BLOCKS(IB,5)
          IFB = IFB + 1
          ! FRONT FACE
          FRONTBACK(IFB,1) = BLOCKS(IB,4)
          FRONTBACK(IFB,2) = BLOCKS(IB,3)
          FRONTBACK(IFB,3) = BLOCKS(IB,7)
          FRONTBACK(IFB,4) = BLOCKS(IB,8)
          IFB = IFB + 1
        END DO
      END DO
C
C     RESIZING ARRAYS SO I CAN USE SIZE FOR OUTPUT (THIS PART IM KEEPING JUST WANTED IT OUT OF THE WAY)
      REAL_ARRAY = -2.0
      REAL_ARRAY(:,1:3) = VERTICIES(:,1:3)
      DEALLOCATE(VERTICIES)
      ALLOCATE(VERTICIES(0:IV-1,3))
      FORALL (I = 0:IV-1) VERTICIES(I,1:3) = REAL_ARRAY(I,1:3)
      !
      INT_ARRAY = -2
      INT_ARRAY(:,1:4) = INLET(:,1:4)
      DEALLOCATE(INLET)
      ALLOCATE(INLET(0:IN-1,4))
      FORALL (I = 0:IN-1) INLET(I,1:4) = INT_ARRAY(I,1:4)
      !
      INT_ARRAY = -2
      INT_ARRAY(:,1:4) = OUTLET(:,1:4)
      DEALLOCATE(OUTLET)
      ALLOCATE(OUTLET(0:IO-1,4))
      FORALL (I = 0:IO-1) OUTLET(I,1:4) = INT_ARRAY(I,1:4)
      !
      INT_ARRAY = -2
      INT_ARRAY(:,1:4) = SIDES(:,1:4)
      DEALLOCATE(SIDES)
      ALLOCATE(SIDES(0:IS-1,4))
      FORALL (I = 0:IS-1) SIDES(I,1:4) = INT_ARRAY(I,1:4)
      !
      INT_ARRAY = -2
      INT_ARRAY(:,1:4) = FRONTBACK(:,1:4)
      DEALLOCATE(FRONTBACK)
      ALLOCATE(FRONTBACK(0:IFB-1,4))
      FORALL (I = 0:IFB-1) FRONTBACK(I,1:4) = INT_ARRAY(I,1:4)
C
C
      RETURN
C
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
      SUBROUTINE OUTPUT_BlockMeshDict
C
      USE TWOD_MODULE
      USE UNIT_CONVERSION_MODULE
      IMPLICIT NONE
      INTEGER :: I
      CHARACTER(1) :: NL,BL
      BL = ' ';
      NL = NEW_LINE(NL)
C
C     WRITTING HEADER DATA
      WRITE(IBMD,"(A)") 'FoamFile'
      WRITE(IBMD,1000)NL,NL,NL,NL,NL
      WRITE(IBMD,1010)
      WRITE(IBMD,"(A)")BL
      WRITE(IBMD,1020)VOX_MET
      WRITE(IBMD,"(A)")BL
C
C     WRITING VERTICES
      WRITE(IBMD,1030)'vertices',NL
      DO I = 0,SIZE(VERTICIES,1) - 1
        WRITE(IBMD,1100)VERTICIES(I,:)
      END DO
      WRITE(IBMD,1031)
      WRITE(IBMD,"(A)")BL
C
C     WRITING BLOCKS
      WRITE(IBMD,1030)'blocks',NL
      DO I = 0,SIZE(BLOCKS,1) - 1
        WRITE(IBMD,1110)BLOCKS(I,:),INTERNAL_MESH(:)
      END DO
      WRITE(IBMD,1031)
      WRITE(IBMD,"(A)")BL
C
C     WRITING EDGES
      WRITE(IBMD,1030)'edges',NL
      WRITE(IBMD,1031)
      WRITE(IBMD,"(A)")BL
C
C     WRITING BOUNDARIES
      WRITE(IBMD,1030)'boundary',NL
      ! INLET
      WRITE(IBMD,1040)'inlet',NL
      WRITE(IBMD,1050)'wall'
      WRITE(IBMD,1035)'faces',NL
      DO I = 0,SIZE(INLET,1) - 1
        WRITE(IBMD,1120)INLET(I,:)
      END DO
      WRITE(IBMD,1036)
      WRITE(IBMD,1041)
      !
      ! OUTLET
      WRITE(IBMD,1040)'outlet',NL
      WRITE(IBMD,1050)'wall'
      WRITE(IBMD,1035)'faces',NL
      DO I = 0,SIZE(OUTLET,1) - 1
        WRITE(IBMD,1120)OUTLET(I,:)
      END DO
      WRITE(IBMD,1036)
      WRITE(IBMD,1041)
      !
      ! SIDES
      WRITE(IBMD,1040)'sides',NL
      WRITE(IBMD,1050)'empty'
      WRITE(IBMD,1035)'faces',NL
      DO I = 0,SIZE(SIDES,1) - 1
        WRITE(IBMD,1120)SIDES(I,:)
      END DO
      WRITE(IBMD,1036)
      WRITE(IBMD,1041)
      !
      ! FRONT AND BACK
      WRITE(IBMD,1040)'frontAndBack',NL
      WRITE(IBMD,1050)'wall'
      WRITE(IBMD,1035)'faces',NL
      DO I = 0,SIZE(FRONTBACK,1) - 1
        WRITE(IBMD,1120)FRONTBACK(I,:)
      END DO
      WRITE(IBMD,1036)
      WRITE(IBMD,1041)
      !
      WRITE(IBMD,1031)
      WRITE(IBMD,"(A)")BL
C
C     WRITING MERGE PATCH PAIRS
      WRITE(IBMD,1030)'mergePatchPairs',NL
      WRITE(IBMD,1031)
      WRITE(IBMD,"(A)")BL
C
      CLOSE(IBMD)
      RETURN
C
 1000 FORMAT('{',A1,
     &             4X,'version     2.0;',A1,
     &             4X,'format      ascii;',A1,
     &             4X,'class       dictionary;',A1,
     &             4X,'object      blockMeshDict;',A1,
     &        '}')
C
 1010 FORMAT('// * * * * * * * * * * * * * * * * * * * * * * * * * *//')
C
 1020 FORMAT('convertToMeters',1X,F12.9,';')
C
 1030 FORMAT(A,A,'(') !0 indent property with (
 1031 FORMAT(');')
 1035 FORMAT(8X,A,A,8X,'(') !8 indent property with (
 1036 FORMAT(8X,');')
C
 1040 FORMAT(4X,A,A,4X,'{') !4 indent name with {
 1041 FORMAT(4X,'}')
C
 1050 FORMAT(8X,'type',1X,A,';')
C
 1100 FORMAT(4X,'(',F12.4,1X,F12.4,1X,F12.4,')') !VERTICES POINT FORMAT
C
 1110 FORMAT(4X,'hex',1X,'(',I0,7(1X,I0),')',1X,'(',I0,2(1X,I0),')',
     &       1X,'simpleGrading',1X,'(1 1 1)') !BLOCK FORMAT
C
 1120 FORMAT(12X,'(',I0,(3(1X,I0)),')') !BOUNDARY FACES FORMAT
C
C
      END SUBROUTINE
C
C ----------------------------------------------------------------------
C ######################################################################
C ----------------------------------------------------------------------
C
