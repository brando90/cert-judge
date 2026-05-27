import Mathlib

example {alpha beta : Type} (f : alpha -> beta) (xs : List alpha) :
    (xs.map f).length = xs.length := by
  induction xs with
  | nil =>
      rfl
  | cons x xs ih =>
      simp [List.map, ih]
