import Mathlib

namespace PrimeLength

/--
Functional implementation of `primeLength`.

`primeLength s` returns true if the length of the string is a prime number.

## Examples

#eval primeLength "Hello"  -- expected: true
#eval primeLength "orange" -- expected: false
#eval primeLength ""       -- expected: false
-/
def primeLength (s : String) : Bool :=
  let n := s.length
  if n ≤ 1 then
    false
  else
    (List.range n).drop 2 |>.all (fun i => n % i ≠ 0)

/-- **Empty string theorem**: Empty string has non-prime length. -/

/-!
# VeriBench – Prime Length

File order:

1. Implementation
2. Unit tests (positive, edge, positive/negative test suite)
3. Pre‑condition prop
4. Exhaustive property prop and their theorems
5. Post‑condition prop (same order as property props)
6. Correctness theorem `Pre → Post`
7. Imperative i. implementation, ii. tests (positive, edge, positive/negative
test suite), and iii. equivalence theorem.

All real proofs are left as `sorry` for the learner/model/agent.

# Implementation

## Prime Length

Determines whether the length of a given string is a prime number.
A number is prime if it is greater than 1 and has no divisors other than 1 and itself.
For a string, we take its length and check if it is prime.
-/


/--
Functional implementation of `primeLength`.

`primeLength s` returns true if the length of the string is a prime number.

## Examples

#eval primeLength "Hello"  -- expected: true
#eval primeLength "orange" -- expected: false
#eval primeLength ""       -- expected: false
-/
def primeLength (s : String) : Bool :=
  let n := s.length
  if n ≤ 1 then
    false
  else
    (List.range n).drop 2 |>.all (fun i => n % i ≠ 0)

/-!
# Pre‑Condition
-/

/-- **Pre‑condition.** Input must be a string (always valid). -/
def Pre (_ : String) : Prop := True

/-!
# Property Theorems
-/

/-- **Helper**: Predicate for prime numbers. -/
def isPrime (n : Nat) : Prop :=
  n > 1 ∧ ∀ i, 2 ≤ i ∧ i < n → n % i ≠ 0

/-- **Empty string property**: Empty string has non-prime length. -/
def empty_string_prop : Prop := primeLength "" = false

/-- **Empty string theorem**: Empty string has non-prime length. -/
def single_char_prop (c : Char) : Prop := primeLength (String.singleton c) = false

/-- **Single character theorem**: Single character strings have non-prime length. -/
def length_independence_prop (s1 s2 : String) : Prop :=
  s1.length = s2.length → primeLength s1 = primeLength s2

/-- **Length independence theorem**: Only length matters, not content. -/
def consistency_prop (s : String) : Prop := primeLength s = true ↔ isPrime s.length

/-- **Consistency theorem**: primeLength matches mathematical prime definition. -/

/-!
# Post‑Condition  (conjunction of all desired properties)
-/

/-- **Post‑condition**: conjunction of all desired properties for primeLength. -/
def Post_prop (s : String) : Prop :=
  (empty_string_prop) ∧                                   -- empty string property
  (∀ c, single_char_prop c) ∧                            -- single character property
  (∀ s1 s2, length_independence_prop s1 s2) ∧            -- length independence property
  (consistency_prop s)                                   -- consistency property

@[simp] theorem empty_string_thm : empty_string_prop := by
  unfold empty_string_prop primeLength
  simp [String.length_nil]

/-- **Single character theorem**: Single character strings have non-prime length. -/
@[simp] theorem single_char_thm (c : Char) : single_char_prop c := by
  unfold single_char_prop primeLength
  simp [String.length_singleton]

/-- **Length independence theorem**: Only length matters, not content. -/
theorem length_independence_thm (s1 s2 : String) : length_independence_prop s1 s2 := by
  unfold length_independence_prop primeLength
  intro h
  simp [h]

/-- **Consistency theorem**: primeLength matches mathematical prime definition. -/
private lemma mem_range_drop_two {n : Nat} (hn : n ≥ 2) {i : Nat} :
    i ∈ (List.range n).drop 2 ↔ 2 ≤ i ∧ i < n := by
  constructor
  · intro h
    constructor
    · obtain ⟨j, _, hval⟩ := List.mem_iff_getElem.mp h
      rw [List.getElem_drop] at hval
      rw [List.getElem_range] at hval
      omega
    · exact List.mem_range.mp (List.drop_subset 2 (List.range n) h)
  · intro ⟨hi2, hin⟩
    apply List.mem_iff_getElem.mpr
    refine ⟨i - 2, ?_, ?_⟩
    · simp [List.length_drop, List.length_range]; omega
    · rw [List.getElem_drop, List.getElem_range]; omega

theorem consistency_thm (s : String) : consistency_prop s := by
  unfold consistency_prop primeLength isPrime
  simp only
  set n := s.length
  constructor
  · intro h
    split_ifs at h with hle
    · simp_all
    · constructor
      · omega
      · intro i hi2 hin
        exact h i ((mem_range_drop_two (by omega)).mpr ⟨hi2, hin⟩)
  · intro ⟨hgt, hndvd⟩
    split_ifs with hle
    · omega
    · simp only [List.all_eq_true, decide_eq_true_eq]
      intro i hi
      exact hndvd i ((mem_range_drop_two (by omega)).mp hi)

/-- **Correctness theorem**: the pre‑condition implies the post‑condition. -/
theorem correctness_thm (s : String) (hPre : Pre s) : Post_prop s :=
  ⟨empty_string_thm, single_char_thm, length_independence_thm, consistency_thm s⟩


end PrimeLength