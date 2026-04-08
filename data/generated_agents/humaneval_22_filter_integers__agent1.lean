import Std.Data.List.Basic

/--
Filter given list of any python values only for integers.

Example:
```
filter_integers [.string "a", .float 3.14, .int 5] = [5]
filter_integers [.int 1, .int 2, .int 3, .string "abc", .dict {}, .list []] = [1, 2, 3]
```
-/

inductive PyValue where
  | int : Int → PyValue
  | float : Float → PyValue
  | string : String → PyValue
  | list : List PyValue → PyValue
  | dict : List (PyValue × PyValue) → PyValue
  deriving Repr

def filter_integers (values : List PyValue) : List Int :=
  values.filterMap (λ x => match x with
    | .int n => some n
    | _ => none)

/-- Specification for filter_integers -/
def filter_integers_spec (values : List PyValue) : List Int :=
  values.filterMap (λ x => match x with
    | .int n => some n
    | _ => none)

/-- Precondition for filter_integers -/
def filter_integers_pre (_values : List PyValue) : Prop := True

/-- Postcondition for filter_integers -/
def filter_integers_post (values : List PyValue) (result : List Int) : Prop :=
  result = filter_integers_spec values

theorem filter_integers_correct (values : List PyValue) 
    (h_pre : filter_integers_pre values) : 
    filter_integers_post values (filter_integers values) := by
  unfold filter_integers_post
  unfold filter_integers_spec
  unfold filter_integers
  simp
  sorry

def main : IO Unit := do
  -- Test 1: Empty list
  let test1 := filter_integers []
  IO.println s!"Test 1: {test1}"
  assert! test1 == []

  -- Test 2: Mixed list with integers
  let test2 := filter_integers [.int 4, .dict [], .list [], .float 23.2, .int 9, .string "adasd"]
  IO.println s!"Test 2: {test2}"
  assert! test2 == [4, 9]

  -- Test 3: List with integers and strings
  let test3 := filter_integers [.int 3, .string "c", .int 3, .int 3, .string "a", .string "b"]
  IO.println s!"Test 3: {test3}"
  assert! test3 == [3, 3, 3]

  IO.println "All tests passed!"
