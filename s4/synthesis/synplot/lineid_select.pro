pro lineid_select,file,Wline,lineid,wstring,strength,eqw, $
                  ewlim=ewlim,n=n,range=range
;+
;			lineid_select
;
; procedure to extract the wave and ID's from the SYNSPEC output file
; input: file=name of file
; output:Wline = real*8 vector of wavelengths
;        lineid  = vector of identifications (string array)
;	 wstring = string vector of wavelengths
;	 strength = string line strength indicator
;        eqw      = approximate equivalent width
; optional keyword inputs:
;        ewlim = lower limit for approximate equivalent width
;                (default = 0)
;	 N = strength indicator (  0  1      2       3       4
;                               (' ','.' or '*' or '**' or '***')
;		(default n = 2)
;	 range = 2 element vector giving desired wavelength range
;		(default = [0,99999])
;-
;----------------------------------------------------------------------------
;
; print calling sequence
;
	if n_params(0) lt 1 then begin
		print,'CALLING SEQUENCE: lineid_select,file,Wline,lineid,'+ $
				'wstring,strength,eqw'

		print,'OPTIONAL KEYWORD PARAMETERS:'
                print,' EWLIM = limiting approx. equivalent width'
		print,'	RANGE = [wmin,wmax]		default=[0,99999]'
		print,'	N = minimum strength (0-4)	default=2'
		return
	end
;
; set keyword defaults
;
	if n_elements(N) eq 0 then N=2
        if n_elements(ewlim) eq 0 then ewlim=0
	if n_elements(range) eq 0 then range = [0,999999]
	wmin = range(0)
	wmax = range(1)
;
; open input file
;	
	close,1 & openr,1,file
;
; initialization for loop
;
	st = ''
	wline = dblarr(2000)
	wstring = strarr(2000)
	lineid = strarr(2000)
	strength = strarr(2000)
        eqw = fltarr(2000)
	nlines = 0
;
; loop on lines in the file
;
	while not eof(1) do begin
	    readf,1,st					;read string
	    st = strtrim(st,2)				;trim blanks
	    for i=0,1 do junk=gettok(st,' ')		;skip first 2 columns
	    wave = gettok(st,' ')			;get wavelength
	    w = double(wave)				;convert to r*8

	    if (w ge wmin) and (w le wmax) then begin	;within range?
		el = gettok(st,' ')			;element
		strput,el,strlowcase(strmid(el,1,1)),1	;make second character
							;  lower case
		ion = gettok(st,' ')
		for i=5,7 do junk = gettok(st,' ')	;skip columns 5-7
                ew = gettok(st,' ')
		str = strtrim(st,2)			;strength
		case str of				;decode strength
			''   : Nx=0
			'.'  : Nx=1
			'*'  : Nx=2
			'**' : Nx=3
			'***': Nx=4
			else : Nx=999			;unknown
		endcase
;
; add line to the list
;
		if Nx ge N and ew ge ewlim then begin
			wline(nlines) = w
			wstring(nlines) = wave + ' '
			lineid(nlines) =  el + ' ' + ion + ' '
			strength(nlines) = str
                        eqw(nlines) = ew
			nlines = nlines + 1
		endif
	    end
	end
;
; extract good part of the arrays
;
	if nlines gt 0 then begin
		wline = wline(0:nlines-1)
		wstring = wstring(0:nlines-1)
		lineid = lineid(0:nlines-1)
		strength = strength(0:nlines-1)
                eqw = eqw(0:nlines-1)
	    end else begin
		print,'LINEID_SELECT: No lines found for given range/N'
	end
	close,1
return
end
