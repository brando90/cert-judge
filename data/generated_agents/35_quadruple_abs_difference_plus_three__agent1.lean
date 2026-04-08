import Mathlib.Data.Int.Basic

/--
Return four times the absolute difference between `a` and `b`, then add three.
-/
def quadruple_abs_diff_plus_three (a b : Int) : Int :=
  4 * Int.natAbs (a - b) + 3

/-- Precondition: inputs must be integers (always true in Lean) -/
def pre (a b : Int) : Prop := True

/-- Postcondition: result is 4*|a-b|+3 -/
def post (a b : Int) (result : Int) : Prop :=
  result = 4 * Int.natAbs (a - b) + 3

theorem quadruple_abs_diff_plus_three_correct (a b : Int) :
  pre a b → post a b (quadruple_abs_diff_plus_three a b) := by
  intro _
  unfold post quadruple_abs_diff_plus_three
  rfl
  
/-- Tests for quadruple_abs_diff_plus_three -/
def test_quadruple_abs_diff_plus_three : IO Unit := do
  -- Basic test
  IO.println s!"Test 1: {quadruple_abs_diff_plus_three 7 2 = 23}"
  
  -- Edge case with equal numbers
  IO.println s!"Test 2: {quadruple_abs_diff_plus_three 5 5 = 3}"
  
  -- Test with a negative and positive number
  IO.println s!"Test 3: {quadruple_abs_diff_plus_three 0 9 = 39}"

#eval test_quadruple_abs_diff_plus_three
