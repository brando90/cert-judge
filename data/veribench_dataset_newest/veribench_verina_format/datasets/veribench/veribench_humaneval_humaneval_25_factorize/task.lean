-- !benchmark @start import type=solution
import Mathlib
namespace Factorize
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def factorize_precond (n : Nat) : Prop :=
  -- !benchmark @start precond
  n > 0
  -- !benchmark @end precond


-- !benchmark @start code_aux

-- !benchmark @end code_aux


def factorize (n : Nat) (h_precond : factorize_precond (n)) : List Nat :=
  -- !benchmark @start code
  let rec aux (n i : Nat) (acc : List Nat) (fuel : Nat) : List Nat :=
    match fuel with
    | 0 => acc
    | fuel + 1 =>
      if i * i > n then
        if n > 1 then n :: acc else acc
      else if n % i = 0 then
        aux (n / i) i (i :: acc) fuel
      else
        aux n (i + 1) acc fuel
  (aux n 2 [] n).reverse
  -- !benchmark @end code


-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux


@[reducible, simp]
def factorize_postcond (n : Nat) (result : List Nat) (h_precond : factorize_precond (n)) : Prop :=
  -- !benchmark @start postcond
  (n > 1 → result.foldl (· * ·) 1 = n) ∧
    (∀ p ∈ result, ∀ d, 1 < d → d < p → p % d ≠ 0) ∧
    (let factors := result
      ∀ i j, i < j → j < factors.length → factors[i]! ≤ factors[j]!) ∧
    (factorize (1) (by simp) = []) ∧
    (∀ p,
      ((p > 1 ∧ ∀ d, 1 < d → d < p → p % d ≠ 0) → factorize (p) (by sorry) = [p]))
  -- !benchmark @end postcond


-- !benchmark @start proof_aux

def product_prop (n : Nat) : Prop :=
  n > 1 → (factorize (n) (by sorry)).foldl (· * ·) 1 = n

@[simp] theorem product_thm (n : Nat) : product_prop n := by
  sorry

def prime_factors_prop (n : Nat) : Prop :=
  ∀ p ∈ factorize (n) (by sorry), ∀ d, 1 < d → d < p → p % d ≠ 0

@[simp] theorem prime_factors_thm (n : Nat) : prime_factors_prop n := by
  sorry

def ascending_order_prop (n : Nat) : Prop :=
  let factors := factorize (n) (by sorry)
  ∀ i j, i < j → j < factors.length → factors[i]! ≤ factors[j]!

@[simp] theorem ascending_order_thm (n : Nat) : ascending_order_prop n := by
  sorry

def one_factorization_prop : Prop :=
  factorize (1) (by simp) = []

@[simp] theorem one_factorization_thm : one_factorization_prop := by
  sorry

def prime_factorization_prop (p : Nat) : Prop :=
  (p > 1 ∧ ∀ d, 1 < d → d < p → p % d ≠ 0) → factorize (p) (by sorry) = [p]

@[simp] theorem prime_factorization_thm (p : Nat) : prime_factorization_prop p := by
  sorry

-- !benchmark @end proof_aux


theorem factorize_spec_satisfied (n : Nat) (h_precond : factorize_precond (n)) :
    factorize_postcond (n) (factorize (n) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof