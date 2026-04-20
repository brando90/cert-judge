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

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def myStringLength_postcond (s : String) (result: Nat) (h_precond : myStringLength_precond (s)) : Prop :=
  -- !benchmark @start postcond
  result = s.length
  -- !benchmark @end postcond


#print "###test start###"


#print "###sound decidable end###"



#print "<postcond_test_decidable>0</postcond_test_decidable>"

#guard decide (myStringLength_postcond ("hello") (5) (by sorry))

#print "<postcond_test_decidable>1</postcond_test_decidable>"

#guard decide (myStringLength_postcond ("") (0) (by sorry))

#print "<postcond_test_decidable>2</postcond_test_decidable>"

#guard decide (myStringLength_postcond ("!") (1) (by sorry))

#print "<postcond_test_decidable>3</postcond_test_decidable>"

#guard decide (myStringLength_postcond ("Hello, World!") (13) (by sorry))

#print "<postcond_test_decidable>4</postcond_test_decidable>"

#guard decide (myStringLength_postcond ("123!@#") (6) (by sorry))

#print "<postcond_test_decidable>5</postcond_test_decidable>"

#guard decide (myStringLength_postcond ("a b c") (5) (by sorry))