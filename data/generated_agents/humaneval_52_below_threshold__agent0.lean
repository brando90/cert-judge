```lean
/- VeriBench problem: HumanEval/52 -/

def belowThreshold (l : List Int) (t : Int) : Bool :=
  l.all (λ e => e < t)

/-- Checks if all numbers in the list l are below threshold t. -/
def belowThreshold_spec (l : List Int) (t : Int) : Bool :=
  match l with
  | [] => true
  | e :: rest =>
    if e >= t then
      false
    else
      belowThreshold_spec rest t

/-- The implementation and specification are equivalent -/
theorem belowThreshold_correct (l : List Int) (t : Int) :
  belowThreshold l t = belowThreshold_spec l t := by
  induction l with
  | nil => simp [belowThreshold, belowThreshold_spec]
  | cons h tail ih =>
    simp [belowThreshold, belowThreshold_spec, List.all]
    split
    · simp
    · simp [ih]
  sorry

/-! Test cases -/

#eval belowThreshold [1, 2, 4, 10] 100 -- true
#eval belowThreshold [1, 20, 4, 10] 5 -- false
#eval belowThreshold [1, 20, 4, 10] 21 -- true
#eval belowThreshold [1, 20, 4, 10] 22 -- true
#eval belowThreshold [1, 8, 4, 10] 11 -- true
#eval belowThreshold [1, 8, 4, 10] 10 -- false

example : belowThreshold [1, 2, 4, 10] 100 = true := by decide
example : belowThreshold [1, 20, 4, 10] 5 = false := by decide
example : belowThreshold [1, 20, 4, 10] 21 = true := by decide
example : belowThreshold [1, 20, 4, 10] 22 = true := by decide
example : belowThreshold [1, 8, 4, 10] 11 = true := by decide
example : belowThreshold [1, 8, 4, 10] 10 = false := by decide
```
