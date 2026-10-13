/-
  Return the smallest element in a non-empty list of non-negative integers.

  Edge cases:
  - Single-element list returns that element.
  - Empty list or non-integers are invalid and raise ValueError.
-/

def my_min_list (xs : List Nat) : Nat :=
  match xs with
  | [] => panic! "Require non-empty list of non-negative integers"
  | [x] => x
  | x :: xs => 
    let min_rest := my_min_list xs
    if x < min_rest then x else min_rest

/-- The precondition for `my_min_list`: The list must be non-empty. -/
def my_min_list_pre (xs : List Nat) : Prop :=
  xs.length > 0

/-- The postcondition for `my_min_list`: The result is the minimum element in the list. -/
def my_min_list_post (xs : List Nat) (result : Nat) : Prop :=
  result ∈ xs ∧ ∀ x ∈ xs, result ≤ x

theorem my_min_list_correct (xs : List Nat) (h : my_min_list_pre xs) :
  my_min_list_post xs (my_min_list xs) := by
  sorry

/--
Test cases for `my_min_list`
-/
def test_my_min_list : IO Unit := do
  -- Basic test
  IO.println s!"Test 1: {my_min_list [7, 3, 9, 2]}"
  assert! my_min_list [7, 3, 9, 2] = 2

  -- Edge case: single element
  IO.println s!"Test 2: {my_min_list [5]}"
  assert! my_min_list [5] = 5

  -- The empty list case would cause a runtime error, not tested here
  
  IO.println "All tests passed!"

#eval test_my_min_list
