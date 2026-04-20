import Mathlib

namespace LongestString

/--
**Implementation of `longest`.**

Takes a list of strings and returns the longest one.
If multiple strings have the same maximum length, returns the first one.
Returns none if the input list is empty.

## Examples

#eval longest [] -- expected: none
#eval longest ["a", "b", "c"] -- expected: some "a"
#eval longest ["a", "bb", "ccc"] -- expected: some "ccc"
-/
def longest (strings : List String) : Option String :=
  match strings with
  | [] => none
  | xs =>
    let maxlen := xs.map String.length |>.max?.getD 0
    xs.find? (fun s => s.length = maxlen)

/--
**Imperative implementation of `longest`.**

Alternative implementation using imperative style for comparison.
-/
def longestImp (strings : List String) : Option String :=
  match strings with
  | [] => none
  | first :: rest =>
    let rec loop (current : String) (remaining : List String) : String :=
      match remaining with
      | [] => current
      | head :: tail =>
        if head.length > current.length then
          loop head tail
        else
          loop current tail
    some (loop first rest)

/-- **Maximal theorem**: If longest returns a string, it has maximum length. -/
@[simp] theorem maximal_thm (strings : List String) : maximal_prop strings := by
  unfold maximal_prop
  intro s hs s' hs'
  cases strings with
  | nil => simp [longest] at hs
  | cons x xs =>
    simp only [longest] at hs
    have h_find := List.find?_some hs
    simp at h_find
    have h_mem := List.mem_of_find?_eq_some hs
    have h_maxlen : (x :: xs).map String.length |>.max?.getD 0 = s.length := h_find.2
    have h_s'_in_map : s'.length ∈ (x :: xs).map String.length := by
      apply List.mem_map_of_mem String.length hs'
    have h_max_ge : (x :: xs).map String.length |>.max?.getD 0 ≥ s'.length := by
      cases h_max : (x :: xs).map String.length |>.max? with
      | none => 
        simp [List.max?] at h_max
        have : (x :: xs).map String.length = [] := List.max?_eq_none.mp h_max
        simp [List.map] at this
      | some m =>
        simp [Option.getD]
        exact List.le_max_of_mem h_s'_in_map h_max
    rw [← h_maxlen]
    exact h_max_ge

/-- **First occurrence theorem**: Returns the first string with maximum length. -/
@[simp] theorem first_occurrence_thm (strings : List String) : first_occurrence_prop strings := by
  unfold first_occurrence_prop
  intro s hs s' hs' h_len_eq
  cases strings with
  | nil => simp [longest] at hs
  | cons x xs =>
    simp only [longest] at hs
    have h_find := List.find?_some hs
    simp at h_find
    have h_maxlen : (x :: xs).map String.length |>.max?.getD 0 = s.length := h_find.2
    rw [h_len_eq] at h_maxlen
    have h_s'_prop : s'.length = (x :: xs).map String.length |>.max?.getD 0 := h_maxlen.symm
    have h_find_first : ∀ t ∈ x :: xs, t.length = (x :: xs).map String.length |>.max?.getD 0 → 
                        List.idxOf s (x :: xs) ≤ List.idxOf t (x :: xs) := by
      intro t ht h_t_len
      exact List.idxOf_find?_le hs ht (by simp [h_t_len])
    exact h_find_first s' hs' h_s'_prop

/-- **Non-empty result theorem**: Non-empty lists return Some value. -/
@[simp] theorem non_empty_result_thm (strings : List String) : non_empty_result_prop strings := by
  unfold non_empty_result_prop
  intro h_ne_empty
  cases strings with
  | nil => contradiction
  | cons x xs =>
    simp only [longest]
    simp [Option.isSome]
    apply List.find?_isSome.mpr
    use x
    constructor
    · simp
    · simp
      rfl

/-- **Correctness theorem**: the pre‑condition implies the post‑condition. -/
theorem correctness_thm (strings : List String) (hPre : Pre strings) : Post_prop strings := by
  unfold Post_prop
  exact ⟨empty_list_thm, maximal_thm strings, membership_thm strings, 
         first_occurrence_thm strings, non_empty_result_thm strings⟩

end LongestString
