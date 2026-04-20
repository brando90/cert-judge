-- !benchmark @start import type=task

-- !benchmark @end import

-- !benchmark @start import type=llm_solution
-- No additional imports needed
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
  s.length
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def myStringLength_postcond (s : String) (result: Nat) (h_precond : myStringLength_precond (s)) : Prop :=
  -- !benchmark @start postcond
  result = s.length
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem myStringLength_postcond_satisfied (s: String) (h_precond : myStringLength_precond (s)) :
    myStringLength_postcond (s) (myStringLength (s) h_precond) h_precond := by
  -- !benchmark @start proof
  unfold myStringLength_postcond
  unfold myStringLength
  simp
  -- !benchmark @end proof

