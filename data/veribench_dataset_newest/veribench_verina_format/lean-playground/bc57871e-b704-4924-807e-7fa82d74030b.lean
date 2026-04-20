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

-- !benchmark @start postcond_aux
-- Auxiliary definitions not needed for postcondition
-- !benchmark @end postcond_aux

@[reducible, simp]
def myMax_postcond (a : Nat) (b : Nat) (result: Nat) (h_precond : myMax_precond (a) (b)) : Prop :=
  -- !benchmark @start postcond
  result = a ∨ result = b ∧ result = (if a ≤ b then b else a)
  -- !benchmark @end postcond


#print "###test start###"



#print "<postcond_test_decidable>6,0</postcond_test_decidable>"

#guard decide (¬ (myMax_postcond (5) (3) (True) (by sorry)))

#print "<postcond_test_decidable>7,0</postcond_test_decidable>"

#guard decide (¬ (myMax_postcond (2) (9) (True) (by sorry)))
#print "###sound decidable end###"



#print "<postcond_test_decidable>0</postcond_test_decidable>"

#guard decide (myMax_postcond (7) (3) (7) (by sorry))

#print "<postcond_test_decidable>1</postcond_test_decidable>"

#guard decide (myMax_postcond (0) (0) (0) (by sorry))

#print "<postcond_test_decidable>2</postcond_test_decidable>"

#guard decide (myMax_postcond (5) (5) (5) (by sorry))

#print "<postcond_test_decidable>3</postcond_test_decidable>"

#guard decide (myMax_postcond (10) (3) (10) (by sorry))

#print "<postcond_test_decidable>4</postcond_test_decidable>"

#guard decide (myMax_postcond (2) (8) (8) (by sorry))

#print "<postcond_test_decidable>5</postcond_test_decidable>"

#guard decide (myMax_postcond (0) (7) (7) (by sorry))

#print "<postcond_test_decidable>6</postcond_test_decidable>"

#guard decide (myMax_postcond (5) (3) (False) (by sorry))

#print "<postcond_test_decidable>7</postcond_test_decidable>"

#guard decide (myMax_postcond (2) (9) (False) (by sorry))