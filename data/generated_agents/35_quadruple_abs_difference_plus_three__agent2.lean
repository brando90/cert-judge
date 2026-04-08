/-
# VeriBench: quadruple_abs_diff_plus_three
-/

def quadruple_abs_diff_plus_three (a b : Int) : Int :=
  4 * (a - b).natAbs + 3

/-- Return 4*|a - b| + 3 for integers a and b. -/
def quadruple_abs_diff_plus_three_spec (a b : Int) : Int :=
  4 * (a - b).natAbs + 3

/-- Precondition: a and b must be integers (always true in Lean) -/
def quadruple_abs_diff_plus_three_pre (a b : Int) : Prop := True

/-- Postcondition: result equals 4*|a - b| + 3 -/
def quadruple_abs_diff_plus_three_post (a b : Int) (result : Int) : Prop :=
  result = 4 * (a - b).natAbs + 3

theorem quadruple_abs_diff_plus_three_correct (a b : Int) :
  quadruple_abs_diff_plus_three_pre a b →
  quadruple_abs_diff_plus_three_post a b (quadruple_abs_diff_plus_three a b) := by
  intro _
  unfold quadruple_abs_diff_plus_three_post
  unfold quadruple_abs_diff_plus_three
  simp

/-- Tests for quadruple_abs_diff_plus_three -/
def quadruple_abs_diff_plus_three_tests : Bool :=
  -- Basic test
  quadruple_abs_diff_plus_three 7 2 = 23 &&
  -- Edge case with equal numbers
  quadruple_abs_diff_plus_three 5 5 = 3 &&
  -- Test with zero
  quadruple_abs_diff_plus_three 0 9 = 39

#eval quadruple_abs_diff_plus_three_tests
