import Mathlib

namespace AllPrefixes

/--
**Implementation of `allPrefixes`.**

Returns a list of all prefixes from shortest to longest of the input string.

## Examples

#eval allPrefixes "" -- expected: []
#eval allPrefixes "abc" -- expected: ["a", "ab", "abc"]
-/
def allPrefixes (s : String) : List String :=
  (List.range s.length).map (fun i => s.take (i + 1))

/--
**Imperative implementation of `allPrefixes`.**

Returns a list of all prefixes from shortest to longest of the input string.
-/
def allPrefixesImp (s : String) : List String :=
  let rec aux (i : Nat) (acc : List String) : List String :=
    if i > s.length then acc
    else aux (i + 1) (acc ++ [s.take i])
  aux 1 []

/-- **Last prefix theorem**: Last prefix is the full string. -/
@[simp] theorem last_prefix_thm (s : String) : last_prefix_prop s := by
  unfold last_prefix_prop allPrefixes
  intro h
  simp [List.getLast?_map]
  cases' s.length with n
  · contradiction
  · simp [List.range_succ, List.map_append, List.map_cons, List.getLast?_append]
    simp [String.take_length]

/-- **Increasing length theorem**: Each prefix is one character longer than the previous. -/
@[simp] theorem increasing_length_thm (s : String) : increasing_length_prop s := by
  unfold increasing_length_prop allPrefixes
  intro i hi
  simp at hi
  simp [List.getElem!_map, List.getElem_range]
  rw [String.length_take]
  simp [min_eq_left]
  omega

/-- **Prefix theorem**: Each element is a prefix of the original string. -/
@[simp] theorem prefix_thm (s : String) : prefix_prop s := by
  unfold prefix_prop allPrefixes
  intro p hp
  simp [List.mem_map, List.mem_range] at hp
  obtain ⟨i, hi, rfl⟩ := hp
  exact String.startsWith_take _ _

/-- **Correctness theorem**: the pre‑condition implies the post‑condition. -/
theorem correctness_thm (s : String) (hPre : Pre s) : Post_prop s := by
  unfold Post_prop
  exact ⟨empty_string_thm, length_thm s, last_prefix_thm s, increasing_length_thm s, prefix_thm s⟩

end AllPrefixes
