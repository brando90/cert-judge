```lean
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.LibrarySearch
import Mathlib.Analysis.SpecialFunctions.Pow.Real

namespace HumanEval32

/-- Evaluates polynomial with coefficients xs at point x. -/
def poly (xs : List Float) (x : Float) : Float :=
  xs.enum.foldl (fun acc (i, coeff) => acc + coeff * x ^ i.toFloat) 0.0

/-- 
  Find a zero of a polynomial with coefficients xs.
  This function only returns one zero point, even if there are many.
  It only takes lists xs having an even number of coefficients
  and the largest non-zero coefficient, as this guarantees a solution.
-/
def find_zero (xs : List Float) : Float :=
  let rec bisect (begin end : Float) : Float :=
    if end - begin ≤ 1e-10 then
      begin
    else
      let center := (begin + end) / 2.0
      if poly xs center * poly xs begin > 0 then
        bisect center end
      else
        bisect begin center
  
  let rec expand_range (begin end : Float) : Float × Float :=
    if poly xs begin * poly xs end ≤ 0 then
      (begin, end)
    else
      expand_range (begin * 2.0) (end * 2.0)
  
  let (begin, end) := expand_range (-1.0) (1.0)
  bisect begin end

/-- Predicate that checks if a list has an even number of elements -/
def has_even_length (xs : List α) : Prop :=
  xs.length % 2 = 0

/-- Predicate that checks if the largest coefficient is non-zero -/
def has_nonzero_largest_coeff (xs : List Float) : Prop :=
  xs.length > 0 → xs.getLast! ≠ 0.0

/-- Predicate that checks if the polynomial has a zero in the real domain -/
def has_zero (xs : List Float) : Prop :=
  ∃ x : Float, poly xs x = 0.0

/-- Precondition for find_zero -/
def find_zero_pre (xs : List Float) : Prop :=
  has_even_length xs ∧ has_nonzero_largest_coeff xs

/-- Postcondition for find_zero -/
def find_zero_post (xs : List Float) (result : Float) : Prop :=
  |poly xs result| < 1e-4

theorem find_zero_correct (xs : List Float) (h : find_zero_pre xs) : 
  find_zero_post xs (find_zero xs) := by
  sorry

/-- Test cases for poly and find_zero -/
def test : IO Unit := do
  -- Test poly
  let test1 := poly [1.0, 2.0] 3.0
  IO.println s!"poly [1.0, 2.0] 3.0 = {test1}"
  assert! test1 == 7.0
  
  let test2 := poly [1.0, 2.0, 3.0] 2.0
  IO.println s!"poly [1.0, 2.0, 3.0] 2.0 = {test2}"
  assert! test2 == 17.0
  
  -- Test find_zero
  let zero1 := find_zero [1.0, 2.0]
  IO.println s!"find_zero [1.0, 2.0] = {zero1}"
  assert! |poly [1.0, 2.0] zero1| < 1e-4
  
  let zero2 := find_zero [-6.0, 11.0, -6.0, 1.0]
  IO.println s!"find_zero [-6.0, 11.0, -6.0, 1.0] = {zero2}"
  assert! |poly [-6.0, 11.0, -6.0, 1.0] zero2| < 1e-4
  
  IO.println "All tests passed!"

end HumanEval32
```
