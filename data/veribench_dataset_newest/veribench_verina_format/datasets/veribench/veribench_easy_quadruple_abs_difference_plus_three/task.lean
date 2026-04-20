-- !benchmark @start import type=solution
import Mathlib
namespace QuadAbsDiff
-- !benchmark @end import

-- !benchmark @start solution_aux
/-- Compute the absolute difference of `a` and `b` manually. -/
def absDiff (a b : Nat) : Nat :=
  if a ≥ b then a - b else b - a
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def quadAbsDiffPlusThree_precond (a : Nat) (b : Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def quadAbsDiffPlusThree (a : Nat) (b : Nat) (h_precond : quadAbsDiffPlusThree_precond (a) (b)) : Nat :=
  -- !benchmark @start code
  4 * absDiff a b + 3
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def quadAbsDiffPlusThree_postcond (a : Nat) (b : Nat) (result : Nat)
    (h_precond : quadAbsDiffPlusThree_precond (a) (b)) : Prop :=
  -- !benchmark @start postcond
  (quadAbsDiffPlusThree (a) (b) h_precond = quadAbsDiffPlusThree (b) (a) (by simp)) ∧
    (3 ≤ quadAbsDiffPlusThree (a) (b) h_precond) ∧
    (quadAbsDiffPlusThree (0) (0) (by simp) = 3) ∧
    (quadAbsDiffPlusThree (a) (b) h_precond % 1 = 0) ∧
    (∀ x : Nat, quadAbsDiffPlusThree (x) (x) (by simp) = 3)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
/-- **Commutativity property**: Function is commutative in its arguments. -/
def commutativity_prop (a b : Nat) : Prop :=
  quadAbsDiffPlusThree a b (by simp) = quadAbsDiffPlusThree b a (by simp)

/-- **Commutativity theorem**: Function is commutative in its arguments. -/
@[simp] theorem commutativity_thm (a b : Nat) : commutativity_prop a b := by
  sorry

/-- **Lower bound property**: Result is always at least 3. -/
def lower_bound_prop (a b : Nat) : Prop :=
  3 ≤ quadAbsDiffPlusThree a b (by simp)

/-- **Lower bound theorem**: Result is always at least 3. -/
@[simp] theorem lower_bound_thm (a b : Nat) : lower_bound_prop a b := by
  sorry

/-- **Zero input property**: Both inputs zero gives result 3. -/
def zero_input_prop : Prop := quadAbsDiffPlusThree 0 0 (by simp) = 3

/-- **Zero input theorem**: Both inputs zero gives result 3. -/
@[simp] theorem zero_input_thm : zero_input_prop := by
  sorry

/-- **Mod one property**: Result modulo 1 is always 0. -/
def mod_one_prop (a b : Nat) : Prop :=
  quadAbsDiffPlusThree a b (by simp) % 1 = 0

/-- **Mod one theorem**: Result modulo 1 is always 0. -/
@[simp] theorem mod_one_thm (a b : Nat) : mod_one_prop a b := by
  sorry

/-- **Equal inputs property**: Equal inputs always give result 3. -/
def equal_inputs_prop (x : Nat) : Prop := quadAbsDiffPlusThree x x (by simp) = 3

/-- **Equal inputs theorem**: Equal inputs always give result 3. -/
@[simp] theorem equal_inputs_thm (x : Nat) : equal_inputs_prop x := by
  sorry
-- !benchmark @end proof_aux

theorem quadAbsDiffPlusThree_spec_satisfied (a : Nat) (b : Nat)
    (h_precond : quadAbsDiffPlusThree_precond (a) (b)) :
    quadAbsDiffPlusThree_postcond (a) (b) (quadAbsDiffPlusThree (a) (b) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof