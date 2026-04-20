-- !benchmark @start import type=task

-- !benchmark @end import

-- !benchmark @start import type=llm_solution
-- No imports are necessary for this task.
-- !benchmark @end import

-- !benchmark @start task_aux

-- !benchmark @end task_aux

-- !benchmark @start precond_aux
-- No auxiliary definitions are needed for the precondition.
-- !benchmark @end precond_aux

@[reducible, simp]
def myMax_precond (a : Nat) (b : Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start postcond_aux
-- No auxiliary definitions are needed for the postcondition.
-- !benchmark @end postcond_aux

@[reducible, simp]
def myMax_postcond (a : Nat) (b : Nat) (result: Nat) (h_precond : myMax_precond (a) (b)) : Prop :=
  -- !benchmark @start postcond
  result = if a ≤ b then b else a
  -- !benchmark @end postcond

