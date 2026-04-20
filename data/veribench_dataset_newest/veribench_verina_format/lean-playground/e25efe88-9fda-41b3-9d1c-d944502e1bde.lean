-- !benchmark @start import type=task

-- !benchmark @end import

-- !benchmark @start import type=llm_solution
import Mathlib.Data.Nat.Basic
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
def commutativity_prop (a b : Nat) : Prop := myMax (a) (b) (by simp) = myMax (b) (a) (by simp)

theorem commutativity_thm (a b : Nat) : commutativity_prop a b := by
  rw [commutativity_prop]
  dsimp [myMax]
  split_ifs
  · apply Nat.le_antisymm
    · assumption
    · apply Nat.le_trans
      · apply Nat.le_refl
      · assumption
  · split_ifs
    · reflexivity
    · apply Nat.le_antisymm
      · apply Nat.le_trans
        · apply Nat.le_refl
        · assumption
      · assumption

def upper_bound_prop (a b : Nat) : Prop :=
  ∀ c, a ≤ c → b ≤ c → myMax (a) (b) (by simp) ≤ c

theorem upper_bound_thm (a b : Nat) : upper_bound_prop a b := by
  rw [upper_bound_prop]
  dsimp [myMax]
  split_ifs
  · intros c hac hbc
    assumption
  · intros c hac hbc
    assumption
-- !benchmark @end proof_aux

theorem myMax_postcond_satisfied (a: Nat) (b: Nat) (h_precond : myMax_precond (a) (b)) :
    myMax_postcond (a) (b) (myMax (a) (b) h_precond) h_precond := by
  -- !benchmark @start proof
  unfold myMax_postcond
  
  -- Show result = myMax a b h_precond
  apply And.intro
  - unfold myMax
    split_ifs
    · rfl
    · rfl
  
  -- Show myMax a b h_precond = myMax b a _
  apply And.intro
  - apply commutativity_thm
  
  -- Show ∀ c, a ≤ c → b ≤ c → result ≤ c
  - apply upper_bound_thm
  -- !benchmark @end proof

