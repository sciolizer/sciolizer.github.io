(let ((nums (list 0 1))
      (numclosures (list)))
  (progn
    (dolist (num nums)
      (push #'(lambda () num) numclosures))
    (dolist (numclosure numclosures)
      (format t "~a~%" (funcall numclosure)))))

; output from SBCL 1.0.11.debian
; 1
; 0
