-- !benchmark @start import type=type=test
import Plausible
import Mathlib
-- !benchmark @end import

-- !benchmark @start import type=task

-- !benchmark @end import

-- !benchmark @start import type=llm_solution
-- Import not needed
-- !benchmark @end import

-- !benchmark @start task_aux

-- !benchmark @end task_aux

-- !benchmark @start precond_aux
-- Auxiliary definitions not needed for precondition
-- !benchmark @end precond_aux

@[reducible, simp]
def myMax_precond (a : Nat) (b : Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond


#print "###test start###"



#print "<precond_test_decidable>0</precond_test_decidable>"

#guard decide (myMax_precond (7) (3))

#print "<precond_test_decidable>1</precond_test_decidable>"

#guard decide (myMax_precond (0) (0))

#print "<precond_test_decidable>2</precond_test_decidable>"

#guard decide (myMax_precond (5) (5))

#print "<precond_test_decidable>3</precond_test_decidable>"

#guard decide (myMax_precond (10) (3))

#print "<precond_test_decidable>4</precond_test_decidable>"

#guard decide (myMax_precond (2) (8))

#print "<precond_test_decidable>5</precond_test_decidable>"

#guard decide (myMax_precond (0) (7))

#print "<precond_test_decidable>6</precond_test_decidable>"

#guard decide (myMax_precond (5) (3))

#print "<precond_test_decidable>7</precond_test_decidable>"

#guard decide (myMax_precond (2) (9))
#print "###sound decidable end###"

