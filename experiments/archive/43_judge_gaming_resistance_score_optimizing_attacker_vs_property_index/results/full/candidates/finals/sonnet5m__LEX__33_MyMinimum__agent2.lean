/-
  Return the smallest element in a non-empty list of non-negative integers.

  Natural numbers encode the non-negative integer inputs; the precondition
  records that the list is non-empty.
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

/-- The result occurs in the list and is no greater than any list element. -/
def my_min_list_post (xs : List Nat) (result : Nat) : Prop :=
  result ∈ xs ∧ ∀ x ∈ xs, result ≤ x

theorem my_min_list_correct (xs : List Nat) (h : my_min_list_pre xs) :
    my_min_list_post xs (my_min_list xs) := by sorry

/-- The computed minimum belongs to the input list. -/
theorem my_min_list_mem (xs : List Nat) (h : my_min_list_pre xs) :
    my_min_list xs ∈ xs :=
  (my_min_list_correct xs h).1

/-- The computed minimum is no greater than any element of the input list. -/
theorem my_min_list_le (xs : List Nat) (h : my_min_list_pre xs)
    (x : Nat) (hx : x ∈ xs) :
    my_min_list xs ≤ x :=
  (my_min_list_correct xs h).2 x hx

/-- A singleton list has that element as its minimum. -/
theorem my_min_list_singleton (x : Nat) : my_min_list [x] = x := by
  simp [my_min_list]

example : my_min_list [7, 3, 9, 2] = 2 := by decide
example : my_min_list [5] = 5 := by decide
example : ¬ my_min_list_pre ([] : List Nat) := by simp [my_min_list_pre]

/--
Test cases for `my_min_list`.
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
