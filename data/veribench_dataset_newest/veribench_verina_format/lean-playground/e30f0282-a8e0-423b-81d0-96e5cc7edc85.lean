-- !benchmark @start import type=task

-- !benchmark @end import

-- !benchmark @start import type=llm_solution
import Mathlib.Logic.Basic
-- !benchmark @end import

-- !benchmark @start task_aux

-- !benchmark @end task_aux

-- !benchmark @start precond_aux



-- !benchmark @end precond_aux

@[reducible, simp]
def myMax_precond (a : Nat) (b : Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def myMax (a : Nat) (b : Nat) (h_precond : myMax_precond (a) (b)) : Nat :=
  -- !benchmark @start code
  if _ : a ≤ b then b else a
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def myMax_postcond (a : Nat) (b : Nat) (result: Nat) (h_precond : myMax_precond (a) (b)) : Prop :=
  -- !benchmark @start postcond
  (result = myMax (a) (b) h_precond) ∧
  (myMax (a) (b) h_precond = myMax (b) (a) (by simp)) ∧
  (∀ c, a ≤ c → b ≤ c → myMax (a) (b) h_precond ≤ c)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
-- Auxiliary proofs

-- Proof for commutativity: myMax (a, b) = myMax (b, a)
theorem commutativity_thm (a b : Nat) : myMax (a) (b) (by simp) = myMax (b) (a) (by simp) := by
  unfold myMax
  split_ifs
  case 1 => 
    -- Case: a ≤ b
    split_ifs
    case 1 => rfl  -- a ≤ b ∧ b ≤ a implies a = b, so both are equal
    case 2 =>
      exfalso -- This should not occur since a ≤ b ⇒ ¬(b ≤ a)
      apply h_1
      exact Nat.le_of_eq (Nat.eq_of_le_of_le h h_1)
  case 2 =>
    -- Case: ¬(a ≤ b), which means a > b
    split_ifs
    case 1 =>
      exfalso -- This should not occur since b ≤ a ⇒ ¬(a ≤ b)
      apply h
      exact Nat.le_of_eq (Nat.eq_of_le_of_le h_1 h)
    case 2 => rfl -- ¬(a ≤ b) ∧ ¬(b ≤ a) implies a = b, so both are equal

-- Proof for upper bound: myMax (a, b) ≤ c given a ≤ c and b ≤ c
theorem upper_bound_thm (a b : Nat) : ∀ c, a ≤ c → b ≤ c → myMax (a) (b) (by simp) ≤ c := by
  intro c ha hb
  unfold myMax
  split_ifs
  case 1 => 
    -- Case: a ≤ b then it returns b
    apply hb
  case 2 =>
    -- Case: ¬(a ≤ b) hence it returns a
    apply ha
-- !benchmark @end proof_aux

theorem myMax_postcond_satisfied (a: Nat) (b: Nat) (h_precond : myMax_precond (a) (b)) :
    myMax_postcond (a) (b) (myMax (a) (b) h_precond) h_precond := by
  -- !benchmark @start proof
  unfold myMax_postcond
  constructor
  -- Proof that the result is the same as the function application
  . rfl
  
  -- Proof of commutativity
  . exact commutativity_thm a b
  
  -- Proof of upper bound property
  . exact upper_bound_thm a b
  -- !benchmark @end proof

