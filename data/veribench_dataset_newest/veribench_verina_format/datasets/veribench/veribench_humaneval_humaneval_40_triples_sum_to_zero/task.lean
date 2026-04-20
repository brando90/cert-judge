-- !benchmark @start import type=solution
import Mathlib
namespace TriplesSumToZero
open List
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def triples_sum_to_zero_precond (l : List Int) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

partial def triples_sum_to_zero (l : List Int) (h_precond : triples_sum_to_zero_precond (l)) : Bool :=
  -- !benchmark @start code
  let rec check_triple (i j k : Nat) : Bool :=
    if i ≥ l.length then false
    else if j ≥ l.length then check_triple (i + 1) (i + 2) (i + 3)
    else if k ≥ l.length then check_triple i (j + 1) (j + 2)
    else if l[i]! + l[j]! + l[k]! = 0 then true
    else check_triple i j (k + 1)
  check_triple 0 1 2
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

-- !benchmark @start proof_aux
/-- **Specification property**: Correctness specification. -/
def specification_prop (l : List Int) : Prop :=
  triples_sum_to_zero (l) (by simp) = true ↔
    ∃ i j k : Nat,
      i < j ∧ j < k ∧ k < l.length ∧
      l[i]! + l[j]! + l[k]! = 0

/-- **Specification theorem**: Correctness specification. -/
@[simp] theorem specification_thm (l : List Int) : specification_prop l := by
  sorry

/-- **Empty list property**: Empty list returns false. -/
def empty_list_prop : Prop := triples_sum_to_zero ([]) (by simp) = false

/-- **Empty list theorem**: Empty list returns false. -/
@[simp] theorem empty_list_thm : empty_list_prop := by
  sorry

/-- **Small list property**: Lists with fewer than 3 elements return false. -/
def small_list_prop (l : List Int) : Prop :=
  l.length < 3 → triples_sum_to_zero (l) (by simp) = false

/-- **Small list theorem**: Lists with fewer than 3 elements return false. -/
@[simp] theorem small_list_thm (l : List Int) : small_list_prop l := by
  sorry

/-- **Permutation invariance property**: Result is stable under permutations. -/
def permutation_invariance_prop (l l' : List Int) : Prop :=
  l ~ l' → triples_sum_to_zero (l) (by simp) = triples_sum_to_zero (l') (by simp)

/-- **Permutation invariance theorem**: Result is stable under permutations. -/
@[simp] theorem permutation_invariance_thm (l l' : List Int) : permutation_invariance_prop l l' := by
  sorry
-- !benchmark @end proof_aux

@[reducible, simp]
def triples_sum_to_zero_postcond (l : List Int) (result : Bool)
    (h_precond : triples_sum_to_zero_precond (l)) : Prop :=
  -- !benchmark @start postcond
  (specification_prop l) ∧
  (empty_list_prop) ∧
  (small_list_prop l) ∧
  (∀ l', permutation_invariance_prop l l')
  -- !benchmark @end postcond

theorem triples_sum_to_zero_spec_satisfied (l : List Int) (h_precond : triples_sum_to_zero_precond (l)) :
    triples_sum_to_zero_postcond (l) (triples_sum_to_zero (l) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof