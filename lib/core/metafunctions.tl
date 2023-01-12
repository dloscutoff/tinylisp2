
(load utilities)
(load lists)

(def quote-each
  (lambda (seq (accum))
    (if seq
      (quote-each
        (tail seq)
        (cons
          (list (q q) (head seq))
          accum))
      (reverse accum))))

(def apply
  (macro (&func &arglist)
    (eval
      (cons (q &func) (quote-each &arglist)))))

(def map
  (lambda (func seq (accum))
    (if seq
      (map func
        (tail seq)
        (cons
          (func (head seq))
          accum))
      (reverse accum))))

(def filter
  (lambda (func seq (accum))
    (if seq
      (filter func
        (tail seq)
        (if (func (head seq))
          (cons (head seq) accum)
          accum))
      (reverse-onto accum seq))))

(def filter-not
  (macro (&func &seq)
    (filter
      (lambda (val) (not (&func val)))
      &seq)))

(def take-while
  (lambda (func seq (accum))
    (if (both seq (func (head seq)))
      (take-while func
        (tail seq)
        (cons (head seq) accum))
      (reverse accum))))

(def drop-while
  (lambda (func seq)
    (if (both seq (func (head seq)))
      (drop-while func (tail seq))
      seq)))

(def foldl
  (lambda (func seq (accum))
    (if seq
      (foldl func
        (tail seq)
        (func accum (head seq)))
      accum)))

(def foldl1
  (lambda (func seq (default))
    (if seq
      (foldl func (tail seq) (head seq))
      default)))

(def _foldr
  (lambda (func seq accum)
    (if seq
      (_foldr func
        (tail seq)
        (func (head seq) accum))
    accum)))

(def foldr
  (lambda (func seq (accum))
    (_foldr func (reverse seq) accum)))

(def foldr1
  (lambda (func seq (default))
    (if seq
      (let reversed
        (reverse seq)
        (_foldr func (tail reversed) (head reversed)))
      default)))

; Composes functions together; for example, (compose f g h) returns a new
; function that passes its argument to h, the result to g, and that result
; to f--equivalent to (lambda (_arg) (f (g (h _arg))))
(def compose
  (macro &functions
    (eval
      (insert-end
        (q (lambda (_arg)))
        (foldr list
          (concat (q &functions) (q (_arg))))))))

; Takes a 2-argument function and returns a new function that does the same
; thing but takes its arguments in the opposite order
(def flip
  (macro (&func)
    (lambda (_arg1 _arg2)
      (&func _arg2 _arg1))))

; Takes a function and some number of arguments; returns a new variadic
; function that calls the original function with the specified arguments
; followed by the new function's arguments
; For example, (partial + 1) returns a function that adds 1 together
; with all its arguments--equivalent to (lambda args (apply + (cons 1 args)))
(def partial
  (macro &func-and-args
    (lambda remaining-args
      (eval
        (concat
          (q &func-and-args)
          (quote-each remaining-args))))))
