import Mathlib.Data.List.Basic
import Mathlib.Tactic.LibrarySearch
import Mathlib.Algebra.BigOperators.Basic

/--
Product of all elements in a non-empty list of integers.

Edge cases:
- Single-element list returns that element.
- Empty list is invalid.
-/
def productOfList (xs : List Int) : Int :=
  match xs with
  | [] => panic! "Require non-empty list"
  | x :: xs => xs.foldl (· * ·) x

/-- Precondition: list must be non-empty -/
def productOfList.pre (xs : List Int) : Prop :=
  xs ≠ []

/-- Postcondition: result equals the product of all elements -/
def productOfList.post (xs : List Int) (result : Int) : Prop :=
  result = xs.prod

theorem productOfList_correct (xs : List Int) (h : productOfList.pre xs) :
  productOfList.post xs (productOfList xs) := by
  unfold productOfList.pre at h
  unfold productOfList.post
  unfold productOfList
  cases xs with
  | nil => contradiction
  | cons head tail =>
    simp [List.prod]
    induction tail with
    | nil => simp [List.foldl]
    | cons x xs ih =>
      simp [List.foldl]
      sorry

-- Tests
#eval productOfList [2, 3, 4] -- 24
#eval productOfList [5] -- 5
#eval productOfList [1, 1, 1] -- 1

example : productOfList [2, 3, 4] = 24 := by rfl
example : productOfList [5] = 5 := by rfl
example : productOfList [1, 1, 1] = 1 := by rfl
