
(load utilities)
(load lists)
(load metafunctions)

(def >
  (macro &args
    (eval
      (cons (q <)
        (reverse (q &args))))))

; Returns the absolute value of its argument
(def abs
  (lambda (num)
    (if (neg? num)
      (- num)
      num)))

; Returns the sign of its argument: -1 for negative, 1 for positive, 0 for zero
(def sign
  (lambda (num)
    (if (neg? num)
      -1
      (pos? num))))

; Returns the square of <num>
(def square
  (lambda (num) (* num num)))

(def _minimum
  (lambda (seq current-min)
    (if seq
      (_minimum (tail seq)
        (if (< (head seq) current-min)
          (head seq)
          current-min))
      current-min)))

; Returns the smallest number in a sequence, or nil if the sequence is empty
(def minimum
  (lambda (seq)
    (if seq
      (_minimum (tail seq) (head seq))
      nil)))

; Returns the smallest number of its arguments, or nil if there are no
; arguments
(def min
  (lambda nums (minimum nums)))

(def _maximum
  (lambda (seq current-max)
    (if seq
      (_maximum (tail seq)
        (if (< current-max (head seq))
          (head seq)
          current-max))
      current-max)))

; Returns the largest number in a sequence, or nil if the sequence is empty
(def maximum
  (lambda (seq)
    (if seq
      (_maximum (tail seq) (head seq))
      nil)))

; Returns the largest number of its arguments, or nil if there are no
; arguments
(def max
  (lambda nums (maximum nums)))

; Tests whether <divisor> divides <multiple> evenly
(def divides?
  (macro (&divisor &multiple)
    (zero? (mod &multiple &divisor))))

(def _prime?
  (lambda (num (divisor 2))
    (if (> (square divisor) num)
      1
      (if (divides? divisor num)
        0
        (_prime? num (inc divisor))))))

; Tests whether its argument is a prime number
; For numbers greater than 1, test if the number has any divisors in
; the half-open range [2, num)
; The only number less than 2 that is considered prime is -1
(def prime?
  (lambda (num)
    (if (> num 1)
      (_prime? num)
      (= num -1))))

(def _to-base
  (lambda (base num (accum))
    (if (pos? num)
      (_to-base base
        (/ num base)
        (cons (mod num base) accum))
      accum)))

(def to-base
  (lambda (base num)
    (if (pos? base)
      (if (= base 1)
        (repeat 1 num)
        (_to-base base num))
      nil)))

(def to-binary
  (macro (&num)
    (to-base 2 &num)))

(def to-digits
  (macro (&num)
    (to-base 10 &num)))

(def from-base
  (lambda (base digits (accum 0))
    (if digits
      (from-base base
        (tail digits)
        (+ (head digits) (* accum base)))
      accum)))

(def from-binary
  (macro (&num)
    (from-base 2 &num)))

(def from-digits
  (macro (&num)
    (from-base 10 &num)))
