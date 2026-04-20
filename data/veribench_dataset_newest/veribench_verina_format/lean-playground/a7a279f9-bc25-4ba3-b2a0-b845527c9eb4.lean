-- !benchmark @start import type=task

-- !benchmark @end import

-- !benchmark @start import type=llm_solution

-- !benchmark @end import

-- !benchmark @start task_aux

-- !benchmark @end task_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def myAdd_precond (a : Nat) (b : Nat) : Prop :=
  -- !benchmark @start precond
  true
  -- !benchmark @end precond

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def myAdd_postcond (a : Nat) (b : Nat) (result: Nat) (h_precond : myAdd_precond (a) (b)) : Prop :=
  -- !benchmark @start postcond
  result = a + b
  -- !benchmark @end postcond

