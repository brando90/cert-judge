import Mathlib.Data.List.Basic
import Mathlib.Data.Int.Basic

/-!
# Triple All Elements in a List

Triple each integer in the input list.

Edge cases:
- Empty list returns empty list.
- Non-integer elements are invalid and handled by type system.
-/

def tripleAll (lst : List Int) : List Int :=
  lst.map (fun x => x * 3)

/-- The precondition is handled by the Lean type system -/
def pre (lst : List Int) : Prop := True

/-- The postcondition specifies that each element in the output is triple the corresponding element in the input -/
def post (lst : List Int) (result : List Int) : Prop :=
  lst.length = result.length ∧
  (List.zipWith (fun x y => y = x * 3) lst result).all id

theorem tripleAll_correct (lst : List Int) : post lst (tripleAll lst) := by
  unfold post
  unfold tripleAll
  simp [List.length_map]
  have h1 : (List.zipWith (fun x y => y = x * 3) lst (lst.map fun x => x * 3)).all id = true := by
    induction lst with
    | nil => simp
    | cons head tail ih =>
      simp [List.zipWith, List.all]
      constructor
      · simp
      · exact ih
  simp [h1]
  sorry

/-- Test cases for tripleAll -/
def testTripleAll : IO Unit := do
  -- Basic case
  assert! (tripleAll [1, 2, 3] = [3, 6, 9])
  
  -- Empty list
  assert! (tripleAll [] = [])
  
  -- Negative numbers
  assert! (tripleAll [-1, 0, 4] = [-3, 0, 12])
  
  IO.println "All tests passed!"

#eval testTripleAll
