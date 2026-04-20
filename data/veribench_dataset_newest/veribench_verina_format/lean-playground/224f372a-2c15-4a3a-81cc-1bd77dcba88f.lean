-- !benchmark @start import type=type=test
import Plausible
import Mathlib
-- !benchmark @end import

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
  if a ≤ b then b else a
  -- !benchmark @end code



#print "<code_test>0</code_test>"

#guard myMax (7) (3) (by sorry) == (7)

#print "<code_test>1</code_test>"

#guard myMax (0) (0) (by sorry) == (0)

#print "<code_test>2</code_test>"

#guard myMax (5) (5) (by sorry) == (5)

#print "<code_test>3</code_test>"

#guard myMax (10) (3) (by sorry) == (10)

#print "<code_test>4</code_test>"

#guard myMax (2) (8) (by sorry) == (8)

#print "<code_test>5</code_test>"

#guard myMax (0) (7) (by sorry) == (7)

#print "<code_test>6</code_test>"

#guard myMax (5) (3) (by sorry) == (False)

#print "<code_test>7</code_test>"

#guard myMax (2) (9) (by sorry) == (False)