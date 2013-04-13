function gettok,st,char
;+
; NAME:
;   GETTOK                                    
; PURPOSE:
;   Function to retrieve the first part of the string
;   until the character char is encountered.
;   (eg.  if st is 'abc=999' then gettok(st,'=') would return
;	'abc' and st would be left as 999)
;
;		gettok(st,char)
; INPUT:
;	st - string to get token from (on output token is removed)
;	char - character separating tokens
; OUTPUT:
;	taken value is returned 
;	!err is set to size of token
; HISTORY
;	version 1  by D. Lindler APR,86
;	10-JUN-1991 	JKF/ACC		- removed leading blanks.
;-
;----------------------------------------------------------------------
;
; if char is a blank, treat tabs as blanks
;
	tab='	'
	while strpos(st,tab) ge 0 do begin
		pos=strpos(st,tab)
		strput,st,' ',pos
	end

        st = strtrim(st,1)	; get rid of any leading blanks!

	;
	; find character in string
	;
	pos=strpos(st,char)
	if pos eq -1 then begin	;char not found?
		token=st
		st=''
		return,token
	endif

	;
	; extract token
	;
	token=strmid(st,0,pos)
	len=strlen(st)
	if pos eq (len-1) then st='' else st=strmid(st,pos+1,len-pos-1)

	;
	;  Return the result.
	;
	return,token
	end
