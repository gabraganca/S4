pro forclte,file=file
;
if n_elements(file) eq 0 then file='fort.8'
;
get_lun,lun1
openr,lun1,file
get_lun,lun2
spawn,'/bin/rm -f f8'
openw,lun2,'f8'
;
readf,lun1,nd,npar
npar0=3
;
dm=fltarr(nd)
par=fltarr(npar)
;
readf,lun1,dm
;
print,nd,npar0
print,dm
printf,lun2,nd,npar0,format='(2i6)'
printf,lun2,dm
;
while not eof(lun1) do begin
 readf,lun1,par
 par0=par(0:2)
 print,par0
 printf,lun2,par0
endwhile
;
close,lun1
free_lun,lun1
close,lun2
free_lun,lun2
return
end