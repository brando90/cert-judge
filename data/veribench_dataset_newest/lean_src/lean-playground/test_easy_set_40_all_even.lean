import Mathlib

open List
namespace AllEven


def allEven (xs : List Nat) : Bool :=
  xs.all (fun x => x % 2 = 0)


def allEvenImp (xs : List Nat) : Bool :=
  Id.run (do
    let mut result := true
    for x in xs do
      if x % 2 = 1 then
        result := false
    return result)

/-!
# Pre‑Condition
-/


def Pre (xs : List Nat) : Prop := True

/-!
# Property Theorems
-/


def empty_list_prop : Prop := allEven [] = true


def all_even_prop (xs : List Nat) : Prop :=
  allEven xs = true → ∀ x ∈ xs, x % 2 = 0


def single_even_prop (x : Nat) : Prop := x % 2 = 0 → allEven [x] = true


def contains_odd_prop (xs : List Nat) : Prop :=
  (∃ x ∈ xs, x % 2 = 1) → allEven xs = false


def boolean_result_prop (xs : List Nat) : Prop :=
  allEven xs = true ∨ allEven xs = false


# Post‑Condition  (conjunction of all desired properties)
-/


def Post_prop (xs : List Nat) : Prop :=
  (empty_list_prop) ∧                                    -- empty_list_prop
  (all_even_prop xs) ∧                                   -- all_even_prop
  (∀ x, single_even_prop x) ∧                            -- single_even_prop
  (contains_odd_prop xs) ∧                               -- contains_odd_prop
  (boolean_result_prop xs)                               -- boolean_result_prop

/-!
# Correctness Theorem
-/



/-!
# Tests
-/

/-- expected: true -/
example : allEven [2, 4, 6] = true := by native_decide
#eval allEven [2, 4, 6] -- expected: true

/-- expected: false -/
example : allEven [1, 2, 4] = false := by native_decide
#eval allEven [1, 2, 4] -- expected: false

/-!
# Tests: Edge Cases
-/

/-- expected: true -/
example : allEven [] = true := by native_decide
#eval allEven [] -- expected: true

/-- expected: true -/
example : allEven [0] = true := by native_decide
#eval allEven [0] -- expected: true

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: all even numbers -/
example : allEven [2, 8, 10] = true := by native_decide
#eval allEven [2, 8, 10] -- expected: true

/-- positive: empty list is vacuously true -/
example : allEven [] = true := by native_decide
#eval allEven [] -- expected: true

/-- negative: contains odd number -/
example : ¬ (allEven [1, 2, 4] = true) := by native_decide
#eval (decide (allEven [1, 2, 4] = true)) -- expected: false

/-- negative: single odd number -/
example : ¬ (allEven [1] = true) := by native_decide
#eval (decide (allEven [1] = true)) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: single even -/
example : allEvenImp [0] = true := by native_decide
#eval allEvenImp [0] -- expected: true

/-- negative: single odd -/
example : ¬ (allEvenImp [1] = true) := by native_decide
#eval (decide (allEvenImp [1] = true)) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
private theorem allEvenImp_false_aux (xs : List Nat) :
    Id.run (do
      let mut result := false
      for x in xs do
        if x % 2 = 1 then
          result := false
      return result) = false := by
  induction xs with
  | nil =>
      simp
  | cons x xs ih =>
      by_cases h : x % 2 = 1
      · simpa [h] using ih
      · simpa [h] using ih

theorem allEven_equivalence_thm (xs : List Nat) :
  allEven xs = allEvenImp xs := by
  induction xs with
  | nil =>
      simp [allEven, allEvenImp]
  | cons x xs ih =>
      by_cases h : x % 2 = 0
      · have h1 : x % 2 ≠ 1 := by
          omega
        simpa [allEven, allEvenImp, h, h1] using ih
      · have h1 : x % 2 = 1 := by
          omega
        simpa [allEven, allEvenImp, h1] using allEvenImp_false_aux xs




end AllEven