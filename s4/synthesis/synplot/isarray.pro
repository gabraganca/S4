FUNCTION ISARRAY,A
;+    
; Name: 
;     ISARRAY
; PURPOSE: 
;     Determine if arg is an array.
; CALLING SEQUENCE: 
;     I = ISARRAY(A)
; Inputs: 
;     A = variable to test.
; OUTPUTS: 
;     I = function result. 1 if A is an array, else 0.
; MODIFICATION HISTORY: 
;    R. Sterner           20 Mar, 1986.
;-
S = SIZE(A)
RETURN, S(0) NE 0
END
