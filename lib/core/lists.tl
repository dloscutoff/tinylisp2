
(load utilities)
(load metafunctions)

(def length
  (lambda (seq (accum 0))
    (if seq
      (length (tail seq) (inc accum))
      accum)))

(def nth
  (lambda (seq index)
    (if (same-type? index 0)
      (if (< index 0)
        nil
        (if index
          (nth (tail seq) (dec index))
          (head seq)))
      nil)))

(def reverse-onto
  (lambda (seq accum)
    (if seq
      (reverse-onto
        (tail seq)
        (cons (head seq) accum))
      accum)))

(def reverse
  (lambda (seq)
    (reverse-onto seq (empty seq))))

(def concat
  (lambda (seq-front seq-back)
    (reverse-onto (reverse seq-front) seq-back)))

(def take
  (lambda (count seq (accum))
    (if (both? seq (< 0 count))
      (take
        (dec count)
        (tail seq)
        (cons (head seq) accum))
      (reverse-onto accum (empty seq)))))

(def drop
  (lambda (count seq)
    (if (both? seq (< 0 count))
      (drop (dec count) (tail seq))
      seq)))

(def insert-end
  (lambda (seq val)
    (concat seq
      (cons val (empty seq)))))

(def contains?
  (lambda (seq item)
    (if seq
      (if (= (head seq) item)
        1
        (contains? (tail seq) item))
      0)))

(def first-index
  (lambda (seq item (index 0))
    (if seq
      (if (= (head seq) item)
        index
        (first-index (tail seq) item (inc index)))
      nil)))

(def last-index
  (lambda (seq item (index 0) (final-index))
    (if seq
      (last-index
        (tail seq)
        item
        (inc index)
        (if (= (head seq) item)
          index
          final-index))
      final-index)))

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
  (macro (&num)
    (count-up 0 &num)))

(def 1to
  (macro (&num)
    (count-up 1 &num)))

(def to0
  (macro (&num)
    (count-down &num 0)))

(def to1
  (macro (&num)
    (count-down &num 1)))

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

(def all?
  (lambda (seq)
    (if seq
      (if (head seq)
        (all? (tail seq))
        0)
      1)))

(def any?
  (lambda (seq)
    (if seq
      (if (head seq)
        1
        (any? (tail seq)))
      0)))

(def none?
  (macro (&seq)
    (not (any? &seq))))

; Transpose a list of sequences, stopping when one of them becomes empty
; For efficiency's sake, the algorithm performs a back-and-forth traversal,
; reversing the result sequences only when necessary
(def _zip
  (lambda (seqs (accum) (reversed 0))
    (if (both? seqs (all? seqs))
      (_zip
        (map-backwards tail seqs)
        (cons
          (if reversed
            (map-backwards head seqs)
            (map head seqs))
          accum)
        (not reversed))
      (reverse accum))))

(def zip
  (lambda seqs (_zip seqs)))

(def _unique
  (lambda (seq accum)
    (if seq
      (if (contains? accum (head seq))
        (_unique (tail seq) accum)
        (_unique
          (tail seq)
          (cons (head seq) accum)))
      (reverse accum))))

(def unique
  (lambda (seq)
    (_unique seq (empty seq))))
