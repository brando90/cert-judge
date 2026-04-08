```lean
import Std.Data.List.Basic
import Std.Tactic.Basic

/--
  Return a new list with the elements in reverse order.

  Edge cases:
  - Empty list returns empty list.
  - Single element list returns the same list.
  - The function raises ValueError if input is not a list of integers.
-/

def pre (xs : List Int) : Prop := true

def post (xs : List Int) (result : List Int) : Prop :=
  result = xs.reverse

def prog (xs : List Int) : List Int :=
  xs.reverse

theorem prog_correct (xs : List Int) (h_pre : pre xs) : 
  post xs (prog xs) := by
  simp [post, prog]
  sorry

-- Tests
def test1 : prog [1, 2, 3, 4] = [4, 3, 2, 1] := by rfl
def test2 : prog [] = [] := by rfl
def test3 : prog [5] = [5] := by rfl

-- Note: In Lean, we use strong typing so the precondition about
-- "list of integers" is handled by the type system automatically.
-- There's no need to check if the list contains only integers
-- because the type system guarantees it.
```
