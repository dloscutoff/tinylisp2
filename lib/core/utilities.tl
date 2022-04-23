
(def nil ())
(def nl "\n")

(def macro
  (q
    ((&params &expr)
      (q (&params &expr)))))

(def lambda
  (macro (&params &expr)
    (cons (locals)
      (q (&params &expr)))))

(def let
  (macro (&name &val &expr)
    ((lambda (&name) &expr)
      &val)))

(def list
  (lambda args args))

(def quote
  (macro (&expr)
    (q ((q q) &expr))))

(def disp
  (macro (&expr)
    (write (unparse &expr) nl)))

(def to-string
  (lambda (val)
    (if (same-type? val "")
      val
      (unparse val))))

(def empty
  (lambda (val)
    (if (same-type? val "")
      ""
      nil)))

(def dec (macro (&num) (- &num 1)))
(def inc (macro (&num) (+ &num 1)))

(def nil? (macro (&val) (= &val nil)))
(def empty-string? (macro (&val) (= &val "")))
(def zero? (macro (&val) (= &val 0)))
(def pos? (macro (&num) (< 0 &num)))
(def neg? (macro (&num) (< &num 0)))
(def even? (macro (&num) (= 0 (mod &num 2))))
(def odd? (macro (&num) (= 1 (mod &num 2))))

(def htail (macro (&seq) (head (tail &seq))))
(def ttail (macro (&seq) (tail (tail &seq))))

(def id (macro (&val) &val))
(def not (macro (&val) (if &val 0 1)))

(def both
  (macro (&cond1 &cond2)
    (if &cond1
      (if &cond2 1 0)
      0)))

(def either
  (lambda (&cond1 &cond2)
    (if &cond1
      1
      (if &cond2 1 0))))

(def neither
  (macro (&cond1 &cond2)
    (not (either &cond1 &cond2))))
