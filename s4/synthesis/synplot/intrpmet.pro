pro intrpmet,file1,file2,met1,met2,metal=metal,outfile=outfile
;
; interpolation between two models
;
; input:
; keyword parameters:
;          metal - desired metallicity (logarithmic)
; positional parameters: file1-2 - core names for models 
; that bracket the desired metallicity
; met1,met2 -corresponding values of model metallicities
;
f=strarr(2)
f(0)=file1+'.7'
f(1)=file2+'.7'
;
for i=0,1 do begin
  get_lun,l1
  openr,l1,f(i)
  readf,l1,nd,np
  dm=fltarr(nd)
  x0=fltarr(np,nd)
  readf,l1,dm
  readf,l1,x0 
  x0 = x0>1.e-35
  nd1=nd-1
  np1=np-1
  if i eq 0 then begin
    m=fltarr(nd,4)
    x=fltarr(np,nd,4)
  endif
  for id=0,nd1 do begin
    m(id,i) = alog10(dm(id))
    for ip=0,np1 do x(ip,id,i) = alog10(x0(ip,id))
  endfor
;  if i eq 0 then plot_oi,dm,x0(0,*),_extra=e else oplot,dm,x0(0,*)
  close,l1
  free_lun,l1
endfor
;
dm1=fltarr(nd)
x1=fltarr(np,nd)
;
a1=(met2-metal)/(met2-met1)
for id=0,nd1 do begin
  dm1(id)=a1*m(id,0) + (1.-a1)*m(id,1)
  for ip=0,np1 do x1(ip,id)=a1*x(ip,id,0) + (1.-a1)*x(ip,id,1)
endfor
dm1=10.^dm1
x1=10.^x1
;
if n_elements(outfile) eq 0 then outfile='intrp_fin'
get_lun,l1
openw,l1,outfile+'.7'
printf,l1,nd,np,format='(2i5)'
printf,l1,dm1,format='(6e13.6)'
for id=0,nd1 do printf,l1,x1(*,id),format='(6e13.6)'
close,l1
free_lun,l1
;spawn,'/bin/cp -f '+file1+'.5 '+outfile+'.5'
;
;
metn=10.^metal
met='-'+strmid(strtrim(string(metn),2),0,5)
;
a='head -17 intrp.5 > begf'
spawn,a
;
get_lun,l1
openr,l1,'intrp.5'
readf,l1,teff,logg
close,l1
free_lun,l1
;
get_lun,l1
openw,l1,'midf'
;
if teff ge 30000. then begin
printf,l1,'    2  '+met+'      0  ! C'
printf,l1,'    2  '+met+'      0  ! N'
printf,l1,'    2  '+met+'      0  ! O'
printf,l1,'    1  '+met+'      0'
printf,l1,'    2  '+met+'      0  ! Ne'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
printf,l1,'    2  '+met+'      0  ! Si'
printf,l1,'    2  '+met+'      0  ! P'
printf,l1,'    2  '+met+'      0  ! S'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
printf,l1,'    2  '+met+'      0  ! Fe'
printf,l1,'    1  '+met+'      0'
printf,l1,'    2  '+met+'      0  ! Ni'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
;
endif else begin
;
printf,l1,'    2  '+met+'      0  ! C'
printf,l1,'    2  '+met+'      0  ! N'
printf,l1,'    2  '+met+'      0  ! O'
printf,l1,'    1  '+met+'      0'
printf,l1,'    2  '+met+'      0  ! Ne'
printf,l1,'    1  '+met+'      0'
printf,l1,'    2  '+met+'      0  ! Mg'
printf,l1,'    2  '+met+'      0  ! Al'
printf,l1,'    2  '+met+'      0  ! Si'
printf,l1,'    1  '+met+'      0'
printf,l1,'    2  '+met+'      0  ! S'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
printf,l1,'    2  '+met+'      0  ! Fe'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
printf,l1,'    1  '+met+'      0'
;
endelse
;
close,l1
free_lun,l1
a='sed ''1,43''d intrp.5 > endf
spawn,a
a='cat begf midf endf > '+outfile+'.5'
spawn,a
;
return
end

