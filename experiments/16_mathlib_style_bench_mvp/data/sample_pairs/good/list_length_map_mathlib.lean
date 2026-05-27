import Mathlib

example {alpha beta : Type} (f : alpha -> beta) (xs : List alpha) :
    (xs.map f).length = xs.length := by
  simpa using List.length_map f xs
