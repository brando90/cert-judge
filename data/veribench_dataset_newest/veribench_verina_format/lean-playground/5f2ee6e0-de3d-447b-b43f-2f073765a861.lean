-- !benchmark @start import type=task

-- !benchmark @end import

-- !benchmark @start import type=llm_solution

-- !benchmark @end import

-- !benchmark @start task_aux

-- !benchmark @end task_aux

-- !benchmark @start precond_aux


-- !benchmark @end precond_aux

@[reducible, simp]
def myStringLength_precond (s : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def myStringLength (s : String) (h_precond : myStringLength_precond (s)) : Nat :=
  -- !benchmark @start code
  -- !benchmark @end code

