pro intrpmod,file1,file2,file3,file4,teff=teff,logg=logg,outfile=outfile
;
; interpolation between four models
;
; input:
; keyword parameters:
;          teff - desired Teff
;          logg - desired log g
; positional parameters: file1-4 - core names for models 
; that bracket the desired Teff and log g
;          file1 - low  Teff, low  log g
;          file2 - low  Teff, high log g
;          file3 - high Teff, low  log g 
;          file4 - high Teff, high log g
;
; output - input files for a Synplot run, with a core name "intrp",
; so Synplot is run as synplot,0,0,0,atmos='intrp',...
; 
; Example:
;
; intrpmod,'BGA17000g400v2','BGA17000g425v2','BGA18000g400v2','BGA18000g425v2',$
;          teff=17400,logg=4.1
;
f=strarr(4)
f(0)=file1+'.7'
f(1)=file2+'.7'
f(2)=file3+'.7'
f(3)=file4+'.7'
t=fltarr(4)
g=t
;
a=strmid(strtrim(string(teff),2),0,1)
p=strpos(f(0),'v')-9
for i=0,3 do begin
  get_lun,l1
  openr,l1,f(i)
  readf,l1,nd,np
  dm=fltarr(nd)
  x0=fltarr(np,nd)
  readf,l1,dm
  readf,l1,x0 
  x0 = x0>1.e-35
  reads,strmid(f(i),p,5),tt,format='(f5.0)'
  reads,strmid(f(i),p+6,3),gg,format='(f3.0)'
  t(i)=alog10(tt)
  g(i)=gg*1.e-2
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
dm2=dm1
dm3=dm1
x1=fltarr(np,nd)
x2=x1
x3=x1
;
a1=(g(1)-logg)/(g(1)-g(0))
for id=0,nd1 do begin
  dm1(id)=a1*m(id,0) + (1.-a1)*m(id,1)
  for ip=0,np1 do x1(ip,id)=a1*x(ip,id,0) + (1.-a1)*x(ip,id,1)
endfor
;
a2=(g(3)-logg)/(g(3)-g(2))
for id=0,nd1 do begin
  dm2(id)=a2*m(id,2) + (1.-a2)*m(id,3)
  for ip=0,np1 do x2(ip,id)=a2*x(ip,id,2) + (1.-a2)*x(ip,id,3)
endfor
;
te=alog10(teff)
a3=(t(2)-te)/(t(2)-t(0))
dm3=a3*dm1 + (1.-a3)*dm2
x3=a3*x1 + (1.-a3)*x2
dm3=10.^dm3
x3=10.^x3
;
;oplot,dm3,x3(0,*),thick=3

if n_elements(outfile) eq 0 then outfile='intrp'
get_lun,l1
openw,l1,outfile+'.7'
printf,l1,nd,np,format='(2i5)'
printf,l1,dm3,format='(6e13.6)'
for id=0,nd1 do printf,l1,x3(*,id),format='(6e13.6)'
close,l1
free_lun,l1
spawn,'/bin/cp -f '+file1+'.5 '+outfile+'.5'
;
return
end


