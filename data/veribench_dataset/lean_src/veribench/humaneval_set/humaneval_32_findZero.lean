/-!
# VeriBench – Find Zero

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

## Find Zero

Implements `find_zero`, which finds a root of a polynomial using binary search method within a given bracket.-/

namespace PolynomialRoot

/-- Small epsilon value for float comparisons -/
def epsilon : Float := 1e-10

/--
Evaluates a polynomial at a given point x.

Given a list of coefficients [a₀, a₁, ..., aₙ], evaluates:
a₀ + a₁x + a₂x² + ... + aₙxⁿ
-/
def poly (xs : List Float) (x : Float) : Float :=
  let rec eval_at (i : Nat) (acc : Float) : Float :=
    match i with
    | 0 => acc
    | n + 1 =>
      match xs[n]? with
      | none => acc
      | some coeff => eval_at n (acc + coeff * (x ^ n.toFloat))
  eval_at xs.length 0

/--
**Implementation of `find_zero`.**

`find_zero xs a b fuel` finds a root of a polynomial using binary search method within the bracket [a, b].
Returns an x such that poly(x) ≈ 0. Uses binary search for a maximum of `fuel` iterations.

## Examples

#eval find_zero [1.0, 2.0] (-1.0) 0.0 100 -- expected: close to -0.5 (root of 1 + 2x)
#eval find_zero [-6.0, 11.0, -6.0, 1.0] 0.0 2.0 100 -- expected: close to 1.0 (root of (x-1)(x-2)(x-3))
-/
def find_zero (xs : List Float) (a b : Float) (fuel : Nat) : Float :=
  match fuel with
  | 0 => (a + b) / 2
  | fuel + 1 =>
    let mid := (a + b) / 2
    let f_mid := poly xs mid
    if Float.abs f_mid < epsilon then
      mid
    else if poly xs a * f_mid ≤ 0 then
      find_zero xs a mid fuel
    else
      find_zero xs mid b fuel

/-!
# Tests
-/

/-- expected: close to -0.5 -/
example : Float.abs (find_zero [1.0, 2.0] (-1.0) 0.0 100 + 0.5) < 0.01 := by sorry
#eval find_zero [1.0, 2.0] (-1.0) 0.0 100 -- expected: close to -0.5

/-- expected: close to 1.0 -/
example : Float.abs (find_zero [-6.0, 11.0, -6.0, 1.0] 0.0 2.0 100 - 1.0) < 0.01 := by sorry
#eval find_zero [-6.0, 11.0, -6.0, 1.0] 0.0 2.0 100 -- expected: close to 1.0

/-!
# Tests: Edge Cases
-/

/-- expected: close to 0.0 -/
example : Float.abs (find_zero [0.0, 1.0] (-1.0) 1.0 100) < 0.01 := by sorry
#eval find_zero [0.0, 1.0] (-1.0) 1.0 100 -- expected: close to 0.0

/-- expected: close to 2.0 -/
example : Float.abs (find_zero [4.0, -4.0, 1.0] 1.0 3.0 100 - 2.0) < 0.01 := by sorry
#eval find_zero [4.0, -4.0, 1.0] 1.0 3.0 100 -- expected: close to 2.0

/-!
# Positive / Negative Test‑Suite
-/

/-- positive test: linear polynomial -/
example : Float.abs (find_zero [3.0, -1.0] 0.0 4.0 100 - 3.0) < 0.01 := by sorry
#eval find_zero [3.0, -1.0] 0.0 4.0 100 -- expected: close to 3.0

/-- positive test: quadratic polynomial -/
example : Float.abs (find_zero [-1.0, 0.0, 1.0] 0.0 2.0 100 - 1.0) < 0.01 := by sorry
#eval find_zero [-1.0, 0.0, 1.0] 0.0 2.0 100 -- expected: close to 1.0

/-- negative test: result is not exact zero (floating point) -/
example : ¬ (find_zero [1.0, 2.0] (-1.0) 0.0 100 = 0.0) := by sorry
-- Note: removed #eval decide due to Decidable instance issues with Float equality

/-- negative test: different polynomials give different roots -/
example : ¬ (find_zero [1.0, 2.0] (-1.0) 0.0 100 = find_zero [2.0, 1.0] (-2.0) 0.0 100) := by sorry
-- Note: removed #eval decide due to Decidable instance issues with Float equality

/-!
# Pre‑Condition
-/

/-- **Pre‑condition.** Polynomial must have at least one coefficient, and the bracket [a, b] must contain a root. -/
def Pre (xs : List Float) (a b : Float) : Prop :=
  xs ≠ [] ∧ a < b ∧ poly xs a * poly xs b ≤ 0

/-!
# Property Theorems
-/

/-- **Root property**: The result is approximately a root of the polynomial. -/
def root_prop (xs : List Float) (a b : Float) (fuel : Nat) : Prop :=
  Float.abs (poly xs (find_zero xs a b fuel)) < epsilon

/-- **Root theorem**: The result is approximately a root of the polynomial. -/
@[simp] theorem root_thm (xs : List Float) (a b : Float) (fuel : Nat) : root_prop xs a b fuel := sorry

/-- **Bracket property**: The result lies within the given bracket. -/
def bracket_prop (xs : List Float) (a b : Float) (fuel : Nat) : Prop :=
  a ≤ find_zero xs a b fuel ∧ find_zero xs a b fuel ≤ b

/-- **Bracket theorem**: The result lies within the given bracket. -/
@[simp] theorem bracket_thm (xs : List Float) (a b : Float) (fuel : Nat) : bracket_prop xs a b fuel := sorry

/-- **Polynomial evaluation property**: poly evaluates polynomials correctly. -/
def poly_eval_prop (xs : List Float) (x : Float) : Prop :=
  poly xs x = (xs.mapIdx (fun i c => c * (x ^ i.toFloat))).sum

/-- **Polynomial evaluation theorem**: poly evaluates polynomials correctly. -/
@[simp] theorem poly_eval_thm (xs : List Float) (x : Float) : poly_eval_prop xs x := sorry

/-- **Deterministic property**: Same inputs give the same root. -/
def deterministic_prop (xs : List Float) (a b : Float) (fuel : Nat) : Prop :=
  find_zero xs a b fuel = find_zero xs a b fuel

/-- **Deterministic theorem**: Same inputs give the same root. -/
@[simp] theorem deterministic_thm (xs : List Float) (a b : Float) (fuel : Nat) : deterministic_prop xs a b fuel := sorry

/-!
# Post‑Condition  (conjunction of all desired properties)
-/

/-- **Post‑condition**: conjunction of all desired properties for find_zero. -/
def Post_prop (xs : List Float) (a b : Float) (fuel : Nat) : Prop :=
  (root_prop xs a b fuel) ∧                              -- root property
  (bracket_prop xs a b fuel) ∧                           -- bracket property
  (∀ x, poly_eval_prop xs x) ∧                           -- polynomial evaluation property
  (deterministic_prop xs a b fuel)                       -- deterministic property

/-!
# Correctness Theorem
-/

/-- **Correctness theorem**: the pre‑condition implies the post‑condition. -/
theorem correctness_thm (xs : List Float) (a b : Float) (fuel : Nat) (hPre : Pre xs a b) : Post_prop xs a b fuel := sorry

/-!
# Imperative Implementation
-/

/--
`find_zeroImp xs a b fuel` computes the same result using imperative style with explicit loops.
-/
def find_zeroImp (xs : List Float) (a b : Float) (fuel : Nat) : Float :=
  Id.run do
    let mut left := a
    let mut right := b
    let mut result := (left + right) / 2

    for _ in [1:fuel+1] do
      let mid := (left + right) / 2
      let f_mid := poly xs mid
      if Float.abs f_mid < epsilon then
        result := mid
        break
      if poly xs left * f_mid ≤ 0 then
        right := mid
      else
        left := mid
      result := mid

    return result

/-!
# Imperative Tests
-/

/-- expected: close to -0.5 -/
example : Float.abs (find_zeroImp [1.0, 2.0] (-1.0) 0.0 100 + 0.5) < 0.01 := by sorry
#eval find_zeroImp [1.0, 2.0] (-1.0) 0.0 100 -- expected: close to -0.5

/-!
# Imperative Tests: Edge Cases
-/

/-- expected: close to 1.0 -/
example : Float.abs (find_zeroImp [-6.0, 11.0, -6.0, 1.0] 0.0 2.0 100 - 1.0) < 0.01 := by sorry
#eval find_zeroImp [-6.0, 11.0, -6.0, 1.0] 0.0 2.0 100 -- expected: close to 1.0

/-!
# Positive / Negative Test‑Suite
-/

/-- positive test: finds root -/
example : Float.abs (find_zeroImp [2.0, -1.0] 0.0 4.0 100 - 2.0) < 0.01 := by sorry
#eval find_zeroImp [2.0, -1.0] 0.0 4.0 100 -- expected: close to 2.0

/-- negative test: not exactly zero due to floating point -/
example : ¬ (find_zeroImp [1.0, 1.0] (-2.0) 0.0 100 = 0.0) := by sorry
-- Note: removed #eval decide due to Decidable instance issues with Float equality

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem find_zero_equivalence_thm (xs : List Float) (a b : Float) (fuel : Nat) :
  Float.abs (find_zero xs a b fuel - find_zeroImp xs a b fuel) < epsilon := sorry

end PolynomialRoot
