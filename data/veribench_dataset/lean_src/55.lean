/-
# VeriBench – Fibonacci (HumanEval/55)

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

`fib n` returns the n‑th Fibonacci number with `fib 0 = 0`, `fib 1 = 1`.
-/

namespace Humaneval55_Fib

/-- Naive recursive Fibonacci. -/
def fib : Nat → Nat
  | 0       => 0
  | 1       => 1
  | n + 2   => fib (n + 1) + fib n

/-
# Tests
-/

/-- expected: 55 -/
example : fib 10 = 55 := by native_decide
#eval fib 10 -- expected: 55

/-- expected: 1 -/
example : fib 1 = 1 := by native_decide
#eval fib 1 -- expected: 1

/-- expected: 21 -/
example : fib 8 = 21 := by native_decide
#eval fib 8 -- expected: 21

/-- expected: 89 -/
example : fib 11 = 89 := by native_decide
#eval fib 11 -- expected: 89

/-- expected: 144 -/
example : fib 12 = 144 := by native_decide
#eval fib 12 -- expected: 144

/-
# Tests: Edge Cases
-/

/-- expected: 0 -/
example : fib 0 = 0 := by native_decide
#eval fib 0 -- expected: 0

/-- expected: 1 -/
example : fib 2 = 1 := by native_decide
#eval fib 2 -- expected: 1

/-
# Positive / Negative Test‑Suite
-/

/-- positive: fib 5 = 5 -/
example : fib 5 = 5 := by native_decide
#eval fib 5 -- expected: 5

/-- negative: fib 5 ≠ 6 -/
example : ¬ (fib 5 = 6) := by native_decide
#eval (decide (fib 5 = 6)) -- expected: false

/-
# Tests: Properties
-/

/-- Recurrence test: fib (0+2) = fib (0+1) + fib 0 -/
example : fib (0 + 2) = fib (0 + 1) + fib 0 := by native_decide
#eval (fib 2, fib 1 + fib 0) -- expected: (1, 1)

/-- Recurrence test: fib (5+2) = fib (5+1) + fib 5 -/
example : fib (5 + 2) = fib (5 + 1) + fib 5 := by native_decide
#eval (fib 7, fib 6 + fib 5) -- expected: (13, 13)

/-- Positivity test: n ≥ 1 → fib n ≥ 1, instantiated at n=5 -/
example : 1 ≤ 5 → 1 ≤ fib 5 := by native_decide
#eval (decide (1 ≤ 5 → 1 ≤ fib 5)) -- expected: true

/-- Monotone test: n ≥ 1 → fib n ≤ fib (n+1), instantiated at n=6 -/
example : 1 ≤ 6 → fib 6 ≤ fib (6 + 1) := by native_decide
#eval (decide (1 ≤ 6 → fib 6 ≤ fib (6 + 1))) -- expected: true

/-- Growth bound test: fib 10 ≤ 2^10 -/
example : fib 10 ≤ 2^10 := by native_decide
#eval (decide (fib 10 ≤ 2^10)) -- expected: true

/-
# Pre‑Condition
-/

/-- **Pre‑condition.** `n : Nat` (always non‑negative). -/
def Pre (n : Nat) : Prop := 0 ≤ n

/-
# Property Theorems
-/

/-- **Base‑case property**: `fib 0 = 0` and `fib 1 = 1`. -/
def base_cases_prop : Prop := (fib 0 = 0) ∧ (fib 1 = 1)

/-- **Base‑case theorem**. -/
@[simp] theorem base_cases_thm : base_cases_prop := sorry

/-- **Recurrence property**: `fib (n+2) = fib (n+1) + fib n`. -/
def recurrence_prop (n : Nat) : Prop := fib (n + 2) = fib (n + 1) + fib n

/-- **Recurrence theorem**. -/
@[simp] theorem recurrence_thm (n : Nat) : recurrence_prop n := sorry

/-- **Positivity property**: for `n ≥ 1`, `fib n ≥ 1`. -/
def positivity_prop (n : Nat) : Prop := 1 ≤ n → 1 ≤ fib n

/-- **Positivity theorem**. -/
@[simp] theorem positivity_thm (n : Nat) : positivity_prop n := sorry

/-- **Monotonicity property**: for `n ≥ 1`, `fib n ≤ fib (n+1)`. -/
def monotone_prop (n : Nat) : Prop := 1 ≤ n → fib n ≤ fib (n + 1)

/-- **Monotonicity theorem**. -/
@[simp] theorem monotone_thm (n : Nat) : monotone_prop n := sorry

/-- **Growth bound property**: `fib n ≤ 2^n` for all `n`. -/
def growth_bound_prop (n : Nat) : Prop := fib n ≤ 2^n

/-- **Growth bound theorem**. -/
@[simp] theorem growth_bound_thm (n : Nat) : growth_bound_prop n := sorry

/-- **Strict monotonicity property**: for `n ≥ 2`, `fib n < fib (n+1)`. -/
def strict_monotone_prop (n : Nat) : Prop := 2 ≤ n → fib n < fib (n + 1)

/-- **Strict monotonicity theorem**. -/
@[simp] theorem strict_monotone_thm (n : Nat) : strict_monotone_prop n := sorry

/-- **Special value property**: `fib 2 = 1`. -/
def special_fib2_prop : Prop := fib 2 = 1

/-- **Special value theorem**. -/
@[simp] theorem special_fib2_thm : special_fib2_prop := sorry

/-
# Post‑Condition  (conjunction of all desired properties)
-/

/-- **Post‑condition**: conjunction of the desired properties. -/
def Post_prop (n : Nat) : Prop :=
  base_cases_prop ∧
  (∀ m, recurrence_prop m) ∧
  positivity_prop n ∧
  monotone_prop n ∧
  growth_bound_prop n ∧
  strict_monotone_prop n ∧
  special_fib2_prop

/-
# Correctness Theorem
-/

/-- **Correctness theorem**: the pre‑condition implies the post‑condition. -/
theorem correctness_thm (n : Nat) (hPre : Pre n) : Post_prop n := sorry

/-
# Imperative Implementation
-/

/-- Iterative Fibonacci using two accumulators. -/
def fibImp (n : Nat) : Nat :=
  Id.run do
    let mut a : Nat := 0  -- F(0)
    let mut b : Nat := 1  -- F(1)
    -- For n steps, rotate (a, b) := (b, a+b)
    for _ in [:n] do
      let tmp := a + b
      a := b
      b := tmp
    return a

/-
# Imperative Tests
-/

/-- expected: 55 -/
example : fibImp 10 = 55 := by native_decide
#eval fibImp 10 -- expected: 55

/-- expected: 0 -/
example : fibImp 0 = 0 := by native_decide
#eval fibImp 0 -- expected: 0

/-- expected: 21 -/
example : fibImp 8 = 21 := by native_decide
#eval fibImp 8 -- expected: 21

/-- negative: fibImp 5 ≠ 6 -/
example : ¬ (fibImp 5 = 6) := by native_decide
#eval (decide (fibImp 5 = 6)) -- expected: false

/-- **Equivalence theorem**: functional and imperative Fibonacci coincide. -/
theorem equivalence_thm (n : Nat) : fib n = fibImp n := sorry

end Humaneval55_Fib
