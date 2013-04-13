;*********************************************************************
;+
;
;*name:
;    parcheck     (general idl library 01)  30-mar-1987
;
;*class:
;    error checking
;
;*category:
; 
;*purpose:
;    to check that a procedure has been called with the minimum of allowed
;    number of parameters. 
; 
;*calling sequence:
;    parcheck,nparm,minparms,callingpro
; 
;*parameters:
;    nparm       (req) (i) (0) (i)
;                required input scalar giving the number of parameters
;                in the procedure call (i.e. n_params(0)).
;    minparms    (req) (i) (0 1) (i)
;                if scalar, the minimum number of parameters needed for the
;                procedure to execute properly.
;                if an array, it represents the allowed numbers of
;                parameters (e.g. if 3,4 or 6 parameters are allowed,
;                then set minparms([0,1,2]) = [3,4,6] ).
;    callingpro  (req) (i) (0) (s)
;                required string giving the name of the calling procedure.
;
;*examples:
;     determine if procedure pro, which contains a
;     call to parcheck has the minimum number of parameters
;     (i.e. 4):
;             parcheck,n_params(0),4,'pro'
;     if the same procedure can have 4,5,7, or 8 parameters
;     then use:
;             parcheck,n_params(0),[4,5,7,8],'pro'
;
;*system variables used:
;     none
;
;*interactive input:
;     none
;
;*subroutines called:
;     pcheck
;
;*files used:
;     none 
;
;*side effects:
;     none
;
;*restrictions:
;     none
;
;*notes:
;     none
;
;*procedure:
;     the input parameters to parcheck are first checked themselves
;     using pcheck. if minparms is a scalar it is compared to nparm.
;     if nparm < minparms, then an error message is printed and the
;     procedure returns to the main level. if minparms is a vector,
;     then nparm is subtracted from each value of minparms and the
;     resulting vector is checked for zeroes. if no values are zero,
;     then error messages are printed and the program returns to the
;     main level.
; 
;*modification history :
;     mar 30 1987    cag  gsfc  initial program
;     apr    1987    rwt  gsfc  add vector input for parameters
;     mar 15 1988    cag  gsfc  add vax rdaf-style prolog
;     jul 12 1989    jtb  gsfc  converted to sun/unix idl
;     nov  2 1989    rwt  gsfc  correct print format syntax
;-
;***********************************************************************
pro parcheck,nparm,minparms,callingpro
; check input parameters
;
pcheck,nparm,1,100,0111
pcheck,minparms,2,110,0111
pcheck,callingpro,3,100,1000
cpro = strupcase(callingpro)
;
; check if number of parameters is > minimum (if minparms is scalar)
;
s = size(minparms)
if s(0) eq 0 then begin
  if nparm lt minparms then begin
     print,format='(1x,3a,i2,a)','procedure ',cpro,  $
       ' needs at least ',fix(minparms),' parameters to execute.'
     print,format='(1x,a,i2,a)','only ',fix(nparm),' parameters were specified'
     print,'action: returning to the main program level'
     retall
     end
;
; check if nparm is an allowed number of parameters (if minparms is a vector)
;
  end else begin
     ind = where(minparms-nparm,nonz) ; nonz will be # of non-zero values
     if s(1) eq nonz then begin
        print,'invalid number of input parameters for procedure ',cpro
        print,'action: returning to the main program level'
        retall
        end
     end
return
end
