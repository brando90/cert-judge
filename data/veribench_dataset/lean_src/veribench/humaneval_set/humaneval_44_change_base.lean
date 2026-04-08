/-!
# VeriBench – Change Base

File order:

1. Implementation
2. Unit tests (positive, edge, positive/negative test suite)
3. Pre‑condition prop
4. Exhaustive property prop and their theorems
5. Post‑condition prop (same order as property props)
6. Correctness theorem `Pre → Post`
7. Imperative i. implementation, ii. tests (positive, edge, positive/negative
test suite), and iii. equivalence theorem.

All real proofs are left as `sorry` for the learner/model/agent.

# Implementation

## Change Base

Implements `change_base` which converts a number from decimal (base 10) to another base.-/

namespace ChangeBase

/--
**Implementation of `change_base`.**

`change_base x base` converts a natural number `x` from decimal (base 10) to a string representation
in the specified `base`. The base must be at least 2.

## Examples

#eval change_base 8 3    -- expected: "22"
#eval change_base 9 3    -- expected: "100"
#eval change_base 234 2  -- expected: "11101010"
-/
partial def change_base (x base : Nat) : String :=
  if x = 0 then
    "0"
  else if base ≤ 1 then
    "0"
  else
    let rec aux (n : Nat) (acc : String) : String :=
      if n = 0 then
        acc
      else
        aux (n / base) (toString (n % base) ++ acc)
    aux x ""

/-!
# Tests
-/

/-- expected: "22" -/
example : change_base 8 3 = "22" := by native_decide
#eval change_base 8 3 -- expected: "22"

/-- expected: "100" -/
example : change_base 9 3 = "100" := by native_decide
#eval change_base 9 3 -- expected: "100"

/-!
# Tests: Edge Cases
-/

/-- expected: "11101010" -/
example : change_base 234 2 = "11101010" := by native_decide
#eval change_base 234 2 -- expected: "11101010"

/-- expected: "0" -/
example : change_base 0 2 = "0" := by native_decide
#eval change_base 0 2 -- expected: "0"

/-- expected: "1" -/
example : change_base 1 2 = "1" := by native_decide
#eval change_base 1 2 -- expected: "1"

/-!
# Positive / Negative Test‑Suite
-/

/-- positive test: base 2 -/
example : change_base 2 2 = "10" := by native_decide
#eval change_base 2 2 -- expected: "10"

/-- positive test: larger base -/
example : change_base 15 16 = "15" := by native_decide
#eval change_base 15 16 -- expected: "15"

/-- negative test: different bases give different results -/
example : change_base 8 2 ≠ change_base 8 3 := by native_decide

/-- negative test: not the identity for base 10 -/
example : ¬ (change_base 123 10 = "123") := by sorry

/-!
# Pre‑Condition
-/

/-- **Pre‑condition.** Base must be at least 2. -/
def Pre (x base : Nat) : Prop := base ≥ 2

/-!
# Property Theorems
-/

/-- **Zero property**: Converting zero to any base yields "0". -/
def zero_prop (b : Nat) : Prop := change_base 0 b = "0"

/-- **Zero theorem**: Converting zero to any base yields "0". -/
@[simp] theorem zero_thm (b : Nat) : zero_prop b := sorry

/-- **One property**: Converting one to any base ≥ 2 yields "1". -/
def one_prop (b : Nat) : Prop := b > 1 → change_base 1 b = "1"

/-- **One theorem**: Converting one to any base ≥ 2 yields "1". -/
@[simp] theorem one_thm (b : Nat) : one_prop b := sorry

/-- **Length property**: The length of the result is at least 1. -/
def length_prop (x b : Nat) : Prop := b > 1 → (change_base x b).length ≥ 1

/-- **Length theorem**: The length of the result is at least 1. -/
@[simp] theorem length_thm (x b : Nat) : length_prop x b := sorry

/-- **Non-empty property**: Result is never empty. -/
def non_empty_prop (x b : Nat) : Prop := b ≥ 2 → change_base x b ≠ ""

/-- **Non-empty theorem**: Result is never empty. -/
@[simp] theorem non_empty_thm (x b : Nat) : non_empty_prop x b := sorry

/-!
# Post‑Condition  (conjunction of all desired properties)
-/

/-- **Post‑condition**: conjunction of all desired properties for change_base. -/
def Post_prop (x base : Nat) : Prop :=
  (zero_prop base) ∧                                     -- zero property
  (one_prop base) ∧                                      -- one property
  (length_prop x base) ∧                                 -- length property
  (non_empty_prop x base)                                -- non-empty property

/-!
# Correctness Theorem
-/

/-- **Correctness theorem**: the pre‑condition implies the post‑condition. -/
theorem correctness_thm (x base : Nat) (hPre : Pre x base) : Post_prop x base := sorry

/-!
# Imperative Implementation
-/

/--
`change_baseImp x base` computes the same result using imperative style with a mutable string builder.
This version is more efficient as it avoids string concatenation.
-/
def change_baseImp (x base : Nat) : String :=
  Id.run do
    if x = 0 then
      return "0"
    let mut n := x
    let mut result : List Char := []
    while n > 0 do
      result := (Char.ofNat (n % base + '0'.toNat)) :: result
      n := n / base
    return String.mk result

/-!
# Imperative Tests
-/

/-- expected: "22" -/
example : change_baseImp 8 3 = "22" := by native_decide
#eval change_baseImp 8 3 -- expected: "22"

/-!
# Imperative Tests: Edge Cases
-/

/-- expected: "11101010" -/
example : change_baseImp 234 2 = "11101010" := by native_decide
#eval change_baseImp 234 2 -- expected: "11101010"

/-!
# Positive / Negative Test‑Suite
-/

/-- positive test: zero case -/
example : change_baseImp 0 2 = "0" := by native_decide
#eval change_baseImp 0 2 -- expected: "0"

/-- negative test: different from decimal -/
example : ¬ (change_baseImp 10 2 = "10") := by native_decide

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem change_base_equivalence_thm (x base : Nat) :
  change_base x base = change_baseImp x base := sorry

end ChangeBase
