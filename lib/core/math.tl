
(load utilities)
(load lists)
(load metafunctions)

; Returns the absolute value of its argument
(def abs
  (lambda (num)
    (if (< num 0)
      (- num)
      num)))

; Returns the sign of its argument
(def sign
  (lambda (num)
    (if (< num 0)
      -1
      (if (= 0 num) 0 1))))

; Tests whether <divisor> divides <multiple> evenly
(def divides?
  (macro (&divisor &multiple)
    (= 0 (mod &multiple &divisor))))

; Returns the square of <num>
(def square
  (lambda (num) (* num num)))

(def _to-base
  (lambda (base num (accum))
    (if (< 0 num)
      (_to-base base
        (/ num base)
        (cons (mod num base) accum))
      accum)))

(def to-base
  (lambda (base num)
    (if (< 0 base)
      (if (= base 1)
        (repeat 1 num)
        (_to-base base num))
      nil)))

(def from-base
  (lambda (base digits (accum 0))
    (if digits
      (from-base base
        (tail digits)
        (+ (head digits) (* accum base)))
      accum)))

(def >
  (macro &args
    (apply <
      (reverse
        (map eval (q &args))))))
