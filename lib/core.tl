
(load core/utilities)
(load core/lists)
(load core/metafunctions)

(def tinylisp
  (lambda ((version 1))
    (if (= version 1)
      (q awesome)
      (if (= version 2)
        (q awesomer)
        nil))))
