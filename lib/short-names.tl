
(def a apply)
(def e even?)
(def f filter)
(def l list)
(def m map)
(def o odd?)
(def p partial)
(def r range)
(def z zip)

(def \ lambda)
(def : let)
(def ! not)
(def # length)
(def ~ reverse)
(def , concat)
(def } foldl)
(def { foldr)
(def . compose)

; ] is take if its first argument is an integer, take-while if
; it is a function (list or builtin)
(def ]
  (lambda (count-or-func seq)
    (if (same-type? count-or-func 0)
      (take count-or-func seq)
      (take-while count-or-func seq))))

; [ is drop if its first argument is an integer, drop-while if
; it is a function (list or builtin)
(def [
  (lambda (count-or-func seq)
    (if (same-type? count-or-func 0)
      (drop count-or-func seq)
      (drop-while count-or-func seq))))
