-- !benchmark @start import type=type=test
import Plausible
import Mathlib
-- !benchmark @end import

-- !benchmark @start import type=task

-- !benchmark @end import

-- !benchmark @start import type=llm_solution
-- No imports are needed for this task.
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



#print "<code_test>0</code_test>"

#guard myStringLength ("hello") (by sorry) == (5)

#print "<code_test>1</code_test>"

#guard myStringLength ("") (by sorry) == (0)

#print "<code_test>2</code_test>"

#guard myStringLength ("!") (by sorry) == (1)

#print "<code_test>3</code_test>"

#guard myStringLength ("Hello, World!") (by sorry) == (13)

#print "<code_test>4</code_test>"

#guard myStringLength ("123!@#") (by sorry) == (6)

#print "<code_test>5</code_test>"

#guard myStringLength ("a b c") (by sorry) == (5)