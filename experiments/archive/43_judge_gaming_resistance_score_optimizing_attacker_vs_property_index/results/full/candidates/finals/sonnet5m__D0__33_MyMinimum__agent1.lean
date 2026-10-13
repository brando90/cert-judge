import Mathlib
import Mathlib.Tactic.Have

import Mathlib.Tactic.Ring
import Mathlib.Data.Int.Basic

/-!
# My Min List

Return the smallest element in a non-empty list of non-negative integers.

In this Lean model, elements are `Nat`, so non-negativity is built into the
input type. Empty lists are excluded by `pre`.
-/

namespace MyMinList

def my_min_list (xs : List Nat) : Nat :=
  match xs with
  | [] => panic! "Require non-empty list of non-negative integers"
  | x :: xs => xs.foldl min x

/-- The precondition for `my_min_list` is that the input list is non-empty. -/
def pre (xs : List Nat) : Prop :=
  xs ≠ []

/-- The postcondition says the result is a least element of the input list. -/
def post (xs : List Nat) (result : Nat) : Prop :=
  (∀ x ∈ xs, result ≤ x) ∧ (result ∈ xs)

/-- The result is a smallest member of every valid input list. -/
theorem my_min_list_spec (xs : List Nat) (h : pre xs) :
    post xs (my_min_list xs) := by
  sorry

theorem my_min_list_le_of_mem (xs : List Nat) (h : pre xs)
    {x : Nat} (hx : x ∈ xs) :
    my_min_list xs ≤ x := by
  exact (my_min_list_spec xs h).1 x hx

theorem my_min_list_mem (xs : List Nat) (h : pre xs) :
    my_min_list xs ∈ xs := by
  exact (my_min_list_spec xs h).2

/-- Any member that is a lower bound for the list equals the computed minimum. -/
theorem my_min_list_eq_of_post (xs : List Nat) (h : pre xs) (y : Nat)
    (hy : post xs y) :
    my_min_list xs = y := by
  sorry

/-- The minimum is uniquely characterized by the postcondition. -/
theorem my_min_list_characterization (xs : List Nat) (h : pre xs) (y : Nat) :
    post xs y ↔ y = my_min_list xs := by
  sorry

/-- On a nonempty list, the implementation is the fold of `min` from its head. -/
theorem my_min_list_cons_eq_foldl (x : Nat) (xs : List Nat) :
    my_min_list (x :: xs) = xs.foldl min x := rfl

theorem my_min_list_cons_le_head (x : Nat) (xs : List Nat) :
    my_min_list (x :: xs) ≤ x := by
  sorry

theorem my_min_list_cons_mem (x : Nat) (xs : List Nat) :
    my_min_list (x :: xs) ∈ x :: xs := by
  sorry

/-- A singleton list has that element as its minimum. -/
theorem my_min_list_singleton (x : Nat) :
    my_min_list [x] = x := by
  sorry

/-- The result does not depend on the ordering of the input list. -/
theorem my_min_list_perm (xs ys : List Nat) (hxy : xs.Perm ys)
    (hxs : pre xs) :
    my_min_list xs = my_min_list ys := by
  sorry

/-- The minimum of a concatenation is the minimum of the two minima. -/
theorem my_min_list_append (xs ys : List Nat)
    (hxs : pre xs) (hys : pre ys) :
    my_min_list (xs ++ ys) = min (my_min_list xs) (my_min_list ys) := by
  sorry

/-- Adding the same natural number to every element shifts the minimum by it. -/
theorem my_min_list_map_add (xs : List Nat) (k : Nat) (hxs : pre xs) :
    my_min_list (xs.map (fun x => x + k)) = my_min_list xs + k := by
  sorry

theorem pre_iff_exists_cons (xs : List Nat) :
    pre xs ↔ ∃ x ys, xs = x :: ys := by
  sorry

/-- Test cases for my_min_list. -/
def test : IO Unit := do
  -- Basic
  assert! (my_min_list [7, 3, 9, 2] = 2)
  -- Edge
  assert! (my_min_list [5] = 5)
  -- Duplicates
  assert! (my_min_list [4, 2, 2, 3] = 2)
  -- Larger numbers
  assert! (my_min_list [100, 42, 99, 101] = 42)
  -- Already sorted and reverse sorted
  assert! (my_min_list [1, 2, 3] = 1)
  assert! (my_min_list [3, 2, 1] = 1)

  IO.println "All tests passed!"

example : my_min_list [7, 3, 9, 2] = 2 := by decide
example : my_min_list [5] = 5 := by decide
example : my_min_list [4, 2, 2, 3] = 2 := by decide

end MyMinList
