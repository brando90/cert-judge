import Std.Data.List.Basic

namespace VeriBench

/--
  From a list of integers, remove all elements that occur more than once.
  Keep order of elements left the same as in the input.
-/
def removeDuplicates (numbers : List Int) : List Int :=
  let counts := numbers.foldl (fun m n => m.insert n ((m.findD n 0) + 1)) (Std.HashMap.empty)
  numbers.filter (fun n => counts.findD n 0 ≤ 1)

/-- Tests for removeDuplicates -/
def removeDuplicatesTests : IO Unit := do
  assert! (removeDuplicates [] = [])
  assert! (removeDuplicates [1, 2, 3, 4] = [1, 2, 3, 4])
  assert! (removeDuplicates [1, 2, 3, 2, 4, 3, 5] = [1, 4, 5])
  IO.println "All tests passed!"

/-- Predicate to check if an element occurs at most once in a list -/
def occursAtMostOnce (x : Int) (xs : List Int) : Bool :=
  xs.filter (· == x) |>.length ≤ 1

/-- Precondition: None -/
def removeDuplicatesPre (_numbers : List Int) : Prop := True

/-- Postcondition: Each element in the output occurs exactly once in the input,
    and appears at most once in the input list. The relative order of elements is preserved. -/
def removeDuplicatesPost (numbers : List Int) (result : List Int) : Prop :=
  -- Each element in the result appears in the original list
  (∀ x ∈ result, x ∈ numbers) ∧
  -- Each element in the result appears at most once in the original list
  (∀ x ∈ result, occursAtMostOnce x numbers) ∧
  -- The relative order of elements is preserved
  (∀ i j, i < j → result.get? i = some (result.getD i 0) → result.get? j = some (result.getD j 0) →
    let idxI := numbers.findIdx (· == result.getD i 0)
    let idxJ := numbers.findIdx (· == result.getD j 0)
    idxI < idxJ)

/-- Theorem: removeDuplicates satisfies its specification -/
theorem removeDuplicatesCorrect (numbers : List Int) :
  removeDuplicatesPre numbers → removeDuplicatesPost numbers (removeDuplicates numbers) := sorry

end VeriBench
