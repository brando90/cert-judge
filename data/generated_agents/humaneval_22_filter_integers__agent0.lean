```lean
import Lean
open Lean

def filterIntegers (values : List (Sum Int String)) : List Int :=
  values.filterMap fun v =>
    match v with
    | Sum.inl i => some i
    | Sum.inr _ => none

def test : IO Unit := do
  let test1 := filterIntegers [Sum.inr "a", Sum.inr "3.14", Sum.inl 5]
  IO.println s!"Test 1: {test1}"
  assert! test1 == [5]

  let test2 := filterIntegers [Sum.inl 1, Sum.inl 2, Sum.inl 3, Sum.inr "abc"]
  IO.println s!"Test 2: {test2}"
  assert! test2 == [1, 2, 3]

  let test3 := filterIntegers []
  IO.println s!"Test 3: {test3}"
  assert! test3 == []

  let test4 := filterIntegers [Sum.inl 4, Sum.inr "{}", Sum.inr "[]", Sum.inr "23.2", Sum.inl 9, Sum.inr "adasd"]
  IO.println s!"Test 4: {test4}"
  assert! test4 == [4, 9]

  let test5 := filterIntegers [Sum.inl 3, Sum.inr "c", Sum.inl 3, Sum.inl 3, Sum.inr "a", Sum.inr "b"]
  IO.println s!"Test 5: {test5}"
  assert! test5 == [3, 3, 3]

  IO.println "All tests passed!"

-- Specification
theorem filterIntegers_spec (values : List (Sum Int String)) : 
  filterIntegers values = values.filterMap (fun v => match v with | Sum.inl i => some i | Sum.inr _ => none) :=
  rfl

-- Correctness theorem
theorem filterIntegers_correctness (values : List (Sum Int String)) : 
  ∀ x ∈ filterIntegers values, ∃ v ∈ values, v = Sum.inl x :=
  sorry
```
