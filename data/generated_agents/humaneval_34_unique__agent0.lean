```lean
import Std.Data.List.Basic
import Std.Data.List.Lemmas

/--
  Returns sorted unique elements in a list.
  
  Example:
  ```
  unique [5, 3, 5, 2, 3, 3, 9, 0, 123] = [0, 2, 3, 5, 9, 123]
  ```
-/
def unique (l : List Int) : List Int :=
  (l.eraseDups.qsort (· ≤ ·))

/--
  Specification: unique returns a sorted list of unique elements from the input list.
-/
def uniqueSpec (l : List Int) (res : List Int) : Prop :=
  -- The result contains no duplicates
  res.Nodup ∧ 
  -- Every element in the result is in the original list
  (∀ x, x ∈ res → x ∈ l) ∧ 
  -- Every element in the original list is in the result
  (∀ x, x ∈ l → x ∈ res) ∧
  -- The result is sorted in ascending order
  res.Sorted (· ≤ ·)

/--
  Theorem: The implementation of unique satisfies its specification.
-/
theorem unique_correct (l : List Int) : uniqueSpec l (unique l) := by
  sorry

-- Tests
def test1 : unique [5, 3, 5, 2, 3, 3, 9, 0, 123] = [0, 2, 3, 5, 9, 123] := by rfl

#eval unique [5, 3, 5, 2, 3, 3, 9, 0, 123]
```
