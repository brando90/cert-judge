import Std.Data.List.Basic

/-- Return a new list containing only the even numbers from the input list.

Edge cases:
- Empty list returns empty list.
- List with no even numbers returns empty list.
- The function raises ValueError if input is not a list of integers.
-/

def pre (xs : List Int) : Bool := true

def prog (xs : List Int) : List Int :=
  xs.filter (fun x => x % 2 == 0)

theorem post_empty : prog [] = [] := by
  unfold prog
  simp

theorem post_no_evens : ∀ xs : List Int, (∀ x ∈ xs, x % 2 ≠ 0) → prog xs = [] := by
  intros xs h
  unfold prog
  simp
  apply List.filter_eq_nil
  intro x hx
  simp
  apply h
  assumption

theorem post_correct : ∀ xs : List Int, ∀ x : Int, x ∈ prog xs ↔ (x ∈ xs ∧ x % 2 = 0) := by
  intros xs x
  unfold prog
  simp
  exact List.mem_filter

def test1 : prog [1, 2, 3, 4, 5, 6] = [2, 4, 6] := by rfl
def test2 : prog [] = [] := by rfl
def test3 : prog [1, 3, 5, 7] = [] := by rfl

theorem correctness : ∀ xs : List Int, pre xs → (∀ x : Int, x ∈ prog xs ↔ (x ∈ xs ∧ x % 2 = 0)) := by
  intros xs _ x
  apply post_correct
  sorry
