import Mathlib

namespace MyStringLength


def myStringLength (s : String) : Nat :=
  s.length


def myStringLengthImp (s : String) : Nat :=
  Id.run (do
    let mut count : Nat := 0
    for _ in s.data do
      count := count + 1
    return count)

/-!
# Property Theorems
-/


# Correctness Theorem
-/



/-!
# Unit Tests
-/

/-- expected: 5 -/
example : myStringLength "hello" = 5 := by
  unfold myStringLength
  rfl

#eval myStringLength "hello" -- expected: 5

/-- expected: 0 (edge cases)-/
example : myStringLength "" = 0 := by
  unfold myStringLength
  rfl

#eval myStringLength "" -- expected: 0

/-- expected: 1 -/
example : myStringLength "!" = 1 := by
  unfold myStringLength
  rfl

#eval myStringLength "!" -- expected: 1

/-!
# Positive / Negative Test-Suite
-/

/-- positive: length of longer strings -/
example : myStringLength "Hello, World!" = 13 := by
  unfold myStringLength
  rfl

#eval myStringLength "Hello, World!" -- expected: 13

/-- positive: length with numbers and symbols -/
example : myStringLength "123!@#" = 6 := by
  unfold myStringLength
  rfl

#eval myStringLength "123!@#" -- expected: 6

/-- positive: length with spaces -/
example : myStringLength "a b c" = 5 := by
  unfold myStringLength
  rfl

#eval myStringLength "a b c" -- expected: 5

/-- negative: length should not be negative -/
example : ¬ (myStringLength "test" < 0) := by
  unfold myStringLength
  simp

#eval (decide (myStringLength "test" < 0)) -- expected: false

/-- negative: empty string should not have positive length -/
example : ¬ (myStringLength "" > 0) := by
  unfold myStringLength
  simp

#eval (decide (myStringLength "" > 0)) -- expected: false

/-!
# Positive / Negative Test-Suite
-/

/-- positive: maintains length computation -/
example : myStringLengthImp "test" = 4 := by
  unfold myStringLengthImp
  simp

#eval myStringLengthImp "test" -- expected: 4

/-- negative: should not be negative -/
example : ¬ (myStringLengthImp "abc" < 0) := by
  unfold myStringLengthImp
  simp

#eval (decide (myStringLengthImp "abc" < 0)) -- expected: false

/-- **Equivalence**: functional and imperative string length coincide. -/
private theorem count_chars_aux (cs : List Char) (acc : Nat) :
    Id.run (do
      let mut count : Nat := acc
      for _ in cs do
        count := count + 1
      return count) = acc + cs.length := by
  induction cs generalizing acc with
  | nil =>
      simp
  | cons c cs ih =>
      simpa [Nat.add_assoc, Nat.add_left_comm, Nat.add_comm] using ih (acc + 1)

theorem myStringLength_equivalence (s : String) :
  myStringLength s = myStringLengthImp s := by
  cases s with
  | mk data =>
      unfold myStringLength myStringLengthImp
      rw [count_chars_aux data 0]
      simp




end MyStringLength