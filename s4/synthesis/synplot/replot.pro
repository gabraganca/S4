pro replot,onlyspectrum=onlyspectrum,                 $
    onlychi=onlychi,landscape=landscape, _extra=e          
;
common fitpar,temp,g,chisqt,wobs,fobs,wl,flm,weigh,$
teffm,loggm,chisqm

;
if n_elements(onlyspectrum) gt 0 then begin
  plot,wobs,fobs,thick=3,_extra=e
  oplot,wl,flm
  oplot,wobs,weigh,/line
  xp=!x.crange(0)+0.1*(!x.crange(1)-!x.crange(0))
  yp=(!y.crange(0)+!y.crange(1))*0.5
  xyouts,xp,yp,'Teff,    log g,  chisq',chars=1.5
  xyouts,xp,yp*0.8,strtrim(string(teffm),2)+'  ' $
  +strtrim(string(loggm,format='(f8.2)'),2)$
  +strtrim(string(chisqm,format='(f8.4)')),chars=1.5
  return
endif
;
if n_elements(onlychi) gt 0 then begin
  surface,chisqt,temp,g,xtit='Teff',ytit='log g',xchars=3,ychars=3,$
          ztit='chisq',zchars=3,_extra=e
;
  xmi=!x.crange(0) 
  xma=!x.crange(1)
  ymi=!y.crange(0) 
  yma=!y.crange(1)
  zmi=!z.crange(0) ;
  zma=!z.crange(1)
  tma=fltarr(2)
  gma=tma
  chma=fltarr(2,2)
  tma(0)=teffm*0.999
  tma(1)=teffm*1.001
  gma(0)=loggm*0.999
  gma(1)=loggm*1.001
  for i=0,1 do for j=0,1 do chma(i,j)=chisqm
  !noeras=1
  surface,chma,tma,gma,thick=5,xchars=3,ychars=3,zchars=3,$
          xr=[xmi,xma],yr=[ymi,yma],zr=[zmi,zma]
  !noeras=0
  return
endif
;
if n_elements(landscape) eq 0 then !p.multi=[0,1,2] else !p.multi=[0,2,1]
plot,wobs,fobs,thick=3,_extra=e
oplot,wl,flm
oplot,wobs,weigh,/line
xp=!x.crange(0)+0.1*(!x.crange(1)-!x.crange(0))
yp=(!y.crange(0)+!y.crange(1))*0.5
xyouts,xp,yp,'Teff,    log g,  chisq',chars=1.5
xyouts,xp,yp*0.8,strtrim(string(teffm),2)+'  ' $
+strtrim(string(loggm,format='(f8.2)'),2)$
+strtrim(string(chisqm,format='(f8.4)')),chars=1.5
surface,chisqt,temp,g,xtit='Teff',ytit='log g',xchars=3,ychars=3,$
        ztit='chisq',zchars=3
  
!p.multi=0
;
return
end
