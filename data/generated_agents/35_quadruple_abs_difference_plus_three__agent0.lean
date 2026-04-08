import Lean
import VeriBench.Common

namespace QuadrupleAbsDiffPlusThree

def pre (a b : Int) : Bool := true

def post (a b : Int) (result : Int) : Bool :=
  result = 4 * (a - b).natAbs + 3

def quadruple_abs_diff_plus_three (a b : Int) : Int :=
  4 * (a - b).natAbs + 3

theorem quadruple_abs_diff_plus_three_correct (a b : Int) :
  pre a b → post a b (quadruple_abs_diff_plus_three a b) := by
  intro h
  unfold post
  unfold quadruple_abs_diff_plus_three
  rfl

def test : IO Unit := do
  -- Basic test
  IO.println s!"Test 1: {quadruple_abs_diff_plus_three 7 2}"
  assert! quadruple_abs_diff_plus_three 7 2 = 23
  
  -- Edge case: equal numbers
  IO.println s!"Test 2: {quadruple_abs_diff_plus_three 5 5}"
  assert! quadruple_abs_diff_plus_three 5 5 = 3
  
  -- Additional test
  IO.println s!"Test 3: {quadruple_abs_diff_plus_three 0 9}"
  assert! quadruple_abs_diff_plus_three 0 9 = 39
  
  IO.println "All tests passed!"

end QuadrupleAbsDiffPlusThree
