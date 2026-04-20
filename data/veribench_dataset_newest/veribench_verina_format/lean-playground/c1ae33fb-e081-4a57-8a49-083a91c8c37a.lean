-- !benchmark @start import type=type=test
import Plausible
import Mathlib
-- !benchmark @end import

-- !benchmark @start import type=task

-- !benchmark @end import

-- !benchmark @start import type=llm_solution
-- No imports needed for this task
-- !benchmark @end import

-- !benchmark @start task_aux

-- !benchmark @end task_aux

-- !benchmark @start precond_aux


-- !benchmark @end precond_aux

@[reducible, simp]
def myAdd_precond (a : Nat) (b : Nat) : Prop :=
  -- !benchmark @start precond
  (0 ≤ a) ∧ (0 ≤ b)
  -- !benchmark @end precond

-- !benchmark @start code_aux
-- No auxiliary definitions needed
-- !benchmark @end code_aux

def myAdd (a : Nat) (b : Nat) (h_precond : myAdd_precond (a) (b)) : Nat :=
  -- !benchmark @start code
  a + b
  -- !benchmark @end code



#print "<code_test>0</code_test>"

#guard myAdd (1) (2) (by sorry) == (3)

#print "<code_test>1</code_test>"

#guard myAdd (0) (0) (by sorry) == (0)

#print "<code_test>2</code_test>"

#guard myAdd (2) (3) (by sorry) == (5)

#print "<code_test>3</code_test>"

#guard myAdd (7) (0) (by sorry) == (7)

#print "<code_test>4</code_test>"

#guard myAdd (4) (1) (by sorry) == (5)