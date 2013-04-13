;*************************************************************************
;+
;
;*NAME:   
;    LINTERP  
;
;*CLASS:Interpolation
;
;*CATEGORY:
;    
;*PURPOSE: 
;    To linearly interpolate tabulated data from one data grid to another.
;
;*CALLING SEQUENCE:
;    LINTERP,XTAB,YTAB,XINT,YINT
;
;*PARAMETERS: 
;    XTAB     (REQ) (I) (1) (I L F D)
;             Required input vector containing the current independent
;             variable grid.
;    YTAB     (REQ) (I) (1) (I L F D)
;             Required input vector containing the current dependent
;             variable values at the XTAB grid points.
;    XINT     (REQ) (I) (0 1) (I L F D)
;             Required input scalar or vector containing the new
;             independent variable grid points for which interpolated
;             value(s) of the dependent variable are sought.
;
;    YINT     (REQ) (O) (0 1) (F D) 
;             Required output scalar or vector with the interpolated
;             value(s) of the dependent variable at the XINT grid points.
; 
;*EXAMPLES:
;    To linearly interpolate from an IUE spectrum wavelength grid to
;    another grid defined as:
;    WGRID=[1540., 1541., 1542., 1543., 1544, 1545.]
;
;    LINTERP,WAVE,FLUX,WGRID,FGRID
;
;*SYSTEM VARIABLES CALLED:
;    None
;
;*INTERACTIVE INPUT:
;    None
; 
;*SUBROUTINES CALLED:
;    TABINV
;    PARCHECK
;
;*FILES USED: 
;    None
;
;*SIDE EFFECTS:
;    None
;
;*RESTRICTIONS:
;    None
;
;*NOTES:
;    None
;
;*PROCEDURE: 
;    Uses TABINV to calculate the effective index of the values
;    in XINT in the table XTAB.  The resulting index is used
;    to calculate the interpolated values YINT from the values
;    in YTAB.
;
;*MODIFICATION HISTORY:
;    Mar 15 1981  D. Lindler   initial program
;    Dec 22 1981  FHS3    GSFC to allow scalar XINT and to use TABINV in the
;                              interpolation
;    Oct 23 1985  JKF     GSFC DIDL compatible...replaced function REORDER
;                              with vector subscripting and indirect 
;                              compilations
;    Jun  5 1987  RWT     GSFC add PARCHECK
;    Mar 14 1988  CAG     GSFC add VAX RDAF-style prolog
;                              and printing of calling sequence when
;                              executed without parameters.
;    Dec 29 1990  JKF/ACC      moved to GHRS DAF
;    Jan 31 1990  JKF/ACC      force input vectors to floating point. (ex
;			       [15,15] becomes [15.,15.]. 
;    Mar 11 1991      JKF/ACC    - moved to GHRS DAF (IDL Version 2)
;-
;****************************************************************************
PRO LINTERP,XTAB,YTAB,XINT,YINT
;-
IF N_PARAMS(0) EQ 0 THEN BEGIN
   PRINT,'LINTERP,XTAB,YTAB,XINT,YINT'
   RETALL
  ENDIF
PARCHECK,N_PARAMS(0),4,'LINTERP'
PCHECK,XTAB,1,010,0111
PCHECK,YTAB,2,010,0111
PCHECK,XINT,3,110,0111
;
X= FLOAT(XINT)				; force floating point (JKF 1/31/91)
S= SIZE(X)
IF S(0) EQ 0 THEN  X=FLTARR(1) + X 
;
; DETERMINE INDEX OF DATA-POINTS FROM WHICH INTERPOLATION IS MADE
;
TABINV,XTAB,X,R			; find exact locations
INDEX=FIX(R)			; find nearest index
R=R-INDEX
;
; PERFORM LINEAR INTERPOLATION
;
YINT= YTAB(INDEX+1) * R + YTAB(INDEX) * (1-R)
;
; RETURN SCALAR IF INPUT WAS SCALAR
;
IF S(0) EQ 0 THEN YINT=YINT(0)
;
RETURN
END
