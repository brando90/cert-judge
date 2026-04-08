import Lean.Data.List
import VeriBench.Common

namespace TriplesSumToZero

/--
  `triplesSumToZero` takes a list of integers as an input.
  It returns `true` if there are three distinct elements in the list that
  sum to zero, and `false` otherwise.
-/
def triplesSumToZero (l : List Int) : Bool :=
  let rec aux (i : Nat) : Bool :=
    if i >= l.length then
      false
    else
      let rec auxJ (j : Nat) : Bool :=
        if j >= l.length then
          aux (i + 1)
        else
          let rec auxK (k : Nat) : Bool :=
            if k >= l.length then
              auxJ (j + 1)
            else
              if l[i]! + l[j]! + l[k]! == 0 then
                true
              else
                auxK (k + 1)
          if j + 1 < l.length then
            auxK (j + 1)
          else
            auxJ (j + 1)
      if i + 1 < l.length then
        auxJ (i + 1)
      else
        aux (i + 1)
  aux 0

/--
  The specification states that there must be three *distinct* elements that sum to zero.
  This predicate checks if there exist distinct indices i, j, k such that
  the elements at those indices sum to zero.
-/
def existsTripleWithZeroSum (l : List Int) : Prop :=
  ∃ i j k, i < l.length ∧ j < l.length ∧ k < l.length ∧ 
           i < j ∧ j < k ∧ 
           l[i]! + l[j]! + l[k]! = 0

/--
  Precondition: none
-/
def triplesSumToZeroPre (l : List Int) : Prop := True

/--
  Postcondition: The function returns true if and only if there exist three distinct
  elements in the list that sum to zero.
-/
def triplesSumToZeroPost (l : List Int) (result : Bool) : Prop :=
  result = true ↔ existsTripleWithZeroSum l

theorem triplesSumToZeroCorrect (l : List Int) :
  triplesSumToZeroPre l → triplesSumToZeroPost l (triplesSumToZero l) := by
  sorry

/-- Test cases for the `triplesSumToZero` function. -/
def testTriplesSumToZero : IO Unit := do
  VeriBench.checkEqual (triplesSumToZero [1, 3, 5, 0]) false
  VeriBench.checkEqual (triplesSumToZero [1, 3, 5, -1]) false
  VeriBench.checkEqual (triplesSumToZero [1, 3, -2, 1]) true
  VeriBench.checkEqual (triplesSumToZero [1, 2, 3, 7]) false
  VeriBench.checkEqual (triplesSumToZero [1, 2, 5, 7]) false
  VeriBench.checkEqual (triplesSumToZero [2, 4, -5, 3, 9, 7]) true
  VeriBench.checkEqual (triplesSumToZero [1]) false
  VeriBench.checkEqual (triplesSumToZero [1, 3, 5, -100]) false
  VeriBench.checkEqual (triplesSumToZero [100, 3, 5, -100]) false
  IO.println "All tests passed!"

end TriplesSumToZero
