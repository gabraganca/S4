pro plt,file,x,y,                                  $
ncolumns=ncolumns,xcolumn=xcolumn,ycolumn=ycolumn, $
xscale=xscale,yscale=yscale,yabs=yabs,smoo=smoo,   $
nrows=nrows,delbeg=delbeg,delend=delend,           $
io=io,oi=oi,oo=oo,oplt=oplt,noplt=noplt,_extra=e
;
; utility for easy plotting any columns of a file 
;
if n_params(0) eq 0 then begin
print,'plo,file,x,y'
print,''
print,'input:       file'
print,'output:      x,y - arrays of extracted x,y'
print,'keyword parameters: '
print,'  ncolumns  (default=2)'                 
print,'  xcolumn   (default=1)'                 
print,'  ycolumn   (default=2)'                 
print,'  nrows     (default=30000) - max.number of rows' 
print,'  delbeg,delend - number of deleted lines at the'
print,'             beginning and end (default 0 and NROWS)'
print,'  io,oi,oo: if set, plot_io, etc.'
print,'  oplt      if set, oplot ' 
print,'  noplt     if set, no plot ' 
print,' _extra=e   any extra plotting poarameters'   
return
endif
;
if n_elements(xcolumn) eq 0 then xcolumn=1
if n_elements(ycolumn) eq 0 then ycolumn=2
if n_elements(ncolumns) eq 0 then ncolumns=ycolumn
if n_elements(xscale) eq 0 then xscale=1
if n_elements(yscale) eq 0 then yscale=1
if n_elements(nrows) eq 0 then nrows=30000
if n_elements(delend) eq 0 then delend=nrows
;
get_lun,lun1
openr,lun1,file
x=dblarr(nrows) & y=x
x0=dblarr(ncolumns)
a=''
if n_elements(delbeg) gt 0 then for i=1,delbeg do readf,lun1,a
;
i=0L
while not eof(lun1) do begin
 readf,lun1,x0
 x(i)=x0(xcolumn-1)
 y(i)=x0(ycolumn-1)
 i=i+1L
 if i ge delend then goto,endread
endwhile
endread: n=i-1
x=x(0:n)*xscale
if n_elements(yabs) gt 0 then y=abs(y)
y=y(0:n)*yscale
close,lun1
free_lun,lun1
;
if keyword_set(noplt) then return
if n_elements(oplt) eq 0 then begin
   if n_elements(io) gt 0 then $
     plot_io,x,y,_extra=e $
    else if n_elements(oi) gt 0 then $
     plot_oi,x,y,_extra=e $
    else if n_elements(oo) gt 0 then $
     plot_oo,x,y,_extra=e $
    else $
     if n_elements(smoo) eq 0 then plot,x,y,_extra=e else plot,x,smooth(y,smoo),_extra=e
endif else if n_elements(smoo) eq 0 then oplot,x,y,_extra=e else oplot,x,smooth(y,smoo),_extra=e
;
return
end

