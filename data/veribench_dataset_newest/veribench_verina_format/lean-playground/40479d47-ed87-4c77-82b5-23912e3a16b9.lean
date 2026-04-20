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



#print "<postcond_test_undecidable_plausible>6,0</postcond_test_undecidable_plausible>"

example : ¬(myMax_postcond (5) (3) (True) (by sorry)) := by
  unfold myMax_postcond
  simp_all! (config := { failIfUnchanged := false })
  simp (config := { failIfUnchanged := false }) [*]
  plausible ( config := { numInst := 1000, maxSize := 100, numRetries := 20, randomSeed := some 42})


#print "<postcond_test_undecidable_plausible>7,0</postcond_test_undecidable_plausible>"

example : ¬(myMax_postcond (2) (9) (True) (by sorry)) := by
  unfold myMax_postcond
  simp_all! (config := { failIfUnchanged := false })
  simp (config := { failIfUnchanged := false }) [*]
  plausible ( config := { numInst := 1000, maxSize := 100, numRetries := 20, randomSeed := some 42})

#print "###sound plausible end###"



#print "<postcond_test_undecidable_plausible>6,0</postcond_test_undecidable_plausible>"

example : (myMax_postcond (5) (3) (True) (by sorry)) := by
  unfold myMax_postcond
  simp_all! (config := { failIfUnchanged := false })
  simp (config := { failIfUnchanged := false }) [*]
  plausible ( config := { numInst := 1000, maxSize := 100, numRetries := 20, randomSeed := some 42})


#print "<postcond_test_undecidable_plausible>7,0</postcond_test_undecidable_plausible>"

example : (myMax_postcond (2) (9) (True) (by sorry)) := by
  unfold myMax_postcond
  simp_all! (config := { failIfUnchanged := false })
  simp (config := { failIfUnchanged := false }) [*]
  plausible ( config := { numInst := 1000, maxSize := 100, numRetries := 20, randomSeed := some 42})

#print "###sound plausible inverse end###"



#print "<postcond_test_undecidable_plausible>6</postcond_test_undecidable_plausible>"

example : (myMax_postcond (5) (3) (False) (by sorry)) := by
  unfold myMax_postcond
  simp_all! (config := { failIfUnchanged := false })
  simp (config := { failIfUnchanged := false }) [*]
  plausible ( config := { numInst := 1000, maxSize := 100, numRetries := 20, randomSeed := some 42})


#print "<postcond_test_undecidable_plausible>7</postcond_test_undecidable_plausible>"

example : (myMax_postcond (2) (9) (False) (by sorry)) := by
  unfold myMax_postcond
  simp_all! (config := { failIfUnchanged := false })
  simp (config := { failIfUnchanged := false }) [*]
  plausible ( config := { numInst := 1000, maxSize := 100, numRetries := 20, randomSeed := some 42})

#print "###complete plausible end###"



#print "<postcond_test_undecidable_plausible>6</postcond_test_undecidable_plausible>"

example : ¬(myMax_postcond (5) (3) (False) (by sorry)) := by
  unfold myMax_postcond
  simp_all! (config := { failIfUnchanged := false })
  simp (config := { failIfUnchanged := false }) [*]
  plausible ( config := { numInst := 1000, maxSize := 100, numRetries := 20, randomSeed := some 42})


#print "<postcond_test_undecidable_plausible>7</postcond_test_undecidable_plausible>"

example : ¬(myMax_postcond (2) (9) (False) (by sorry)) := by
  unfold myMax_postcond
  simp_all! (config := { failIfUnchanged := false })
  simp (config := { failIfUnchanged := false }) [*]
  plausible ( config := { numInst := 1000, maxSize := 100, numRetries := 20, randomSeed := some 42})
