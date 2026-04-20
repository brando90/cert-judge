-- !benchmark @start import type=solution
import Mathlib
namespace ChangeBase
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def change_base_precond (x : Nat) (base : Nat) : Prop :=
  -- !benchmark @start precond
  base ≥ 2
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

partial def change_base (x : Nat) (base : Nat) (h_precond : change_base_precond (x) (base)) : String :=
  -- !benchmark @start code
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
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

-- !benchmark @start proof_aux
def zero_prop (b : Nat) : Prop := change_base (0) (b) (by sorry) = "0"

@[simp] theorem zero_thm (b : Nat) : zero_prop b := by
  sorry

def one_prop (b : Nat) : Prop := b > 1 → change_base (1) (b) (by sorry) = "1"

@[simp] theorem one_thm (b : Nat) : one_prop b := by
  sorry

def length_prop (x b : Nat) : Prop := b > 1 → (change_base (x) (b) (by sorry)).length ≥ 1

@[simp] theorem length_thm (x b : Nat) : length_prop x b := by
  sorry

def non_empty_prop (x b : Nat) : Prop := b ≥ 2 → change_base (x) (b) (by sorry) ≠ ""

@[simp] theorem non_empty_thm (x b : Nat) : non_empty_prop x b := by
  sorry
-- !benchmark @end proof_aux

@[reducible, simp]
def change_base_postcond (x : Nat) (base : Nat) (result : String)
    (h_precond : change_base_precond (x) (base)) : Prop :=
  -- !benchmark @start postcond
  (zero_prop base) ∧
    (one_prop base) ∧
    (length_prop x base) ∧
    (non_empty_prop x base)
  -- !benchmark @end postcond

theorem change_base_spec_satisfied (x : Nat) (base : Nat) (h_precond : change_base_precond (x) (base)) :
    change_base_postcond (x) (base) (change_base (x) (base) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof