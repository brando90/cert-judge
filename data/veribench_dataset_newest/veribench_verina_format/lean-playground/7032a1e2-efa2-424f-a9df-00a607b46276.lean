-- !benchmark @start import type=task

-- !benchmark @end import

-- !benchmark @start import type=llm_solution

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

-- !benchmark @end proof_aux

theorem myMax_postcond_satisfied (a: Nat) (b: Nat) (h_precond : myMax_precond (a) (b)) :
    myMax_postcond (a) (b) (myMax (a) (b) h_precond) h_precond := by
  -- !benchmark @start proof
  -- !benchmark @end proof

