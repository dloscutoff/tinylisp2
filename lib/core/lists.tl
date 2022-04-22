
(load utilities)

(def length
  (lambda (ls (accum 0))
    (if ls
      (length (tail ls) (inc accum))
      accum)))

(def nth
  (lambda (ls index)
    (if (same-type? index 0)
      (if (< index 0)
        nil
        (if index
          (nth (tail ls) (dec index))
          (head ls)))
      nil)))

(def _reverse
  (lambda (ls accum)
    (if ls
      (_reverse
        (tail ls)
        (cons (head ls) accum))
      accum)))

(def reverse
  (lambda (ls)
    (_reverse ls (empty ls))))

(def concat
  (lambda (ls-front ls-back)
    (_reverse (reverse ls-front) ls-back)))

(def take
  (lambda (count ls (accum))
    (if (both ls (< 0 count))
      (take
        (dec count)
        (tail ls)
        (cons (head ls) accum))
      (_reverse accum (empty ls)))))

(def drop
  (lambda (count ls)
    (if (both ls (< 0 count))
      (drop (dec count) (tail ls))
      ls)))

(def contains?
  (lambda (ls item)
    (if ls
      (if (= (head ls) item)
        1
        (contains? (tail ls) item))
      0)))

(def first-index
  (lambda (ls item (index 0))
    (if ls
      (if (= (head ls) item)
        index
        (first-index (tail ls) item (inc index)))
      nil)))

(def last-index
  (lambda (ls item (index 0) (final-index))
    (if ls
      (last-index
        (tail ls)
        item
        (inc index)
        (if (= (head ls) item)
          index
          final-index))
      final-index)))

(def quote-each
  (lambda (ls (accum))
    (if ls
      (quote-each
        (tail ls)
        (cons
          (list (q q) (head ls))
          accum))
      (reverse accum))))

(def count-up
  (lambda (lower upper (accum))
    (if (< upper lower)
      accum
      (count-up lower (dec upper) (cons upper accum)))))

(def count-down
  (lambda (upper lower (accum))
    (if (< upper lower)
      accum
      (count-down upper (inc lower) (cons lower accum)))))

(def 0to
  (macro ($num)
    (count-up 0 $num)))

(def 1to
  (macro ($num)
    (count-up 1 $num)))

(def to0
  (macro ($num)
    (count-down $num 0)))

(def to1
  (macro ($num)
    (count-down $num 1)))

(def range
  (lambda (num1 (num2))
    (if (nil? num2)
      (0to (dec num1))
      (count-up num1 (dec num2)))))

(def repeat
  (lambda (val count (accum))
    (if (< 0 count)
      (repeat val (dec count) (cons val accum))
      accum)))
