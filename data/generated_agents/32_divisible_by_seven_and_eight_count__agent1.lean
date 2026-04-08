import Lean
import Mathlib.Tactic
import Mathlib.Data.List.Basic
import Mathlib.Data.Int.Basic

/--
Count numbers divisible by both 7 and 8 in a list of integers.

Edge cases:
- Empty list returns 0.
-/
def count_div_by_7_and_8 (xs : List Int) : Nat :=
  xs.foldl (fun count x => if x % 7 = 0 && x % 8 = 0 then count + 1 else count) 0

/-- Predicate for being divisible by both 7 and 8 -/
def is_div_by_7_and_8 (x : Int) : Bool := x % 7 = 0 && x % 8 = 0

/-- Specification: count_div_by_7_and_8 counts elements divisible by both 7 and 8 -/
def count_div_by_7_and_8_spec (xs : List Int) : Nat :=
  xs.filter (fun x => is_div_by_7_and_8 x).length

/-- Test cases for count_div_by_7_and_8 -/
def count_div_by_7_and_8_test : IO Unit := do
  -- Basic test
  IO.println $ toString $ count_div_by_7_and_8 [56, 14, 28, 112] == 2
  -- Empty list returns 0
  IO.println $ toString $ count_div_by_7_and_8 [] == 0
  -- List with 0 (divisible by both 7 and 8)
  IO.println $ toString $ count_div_by_7_and_8 [0, 56, 84] == 2
  -- List with no elements divisible by both 7 and 8
  IO.println $ toString $ count_div_by_7_and_8 [1, 2, 3, 4] == 0

/-- Theorem stating that our implementation matches the specification -/
theorem count_div_by_7_and_8_correct (xs : List Int) : 
  count_div_by_7_and_8 xs = count_div_by_7_and_8_spec xs := by
  unfold count_div_by_7_and_8
  unfold count_div_by_7_and_8_spec
  induction xs with
  | nil => simp [List.foldl]
  | cons head tail ih =>
    simp [List.foldl]
    cases h : is_div_by_7_and_8 head with
    | true =>
      unfold is_div_by_7_and_8 at h
      simp [List.filter, h]
      rw [ih]
    | false =>
      unfold is_div_by_7_and_8 at h
      simp [List.filter, h]
      rw [ih]
  sorry

/-- Theorem: lcm(7,8) = 56, so a number is divisible by both 7 and 8 iff it's divisible by 56 -/
theorem div_by_7_and_8_iff_div_by_56 (x : Int) :
  (x % 7 = 0 && x % 8 = 0) ↔ x % 56 = 0 := by
  sorry
