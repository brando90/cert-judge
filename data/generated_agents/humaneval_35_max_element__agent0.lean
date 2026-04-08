```lean
import Mathlib.Data.List.Basic

namespace VeriBench.MaxElement

/-- Return maximum element in the list. -/
def max_element (l : List Int) : Int :=
  match l with
  | [] => 0  -- This case should not occur based on the problem
  | x::xs => xs.foldl (fun m e => if e > m then e else m) x

/-- The specification of the max_element function. -/
def max_element_spec (l : List Int) : Int :=
  match l with
  | [] => 0  -- This case should not occur based on the problem
  | x::xs => x.max (xs.foldl max x)

/-- Tests for the max_element function. -/
def test : Bool :=
  max_element [1, 2, 3] = 3 &&
  max_element [5, 3, -5, 2, -3, 3, 9, 0, 124, 1, -10] = 124

/-- Precondition: The input list is non-empty. -/
def max_element_pre (l : List Int) : Prop :=
  l.length > 0

/-- Postcondition: The result is an element of the list and is greater than or equal to all elements in the list. -/
def max_element_post (l : List Int) (result : Int) : Prop :=
  result ∈ l ∧ ∀ e ∈ l, e ≤ result

/-- The max_element function satisfies its specification. -/
theorem max_element_correct (l : List Int) (h : max_element_pre l) :
  max_element_post l (max_element l) := by
  sorry

/-- The max_element function matches its specification. -/
theorem max_element_matches_spec (l : List Int) (h : max_element_pre l) :
  max_element l = max_element_spec l := by
  sorry

#eval test

end VeriBench.MaxElement
```
