/-!
# VeriBench – Triples Sum to Zero

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

## Triples Sum to Zero

Implements `triples_sum_to_zero`, which checks whether there exist three distinct elements
in a list that sum to zero.-/

namespace TriplesSumToZero
open List -- brings the `~` permutation notation into scope

/--
**Implementation of `triples_sum_to_zero`.**

`triples_sum_to_zero l` returns `true` iff there exist three distinct elements in `l`
that sum to zero.

Note: This function is marked as partial because Lean's termination checker
cannot verify its termination, though we know it terminates because:
1. Each recursive call either increases i, j, or k
2. These indices are bounded by l.length
3. The function returns when any index reaches l.length

## Examples

#eval triples_sum_to_zero [1, 3, 5, 0]         -- expected: false
#eval triples_sum_to_zero [1, 3, -2, 1]        -- expected: true
#eval triples_sum_to_zero [1, 2, 3, 7]         -- expected: false
#eval triples_sum_to_zero [2, 4, -5, 3, 9, 7]  -- expected: true
-/
partial def triples_sum_to_zero (l : List Int) : Bool :=
  let rec check_triple (i j k : Nat) : Bool :=
    if i ≥ l.length then false
    else if j ≥ l.length then check_triple (i + 1) (i + 2) (i + 3)
    else if k ≥ l.length then check_triple i (j + 1) (j + 2)
    else if l[i]! + l[j]! + l[k]! = 0 then true
    else check_triple i j (k + 1)
  check_triple 0 1 2

/-!
# Tests
-/

/-- expected: false -/
example : triples_sum_to_zero [1, 3, 5, 0] = false := by native_decide
#eval triples_sum_to_zero [1, 3, 5, 0] -- expected: false

/-- expected: true -/
example : triples_sum_to_zero [1, 3, -2, 1] = true := by native_decide
#eval triples_sum_to_zero [1, 3, -2, 1] -- expected: true

/-!
# Tests: Edge Cases
-/

/-- expected: false -/
example : triples_sum_to_zero [1, 2, 3, 7] = false := by native_decide
#eval triples_sum_to_zero [1, 2, 3, 7] -- expected: false

/-- expected: true -/
example : triples_sum_to_zero [2, 4, -5, 3, 9, 7] = true := by native_decide
#eval triples_sum_to_zero [2, 4, -5, 3, 9, 7] -- expected: true

/-- expected: false -/
example : triples_sum_to_zero [] = false := by native_decide
#eval triples_sum_to_zero [] -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive test: finds valid triple -/
example : triples_sum_to_zero [1] = false := by native_decide
#eval triples_sum_to_zero [1] -- expected: false

/-- positive test: handles two elements -/
example : triples_sum_to_zero [1, 2] = false := by native_decide
#eval triples_sum_to_zero [1, 2] -- expected: false

/-- positive test: finds triple in longer list -/
example : triples_sum_to_zero [-1, 0, 1, 2] = true := by native_decide
#eval triples_sum_to_zero [-1, 0, 1, 2] -- expected: true

/-- negative test: no valid triple exists -/
example : ¬ (triples_sum_to_zero [1, 2, 3] = true) := by native_decide

/-- negative test: different lists give different results -/
example : triples_sum_to_zero [1, 3, -2, 1] ≠ triples_sum_to_zero [1, 2, 3, 7] := by native_decide

/-!
# Pre‑Condition
-/

/-- **Pre‑condition.** Any list of integers is valid input. -/
def Pre (_ : List Int) : Prop := True

/-!
# Property Theorems
-/

/-- **Specification property**: Correctness specification. -/
def specification_prop (l : List Int) : Prop :=
  triples_sum_to_zero l = true ↔
    ∃ i j k : Nat,
      i < j ∧ j < k ∧ k < l.length ∧
      l[i]! + l[j]! + l[k]! = 0

/-- **Specification theorem**: Correctness specification. -/
@[simp] theorem specification_thm (l : List Int) : specification_prop l := sorry

/-- **Empty list property**: Empty list returns false. -/
def empty_list_prop : Prop := triples_sum_to_zero [] = false

/-- **Empty list theorem**: Empty list returns false. -/
@[simp] theorem empty_list_thm : empty_list_prop := sorry

/-- **Small list property**: Lists with fewer than 3 elements return false. -/
def small_list_prop (l : List Int) : Prop :=
  l.length < 3 → triples_sum_to_zero l = false

/-- **Small list theorem**: Lists with fewer than 3 elements return false. -/
@[simp] theorem small_list_thm (l : List Int) : small_list_prop l := sorry

/-- **Permutation invariance property**: Result is stable under permutations. -/
def permutation_invariance_prop (l l' : List Int) : Prop :=
  l ~ l' → triples_sum_to_zero l = triples_sum_to_zero l'

/-- **Permutation invariance theorem**: Result is stable under permutations. -/
@[simp] theorem permutation_invariance_thm (l l' : List Int) : permutation_invariance_prop l l' := sorry

/-!
# Post‑Condition  (conjunction of all desired properties)
-/

/-- **Post‑condition**: conjunction of all desired properties for triples_sum_to_zero. -/
def Post_prop (l : List Int) : Prop :=
  (specification_prop l) ∧                               -- specification property
  (empty_list_prop) ∧                                   -- empty list property
  (small_list_prop l) ∧                                 -- small list property
  (∀ l', permutation_invariance_prop l l')              -- permutation invariance property

/-!
# Correctness Theorem
-/

/-- **Correctness theorem**: the pre‑condition implies the post‑condition. -/
theorem correctness_thm (l : List Int) (hPre : Pre l) : Post_prop l := sorry

/-!
# Imperative Implementation
-/

/--
`triples_sum_to_zeroImp l` computes the same result using imperative style with triple-nested loops.
-/
def triples_sum_to_zeroImp (l : List Int) : Bool :=
  Id.run do
    for i in [:l.length] do
      for j in [:l.length] do
        if i < j then
          for k in [:l.length] do
            if j < k then
              if l[i]! + l[j]! + l[k]! = 0 then
                return true
    return false

/-!
# Imperative Tests
-/

/-- expected: false -/
example : triples_sum_to_zeroImp [1, 3, 5, 0] = false := by native_decide
#eval triples_sum_to_zeroImp [1, 3, 5, 0] -- expected: false

/-!
# Imperative Tests: Edge Cases
-/

/-- expected: true -/
example : triples_sum_to_zeroImp [1, 3, -2, 1] = true := by native_decide
#eval triples_sum_to_zeroImp [1, 3, -2, 1] -- expected: true

/-!
# Positive / Negative Test‑Suite
-/

/-- positive test: handles empty list -/
example : triples_sum_to_zeroImp [] = false := by native_decide
#eval triples_sum_to_zeroImp [] -- expected: false

/-- negative test: no false positives -/
example : ¬ (triples_sum_to_zeroImp [1, 2, 3] = true) := by native_decide

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem triples_sum_to_zero_equivalence_thm (l : List Int) :
  triples_sum_to_zero l = triples_sum_to_zeroImp l := sorry

end TriplesSumToZero
