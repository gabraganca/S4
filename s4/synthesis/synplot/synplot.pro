pro synplot,ispec,iplot,ident,eqw,wl,fl,sp,wlobs,flobs,          $
    atmos=atmos,linlist=linlist,input=input,abund=abund,         $
    teff=teff,logg=logg,metal=metal,                             $
    grid=grid,atdata=atdata,gri2=gri2,met1=met1,met2=met2,       $
    imode=imode,idstd=idstd,                                     $
    kurucz=kurucz,oldinp=oldinp,disk=disk,forcelte=forcelte,     $
    cont=cont,nlte=nlte,lyman=lyman,quasi=quasi,vturb=vturb,     $
    wstart=wstart,wend=wend,wdist=wdist,                         $
    cutoff=cutoff,strength=strength,icontl=icontl,ifhe2=ifhe2,   $
    hydprf=hydprf,he1prf=he1prf,he2prf=he2prf,lemke=lemke,       $
    nangles=nangles,anglmin=anglmin,                             $
    vrot=vrot,steprot=steprot,fwhm=fwhm,stepins=stepins,         $
    vmac_iso=vmac_iso,vmac_rt=vmac_rt,                           $
    relative=relative,scale=scale,rv=rv,                         $
    extend=extend,charsize=charsize,lidshift=lidshift,           $
    observ=observ,noread=noread,spect=spect,                     $
    save=save,oplot=oplot,idtab=idtab,idlim=idlim,               $
    norun=norun,notalk=notalk,noplot=noplot,help=help,_extra=e
;
;
; program for plotting spectra calculated by SYNSPEC, 
; with a possibility to change interactively the chemical composition;
; and interactively convolved with rotation and instrumental broadening;
; and possibly also annotated by line identifications
;
; written by I. Hubeny, Nov-Dec 1994
; modified - Jul 1996 + many times afterward
; significantly modified - Dec 2007 (possibility o interpolating in grids)
; version 2.0 - Feb 2012 (added new programs Synfit and Syn_abund)
; version 2.1 - May 2012 (new features of synfit, syn_abund, 
;               added macroturbulence
;
; ispec   = 0 - Synspec is run
;               no change of chemical composition; 
;         < 0 - Synspec is not run (only Rotins is run)
;         > 0 - ispec elements change abundance; entered interactively
; iplot   = 0 - original plot
;         = 1 - overplot, IPLOT has the meaning of the color index
; ident   = 0 - identification is not plotted        

;
; OPTIONAL KEYWORD INPUT:
;
;   ATMOS        - file name(s) for a model atmosphere
;   LINLIST      - filename of the line list
;   INPUT        - filenames of the additional input (usually not set)
;   OBSERV       - filename of the observed spectrum
;   IMODE        - basic mode of SYNSPEC
;   KURUCZ       - switch for indicating a Kurucz model input (if =1)
;   NLTE         - NLTE switch (see SYNSPEC)
;   LYMAN        - switch for treating Lyman lines (IOPHLI in Synspec)
;   VTURB        - turbulent velocity (in km/s)
;
;   WSTART       - starting wavelength (in Angstrom)
;   WEND         - final wavelength (in A)
;   WDIST        - step in wavelength
;   STRENGTH     - criterion for selecting lines (RELOP in Synspec)
;   CUTOFF       - distance in A to which lines are allow to contribute
;   IFHE2        - He II opacity switch (see SYNSPEC)
; 
;   VROT         - rotational velocity  - v sin i (in km/s)
;   STEPROT      - step for the rotational convolution (if non-zero)
;   FWHM         - FWHM for the instrumental profile (in A)
;   STEPINS      - step for instrumental convolution (if non-zero)
;   RELATIVE     - switch for computing relative spectrum (if =1)
;   SCALE        - a scale factor to multiply the theoretical spectrum
;   RV           - radial velocity (in km/s) applied on theor. spectrum
;
;   EXTEND       - switch for drawing vertical lines in identification
;   CHARSIZE     - character size in identification
;
;   ABUND        - vector of abundance changes
;   SAVE         - core filename for saved files
;
;   _EXTRA       - a set of any extra keywords for PLOT
;
if n_elements(help) gt 0 then begin
   print,'pro synplot,ispec,iplot,ident,eqw,sp,flobs,wlobs, '
   print,'OPTIONAL KEYWORD PARAMETERS '
   print,'  type 1 for a short list; 
   print,'       2 for a long list with explanations;'
   print,'  else return'
   read,ii
   if ii eq 1 then begin
      print,'atmos,linlist,input,observ,  (filenames)'
      print,'imode,idstd,kurucz,nlte,lyman,vturb (fort.55 for SYNSPEC)'
      print,'wstart,wend,wdist,strength,cutoff,ifhe2,icontl, (still fort.55)'
      print,'hydprf,he1prf,he2prf, (H, HeI, HeII line broadening tables-fort.55)'
      print,'nangles,anglmin (still fort.55)'
      print,'vrot,steprot,fwhm,stepins,relative,  (for ROTINS)'
      print,'scale,rv, (radial velocity and scaling of the final spectrum)'
      print,'extend,charsize, (for LINEID)'
      print,'abund,noread,spect,save,_extra  (miscellaneous)'
   endif else begin
      if ii eq 2 then begin
         print,'POSITIONAL PARAMETERS:'
         print,''
         print,'ispec = 0 - normal run of Synspec; <0 - (no run of Synspec),'
         print,'       >0 - ispec abundances changed'
         print,'iplot = 0 - first plot; >0 oplot (iplot is the color index)'
         print,'       <0 - plot only the observed spectrum' 
         print,'ident = 0 - no identification; >0 - identification'
         print,'            in that case, lines with eqw > ident mA are marked'
         print,'eqw   - output: total equivalent width (in mA)'
         print,'sp    - if present, an array of synthetic spectrum (generated
         print,'        by a previous run of Synplot)'
         print,'wlobs - if present, array of wavelengths of the observed spectrum'
         print,'flobs - if present, array of fluxes of the observed spectrum'
         print,''
         print,'KEYWORD PARAMETERS:'
         print,'atmos - names(s) for the input model atmosphere (disk)'
         print,'        if absent: either not needed, or assumed to be'
         print,'                   fort.5 (std input) and fort.8 (model)'
         print,'        if a single string: generic name'
         print,'                   files are atmos.5 and atmos.7'
         print,'        if a 2-comp string vector: '
         print,'                   files are atmos(0) and atmos(1)'
         print,'oldinp - if set, the "old" format of input (up to tlus194,syn41)'
         print,'disk  - if set, input accretion disk model is assumed'
         print,'linlist - filename for the line list (default fort.19)'
         print,'input  - names(s) for the additional input to Synspec'
         print,'         (unit 55) and Rotins (std input)'
         print,'         default - SYNPLOT creates these files'
         print,'         if present, it must be a 2-comp string vector,'
         print,'         [filename for unit55, std input to Rotins]'
         print,'abund  - if present, it is another method to change abundances'
         print,'         must be vector [first at.number, last a.num., abund], 
         print,'         or more triads consecutively'
         print,''
         print,'imode  - basic mode of Synspec (default 0)'
         print,'cont   - the same as imode=2 - flux in continuum'
         print,'idstd  - standard depth; if not set, the program assigns'
         print,'         the last depth point where T<Teff'
         print,'kurucz - if =1, Kurucz model atmosphere, otherwise Tlusty'
         print,'         (default 0 - Tlusty)'
         print,'nlte   - NLTE switch in Synspec 
         print,'         (default 1 - NLTE lines, if NLTE populations given)'
         print,'lyman  - switch for the treatment of Lyman lines (default 1)'
         print,'vturb  - turbulent velocity (in km/s) - default 0'
         print,''
         print,'wstart - starting wavelength (in A)'
         print,'wend   - end of the wavelength interval (in A)'
         print,'wdist  - (maximum) wavelength step (in A) - default 0.01'
         print,'strength - criterion for rejecting lines - default 1.e-4'
         print,'icontl - switch for considering H lines as continua'  
         print,'ifhe2  - switch for treatment He II lines - default 0'
         print,'hydprf - filename for the special H line broadening table'    
         print,'he1prf - filename for the special HeI line broadening table'    
         print,'he2prf - filename for the special HeII line broadening table'  
         print,'nangles- if set, the number of angles for evaluating intensity'
         print,'         equidistant mu''s between 1 and anglmin'
         print,'anglmin- minimum mu = cos(angle) for evaluating intensity'
         print,'           default = 0.1'
         print,''
         print,'vrot   - rotational velocity (in km/s) - default 0'
         print,'       < 0 - ROTIN is not called'
         print,'steprot - wavelength step for rotated spectra (in A),'
         print,'          default = (wstart+wend)*vrot/c/5'
         print,'fwhm   - FWHM for (Gaussian) instrumental profile (default 0)'
         print,'       < 0 - ROTIN is not called'
         print,'stepins- step for convolved spectra (default fwhm/10)'
         print,'relative - if nonzero, plot relative spectrum (default 0)'
         print,'scale  - scale factor for synthetic spectra (default 1)'
         print,'rv     - radial velocity (in km/s) to be applied '
         print,'         to synthethic spectra (default 0)'
         print,''
         print,'extend - swich for drawing lines for identification'
         print,'charsize - character size in identification (default 1)'
         print,'lidshift - if set, identification is shifted with rv'
         print,''
         print,'observ - if present, and is a string, then it is the'
         print,'         the filename of the observed spectrum;'
         print,'         (simple table wavelength (in A) vers. flux(any units))'
         print,'       - if present, and is equal to number 1, '
         print,'         then it indicates that the observed spectrum is'
         print,'         on positional parameters WLOBS and FLOBS'
         print,'noread - if present and non-zero, the synthetic spectrum is'
         print,'         not read from the file fort.11 (must be transfered'
         print,'         by positional parameter SP)'
         print,'spect  - has an effect only if NOREAD is not set,'
         print,'         and if the spectrum is not computed by the present run:'
         print,'         the filaneme where the synthetic spectrum is stored'
         print,'         (if it is different from fort.11)'
         print,''
         print,'save   - if present, filename for saving created files'
         print,'         with filenames save+.7, save+.17, etc'
         print,'_extra - any extra keywords for IDL routine PLOT'
      endif else return
   endelse
   return
endif
;
;  initialization
;
; 
if n_params(0) eq 0 then begin
  ispec=0
  if n_elements(norun) gt 0 then ispec=-1
  iplot=0
  if n_elements(oplot) gt 0 then iplot=oplot
  ident=0
  if n_elements(idtab) gt 0 then ident=idtab 
endif
if n_elements(idlim) gt 0 then ident=idlim
if n_elements(noplot) eq 0 then noplot=0
;
;
if n_elements(atmos) eq 0 and ispec ge 0 then begin
   if n_elements(teff) eq 0 or n_elements(logg) eq 0 then begin
      print,'supply keywords teff and logg!'
      return
   endif
   if n_elements(teff) gt 0 then begin
      if teff le 30000. then begin
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; The next line was changed from the original synplot 
; version.
; My intention with this is to run only the model 
; availabe at bstar2006 folder
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;      
         if n_elements(grid) eq 0 then grid='../bstar2006/BG'
         if n_elements(metal) gt 0 then grid='~/bstar2006/BG'
         if n_elements(gri2) eq 0 then gri2='~/bstar2006/BL'
         if teff lt 15000 or teff ge 30000. then begin
            print,'teff out of range'
            return
         endif
      endif else begin
         if n_elements(grid) eq 0 then grid='~/ostar2002/G'
         if n_elements(gri2) eq 0 then gri2='~/ostar2002/L'
         if teff lt 27500 or teff gt 55000. then begin
            print,'teff out of range'
            return
         endif
      endelse
   endif
;
   if logg lt 1.75 or logg gt 5.5 then begin
      print,'log g out of range'
   endif
   if n_elements(atdata) eq 0 then begin
;      p1=strpos(grid,'/')+1
;      p2=strpos(strmid(grid,p1,100),'/')
;      atdata=strmid(grid,0,p1+p2)+'/data'
      atdata='../atdata'
   endif
   if n_elements(notalk) eq 0 then print,'grid = ',grid,'   atdata = ',atdata
   teff=long(teff)
   lgg=fix(logg*100.)
   g1=lgg/25
   g1=g1*25
   if teff le 30000 then begin
      tef1=(teff/1000*1000)
      tl1=strtrim(string(tef1),2)
      tl2=strtrim(string(tef1+1000),2)
      vs='v2'
    endif else begin
      tef1=(teff/2500l*2500l)
      tl1=strtrim(string(tef1),2)
      tl2=strtrim(string(tef1+2500l),2)
      vs='v10'
   endelse
   gl1=strtrim(string(g1),2)
   gl2=strtrim(string(g1+25),2)
   m1=grid+tl1+'g'+gl1+vs
   m2=grid+tl1+'g'+gl2+vs
   m3=grid+tl2+'g'+gl1+vs
   m4=grid+tl2+'g'+gl2+vs
   intrpmod,m1,m2,m3,m4,teff=teff,logg=logg
;  print,m1,m2,m3,m4
;  print,teff,logg
   if n_elements(metal) eq 0 then begin
      atmos='intrp'
   endif else begin
      m1=gri2+tl1+'g'+gl1+vs
      m2=gri2+tl1+'g'+gl2+vs
      m3=gri2+tl2+'g'+gl1+vs
      m4=gri2+tl2+'g'+gl2+vs
      intrpmod,m1,m2,m3,m4,teff=teff,logg=logg,outfile='intrp2'
     if n_elements(met1) eq 0 then begin
        if strpos(grid,'C') ge 0 then met1=0.3
        if strpos(grid,'G') ge 0 then met1=0.0
        if strpos(grid,'L') ge 0 then met1=-0.3
        if strpos(grid,'S') ge 0 then met1=-0.7
        if strpos(grid,'T') ge 0 then met1=-1.0
     endif
     if n_elements(met2) eq 0 then begin
        if strpos(gri2,'C') ge 0 then met2=0.3
        if strpos(gri2,'G') ge 0 then met2=0.0
        if strpos(gri2,'L') ge 0 then met2=-0.3
        if strpos(gri2,'S') ge 0 then met2=-0.7
        if strpos(gri2,'T') ge 0 then met2=-1.0
     endif
     intrpmet,'intrp','intrp2',met1,met2,metal=metal
     atmos='intrp_fin'
  endelse
endif
;
if n_elements(atmos) eq 1 then begin
   fort5=atmos+".5"
   fort8=atmos+".7"
endif 
if n_elements(atmos) eq 2 then begin
   fort5=atmos(0)
   if fort5 eq 'cool.5' then oldinp=1
   if fort5 eq 'cooln.5' then atdata='../atdata'
   fort8=atmos(1)
endif   
;
if n_elements(forcelte) gt 0 then begin
   forclte,file='fort8'
   spawn,'/bin/cp -f f8 fort8'
endif
;
if n_elements(linlist) eq 1 then begin
   if linlist ne 'fort.19' then begin
   a='ln -s -f '+linlist+' fort.19'
   spawn,a
   endif
endif
;
if n_elements(atdata) gt 0 then begin
   a='ln -f -s '+atdata+' data'
   spawn,a
endif
;
if n_elements(imode) eq 0 then imode=0
if keyword_set(cont) then imode=2
if n_elements(kurucz) eq 0 then inmod=1 else begin
   if kurucz ge 0 then inmod=0 & endelse
if ispec ge 0 then begin
   if strmid(fort8,0,5) eq 'ap00t' then inmod=0
endif
if keyword_set(disk) then inmod=2
if n_elements(nlte) eq 0 then nlte=1
if inmod eq 0 then nlte=0
if n_elements(icontl) eq 0 then icontl=0
if n_elements(ifhe2) eq 0 then ifhe2=0
if n_elements(lyman) eq 0 then lyman=0
;
; set up parameteres for special line broadening tables
;
if n_elements(lemke) eq 0 then lemke=1
if lemke gt 0 then begin
   DIRDAT='./'
   al='ln -s '+DIRDAT+'lyman fort.21'
   ab='ln -s '+DIRDAT+'balmer fort.22'
   spawn,'/bin/rm -f fort.21; '+al
   spawn,'/bin/rm -f fort.22; '+ab
   ihydpr=2122
   if lemke gt 2 then begin
      ap='ln -s '+DIRDAT+'pasch fort.23'
      ab='ln -s '+DIRDAT+'brack fort.24'
      spawn,'/bin/rm -f fort.23; '+ap
      spawn,'/bin/rm -f fort.24; '+ab
      ihydpr=21222324
   endif
endif else begin
if n_elements(hydprf) eq 0 then ihydpr=0 else begin $
   ihydpr=-20 
   spawn,'/bin/rm -f fort.20'
   hydprf=strtrim(string(hydprf),2)
   if hydprf ne '1' then begin
      a='ln -s '+hydprf+' fort.20'
      spawn,a
   endif else begin
      spawn,'ln -s hydprf.dat fort.20'
      hydprf='hydprf.dat'
   endelse
endelse
endelse
;
if n_elements(he1prf) eq 0 then begin
   ihe1pr=25 
   he1prf=1
endif 
   spawn,'/bin/rm -f fort.25'
   he1prf=strtrim(string(he1prf),2)
   if he1prf eq '0' then ihe1pr=0 else begin $
   if he1prf ne '1' then begin
      a='ln -s '+he1prf+' fort.25'
      spawn,a
      ihe1pr=25
   endif else begin
      spawn,'ln -s he1prf.dat fort.25'
      he1prf='he1prf.dat'
      ihe1pr=25
   endelse
endelse
;
if n_elements(he2prf) eq 0 then begin
   ihe2pr=26 
   he2prf=1
endif 
   spawn,'/bin/rm -f fort.26'
   he2prf=strtrim(string(he2prf),2)
   if he2prf eq '0' then ihe2pr=0 else begin $
   if he2prf ne '1' then begin
      a='ln -s '+he2prf+' fort.26'
      spawn,a
      ihe2pr=26
   endif else begin
      spawn,'ln -s he2prf.dat fort.26'
      he2prf='he2prf.dat'
      ihe2pr=26
   endelse
endelse
;
nalp=0
nbet=0
ngam=0
nbal=0
if n_elements(quasi) gt 0 then begin
   if quasi ge 1 then begin
      nalp=3
      spawn,'/bin/rm -f fort.3; ln -s laquasi.dat fort.3'
   endif
   if quasi ge 2 then begin
      nbet=18
      spawn,'/bin/rm -f fort.18; ln -s lbquasi.dat fort.18'
   endif
   if quasi ge 3 then begin
      ngam=28
      spawn,'/bin/rm -f fort.28; ln -s lgquasi.dat fort.28'
   endif
endif
;
if n_elements(cutoff) eq 0 then cutoff=10
if n_elements(strength) eq 0 then strength =1.e-4
if n_elements(wdist) eq 0 then if imode ne 2 then wdist=0.01 else $
                                                  wdist=0.5
;
close,1
;
if ispec ge 0 then begin
   if n_elements(wstart) eq 0 then begin
      spawn,'/bin/rm -f lin1.tmp
;      spawn,'head -1 fort.19 > lin1.tmp'
      openr,1,'lin1.tmp'
      readf,1,al1
      close,1
      wstart=al1*10.
      if imode eq 1 then wstart=wstart-cutoff*0.5
   endif
;     
   if n_elements(wend) eq 0 then begin
      spawn,'/bin/rm -f lin2.tmp
      spawn,'tail -1 fort.19 > lin2.tmp'
      openr,1,'lin2.tmp' 
      readf,1,al2
      close,1
      wend=al2*10.
      if imode eq 1 then wend=wend+cutoff*0.5
   endif
endif else begin
   if n_elements(wstart) eq 0 then begin
      spawn,'/bin/rm -f lin1.tmp
      spawn,'head -1 fort.7 > lin1.tmp'
      openr,1,'lin1.tmp'
      readf,1,al1
      close,1
      wstart=al1
   endif
;
   if n_elements(wend) eq 0 then begin
      spawn,'/bin/rm -f lin2.tmp
      spawn,'tail -1 fort.7 > lin2.tmp'
      openr,1,'lin2.tmp' 
      readf,1,al2
      close,1
      wend=al2
   endif
endelse
;
if n_elements(vrot) eq 0 then vrot=0.
if n_elements(steprot) eq 0 then steprot=0
if n_elements(fwhm) eq 0 then fwhm=0.
if n_elements(stepins) eq 0 then stepins=0
if n_elements(relative) eq 0 then relative=0
if n_elements(scale) eq 0 then scale=1.
if n_elements(rv) eq 0 then rv=0.
;
if ispec ge 0 then begin
;
;  construct the input file fort.55 for Synspec 
;
   if n_elements(input) eq 0 then begin
      if keyword_set(idstd) then idst=idstd else begin
         if inmod eq 0 or inmod eq 2 then idst=46 else begin
            spawn,'/bin/rm -f tetmp'
;           a='grep -v "*" '+fort5+' |head -1 > tetmp'
            a='head -1 '+fort5+' > tetmp'
            spawn,a
            close,1 & openr,1,'tetmp'
            readf,1,teff,grav
            close,1 & openr,1,fort8
            readf,1,nd,np
            dm=fltarr(nd)
            readf,1,dm
            parm=fltarr(np,nd)
            readf,1,parm
            temp=parm(0,*)
            for id=0,nd-1 do if temp(id) lt teff then ids=id
            idst=ids+1
          endelse
      endelse
      close,1 & openw,1,'f55'
      zero=0
      one=1
      printf,1,imode,idst,zero
      printf,1,inmod,zero,zero,one
      printf,1,lyman,nalp,nbet,ngam,nbal
      printf,1,one,nlte,icontl,zero,ifhe2
      printf,1,ihydpr,ihe1pr,ihe2pr
      printf,1,wstart,wend,cutoff,zero,strength,wdist
      printf,1,zero,zero
      noturb=0
      if n_elements(vturb) eq 1 then printf,1,vturb else noturb=1
      if keyword_set(nangles) then begin
         if n_elements(anglmin) eq 0 then anglmin=0.1
         if noturb eq 1 then printf,1,-1
         iflux=1
         printf,1,nangles,anglmin,iflux
         if nangles lt 0 then begin
            print,'enter ',-nangles,' values of mu=cos(angle)'
            ang=fltarr(-nangles)
            read,ang
            printf,1,ang
         endif
      endif
      close,1
      spawn,'/bin/cp f55 fort.55'
   endif
;    
;  construct the input file fort.56 for Synspec 
;    
   openw,1,'inp.tmp'
   if ispec le 0 then begin
      izer=0
      if n_elements(abund) eq 0 then printf,1,izer
   endif else begin
;    
;  interactive input of abundances
;    
      for i=1,ispec do begin
         print,'enter starting and ending atomic number, abund
         read,ia0,ia1,abun
         for ia=ia0,ia1 do printf,1,ia,abun,format='(i4,e15.5)'
      endfor
   endelse
;    
;  input of abundances as a parameter ABUND
;
   if n_elements(abund) ge 3 then begin
      ispec=n_elements(abund)/3
      for i=0,ispec-1 do begin
         for ia=abund(3*i),abund(3*i+1) do printf,1,ia,abund(3*i+2),format='(i4,e15.5)'
      endfor
   endif
   close,1
   if n_elements(abund) gt 0 or ispec gt 0 then begin
      spawn,'/bin/rm -f inum.tmp inum1.tmp fort.56' 
      spawn,'wc -l inp.tmp > inum.tmp'
      spawn,'sed s/inp.tmp// inum.tmp > inum1.tmp'
      spawn,'cat inum1.tmp inp.tmp > fort.56'
   endif else begin
       spawn,'/bin/cp inp.tmp fort.56'
   endelse
;    
;  construct the input file fort.1 for Synspec 
;    
   i=0
   if keyword_set(oldinp) then i=1
   openw,1,'f1'
   printf,1,i
   close,1
   spawn,'/bin/cp -f f1 fort.1'
;    
   a='/bin/cp '+fort8+' fort.8'
   spawn,a
; 
   spawn,'/bin/rm -f sylog.tmp'   
   a='./synspec49 < '+fort5+' > sylog.tmp'
;          
   spawn,a
   spawn,'/bin/rm -f eq.tmp'
   spawn,'tail -1 fort.16 > eq.tmp'
   openr,1,'eq.tmp'
   readf,1,t1,t2,t3,t4,eqw1
   if n_elements(notalk) eq 0 then print,'total equivalent width: ',eqw1,'  milliangstrom'
   close,1
   eqw=eqw1
endif
;       
; -------------------------------------------------------------------------------
;       
if ident gt 0 then set_viewport,0.13,0.95,0.1,0.65
if vrot ge 0 and fwhm ge 0 then begin
;    
;  construct the input file for rotins
; 
   w0=(wstart+wend)*0.5
   if n_elements(vmac_rt) eq 0 then vmac_rt=0.  
   fwhm0=fwhm
   if n_elements(vmac_iso) gt 0 then fwhm0=fwhm+vmac_iso/2.997925e5*w0
   openw,1,'r.tmp'
   printf,1," 'fort.7'   'fort.17'    'fort.11' "
   printf,1,vrot,wdist,steprot
   printf,1,fwhm0,stepins,vmac_rt
   printf,1,wstart,wend,relative
   close,1
;    
;  run rotins
; 
   spawn,'/bin/rm -f out.tmp'       
   spawn,'./rotin3 <r.tmp > out.tmp'
endif
;       
; -------------------------------------------------------------------------------
; 
if n_elements(noread) eq 0 then begin 
   if n_elements(spect) ne 0 then begin
      a='/bin/cp -f '+spect+' fort.11'
      spawn,a
   endif
   spawn,'/bin/rm -f eq.tmp'
   spawn,'wc -l fort.11 > eq.tmp'
   openr,1,'eq.tmp'
   readf,1,npt
   close,1
   openr,1,'fort.11'
   sp=fltarr(2,npt)
   readf,1,sp
   close,1
endif
;       
; -------------------------------------------------------------------------------
;
ymax=1
if relative gt 0 and iplot eq 0 then begin
   ym=max(sp(1,*))
   if ym le 1 and ym ge 0.8 then ymax=1.2
   if ym gt 1.2 then ymax=ym
   ymax=ym>1.2
;   set_xy,0,0,0,ymax
endif
;     
; apply scale factor (scale) and radial velocity (rv) to the convolved spectrum
;  (if required)
;      
if n_elements(scale) eq 0 then fl=sp(1,*) else fl=sp(1,*)*scale
if n_elements(rv) eq 0 then wl=sp(0,*) else wl=sp(0,*)*(1.+rv/2.9977925e5)
if iplot le 0 then begin
;     
;  read and plot the observed spectrum (if required)
;     
   if n_elements(observ) eq 0 and noplot ne 1 then plot,wl,fl,_extra=e
   if n_elements(observ) gt 0 then begin
      observ=strtrim(string(observ),2)
      if observ ne '1' then begin
         close,1 & openr,1,observ
         i=0L
         wlobs=fltarr(3500000) & flobs=wlobs
         while not eof(1) do begin
            readf,1,wl0,fl0
            wlobs(i)=wl0
            flobs(i)=fl0
            i=i+1L
         endwhile
         nobs=i-1L
         wlobs=wlobs(0:nobs)
         flobs=flobs(0:nobs)
      endif
      if noplot ne 1 then begin
        plot,wlobs,flobs,xr=[wstart,wend],thick=3,_extra=e
        if iplot eq 0 then oplot,wl,fl
      endif
   endif
endif else begin
;  if iplot le 256 then oplot,wl,fl,color=iplot_extra=e else oplot,wl,fl,_extra=e
   oplot,wl,fl,_extra=e
endelse
;set_xy
close,1
;
; if required (ident > 0), do graphical identification
;
if ident gt 0 then begin
   if n_elements(extend) gt 0 then begin
      if iplot ge 0 then begin
         nln=n_elements(wl)
         wla=fltarr(nln)
         fla=wla
         for i=0,nln-1 do begin wla(i)=wl(i) & fla(i)=fl(i) & endfor
     endif
     if n_elements(observ) eq 1 then begin
        nobs=n_elements(wlobs)-1
        if iplot ge 0 then beyond=wl(nln-1) lt wlobs(0) or wl(0) gt wlobs(nobs-1)
        if iplot lt 0 then beyond=1
        if extend lt 0 then begin
           extend = -extend
           beyond=1
        endif
        nln=n_elements(wlobs)
        wla=fltarr(nln)
        fla=wla
        for i=0,nln-1 do begin wla(i)=wlobs(i) & fla(i)=flobs(i) & endfor
      endif
   endif
   ra=[wstart,wend]
   ewl=ident
   spawn,'/bin/rm -f f12'
   spawn,'cat fort.12 fort.14 | sort -n -k 3,3 > f12'
   lineid_select,'f12',wli,lid,wst,st,ew,ewlim=ewl,range=ra
   if n_elements(rv) eq 1 and n_elements(lidshift) ne 0 then $
      wli=wli*(1.+rv/2.9977925e5)
   lineid_annot,wla,fla,wli,ew,lid,wst,charsize=charsize,extend=extend
   set_viewport
endif
;
; save files (if parameter SAVE is set)
;
if n_elements(save) eq 1 then begin
   a='/bin/cp fort.7 '+save+".7"
   spawn,a
   a='/bin/cp fort.17 '+save+".17"
   spawn,a
   a='/bin/cp fort.11 '+save+".11"
   spawn,a
   if n_elements(nangles) gt 0 then begin
      a='/bin/cp fort.10 '+save+".10"
      spawn,a
   endif
endif
;
;delete link to fort.19 (line list)
;
if n_elements(linlist) eq 1 then begin
   if linlist ne 'fort.19' then begin
      spawn,'/bin/rm -f fort.19'
   endif
endif
;
;delete link to atomic data
;
if n_elements(atdata) gt 0 then begin
   spawn,'/bin/rm -f data'
endif
;
;delete link to fort.20; fort.25; fort.26 (line broadening)
;
;if n_elements(hydprf) eq 1 then begin
;   if hydprf ne 'fort.20' then begin
;     spawn,'/bin/rm -f fort.20'
;   endif
;endif
;if n_elements(he1prf) eq 1 then begin
;   if he1prf ne 'fort.25' then begin
;      spawn,'/bin/rm -f fort.21'
;   endif
;endif
;if n_elements(he2prf) eq 1 then begin
;   if he2prf ne 'fort.26' then begin
;      spawn,'/bin/rm -f fort.22'
;   endif
;endif
;
end







