
(load core/utilities)
(load core/lists)

(def tinylisp
  (lambda ((version 1))
    (if (= version 1)
      (q awesome)
      (if (= version 2)
        (q awesomer)
        nil))))
