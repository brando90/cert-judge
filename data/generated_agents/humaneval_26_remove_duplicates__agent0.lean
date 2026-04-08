import Lean.Data.HashMap
import Std.Data.List.Basic

namespace VeriBench.HumanEval26

/-- From a list of integers, remove all elements that occur more than once.
    Keep order of elements left the same as in the input. -/
def removeDuplicates (numbers : List Int) : List Int :=
  let counter := numbers.foldl (fun acc x => 
    match acc.find? x with
    | some count => acc.insert x (count + 1)
    | none => acc.insert x 1
    ) (Lean.HashMap.empty)
  
  numbers.filter (fun n => 
    match counter.find? n with
    | some count => count <= 1
    | none => false)

/-- Specification for removeDuplicates function -/
def removeDuplicatesSpec (numbers : List Int) : List Int :=
  numbers.filter (fun n => numbers.count n <= 1)

/-- Predicate that checks if a list contains only elements that appear once -/
def containsOnlySingletons (lst : List Int) : Prop :=
  ∀ x, x ∈ lst → lst.count x = 1

/-- Predicate that checks if a list is a sublist of another list with original order preserved -/
def isOrderPreservingSublist (sub : List Int) (lst : List Int) : Prop :=
  ∀ i j, i < j → i < sub.length → j < sub.length → 
    let idxInOrig₁ := lst.findIdx (· = sub[i]!)
    let idxInOrig₂ := lst.findIdx (· = sub[j]!)
    idxInOrig₁ < idxInOrig₂

/-- Precondition: none -/
def pre (_numbers : List Int) : Prop := True

/-- Postcondition: result contains only elements that appear once in the original list,
    and maintains the original order -/
def post (numbers : List Int) (result : List Int) : Prop :=
  -- All elements in result appear in the original list
  (∀ x, x ∈ result → x ∈ numbers) ∧
  -- All elements in result appear exactly once in the original list
  (∀ x, x ∈ result → numbers.count x = 1) ∧
  -- Result preserves the original order
  isOrderPreservingSublist result numbers

theorem removeDuplicates_correct (numbers : List Int) :
  pre numbers → post numbers (removeDuplicates numbers) :=
  sorry

/-- Test cases for removeDuplicates function -/
def tests : List (List Int × List Int) := [
  ([], []),
  ([1, 2, 3, 4], [1, 2, 3, 4]),
  ([1, 2, 3, 2, 4, 3, 5], [1, 4, 5])
]

/-- Run all test cases -/
def runTests : List Bool :=
  tests.map (fun (input, expected) => removeDuplicates input == expected)

/-- Check if all tests pass -/
def allTestsPass : Bool :=
  runTests.all id

#eval allTestsPass -- Should return true

end VeriBench.HumanEval26
