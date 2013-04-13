;************************************************************************
;+
; this procedure is used to check the parameters of
; a procedure for correct type and dimensions
;
; variable - variable to be checked
; postion  - parameter position of the variable
; dimension- valid dimensions (3 digit integer)
;             each digit must be 0 or 1
;            1 specifies that the dimension is valid
;            first digit  -   scalar
;            second digit -   one dimensional array
;            third digit  -   two dimensional array
; type     - valid types ( 4 digit integer)
;            each digit must be 0 or 1
;            1 specifies a valid type
;            1st digit-  string
;            2nd      -  byte
;            3rd      -  integer, or longword integer
;            4th      -  floating point, double precision or complex
;
; change history:
;   d. lindler dec. 1980
;   version 2 f.h.schiffer 3rd 17 nov 1981
;             copied into [177001] by rwt 1-17-84
;     10-24-85 rwt modify for new didl data types: longword integer,
;              double precision & complex. modified to be compatible
;              with existing version (i.e., no new input parameters)
;     21-sep-88:  converted to sun idl, john hoegy.
;-
;************************************************************************
pro pcheck,variable,position,dimension,type
;
; decode valid dimensions
;
  vdim=bytarr(3)
  idim=dimension
  for i=0,2 do begin
    itemp=idim/10*10
    vdim(2-i)=idim-itemp
    idim=idim/10
  end
;
; decode valid types
;
  itype=fix(type)
  vtype=bytarr(4)
  for i=0,3 do begin
    itemp=itype/10*10
    vtype(i)=itype-itemp
    itype=itype/10
  end
;
; determine type and dimension of the input variable
;
  s=size(variable)
  ndim=s(0)
  ntype=s(ndim+1)
;
; check if it is defined
;
  if ntype eq 0 then begin
  print,' input variable number',position,' is not defined'
  goto,explain
  end
;
; check for valid type
;
  if (ntype eq 7) and ( vtype(3) ne 0 ) then goto,checkd ;string
  if (ntype eq 1) and ( vtype(2) ne 0 ) then goto,checkd ;byte
  if (ntype eq 2) and ( vtype(1) ne 0 ) then goto,checkd ;integer
  if (ntype eq 3) and ( vtype(1) ne 0 ) then goto,checkd ;longword integer
  if (ntype eq 4) and ( vtype(0) ne 0 ) then goto,checkd ;floating pt.
  if (ntype eq 5) and ( vtype(0) ne 0 ) then goto,checkd ;double precision
  if (ntype eq 6) and ( vtype(0) ne 0 ) then goto,checkd ;complex
;
  print,'the parameter in position',position,' is of invalid type'
  goto,explain
;
;
; check for a valid dimension
;
  checkd:  if vdim(ndim) ne 0 then return
  print,'input variable in position',position,' has wrong dimension'
;
; give correct type(s) and dimensions
;
  explain:
  tmsg='     the valid type(s) are: '
  if vtype(3) ne 0 then tmsg=tmsg+' string '
  if vtype(2) ne 0 then tmsg=tmsg+' byte '
  if vtype(1) ne 0 then tmsg=tmsg+' integer '
  if vtype(0) ne 0 then tmsg=tmsg+' floating point '
  print,tmsg
;
  tmsg='  the valid dimensions are:'
  if vdim(2) ne 0 then tmsg=tmsg+' 2-d '
  if vdim(1) ne 0 then tmsg=tmsg+' 1-d '
  if vdim(0) ne 0 then tmsg=tmsg+' scalar'
  print,tmsg
  print,'type .con or retall to continue'
  stop
  retall
end
