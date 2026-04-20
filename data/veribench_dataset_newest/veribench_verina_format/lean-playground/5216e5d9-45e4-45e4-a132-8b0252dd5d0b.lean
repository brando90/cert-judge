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
def myStringLength_precond (s : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond


#print "###test start###"



#print "<precond_test_decidable>0</precond_test_decidable>"

#guard decide (myStringLength_precond ("hello"))

#print "<precond_test_decidable>1</precond_test_decidable>"

#guard decide (myStringLength_precond (""))

#print "<precond_test_decidable>2</precond_test_decidable>"

#guard decide (myStringLength_precond ("!"))

#print "<precond_test_decidable>3</precond_test_decidable>"

#guard decide (myStringLength_precond ("Hello, World!"))

#print "<precond_test_decidable>4</precond_test_decidable>"

#guard decide (myStringLength_precond ("123!@#"))

#print "<precond_test_decidable>5</precond_test_decidable>"

#guard decide (myStringLength_precond ("a b c"))
#print "###sound decidable end###"

