-- !benchmark @start import type=solution
import Mathlib
namespace UniqueElements
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def unique_precond (l : List Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def unique (l : List Nat) (h_precond : unique_precond (l)) : List Nat :=
  -- !benchmark @start code
  (l.eraseDups.toArray.qsort (· ≤ ·)).toList
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def unique_postcond (l : List Nat) (result : List Nat) (h_precond : unique_precond (l)) : Prop :=
  -- !benchmark @start postcond
  (result = unique (l) (by simp)) ∧
  (result.Nodup) ∧
  (∀ i j : Nat, i < j → j < result.length → result[i]! ≤ result[j]!) ∧
  (∀ x ∈ result, x ∈ l) ∧
  (∀ x ∈ l, x ∈ result)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

/-- **No duplicates property**: Result has no duplicate elements. -/
def no_duplicates_prop (l : List Nat) : Prop := (unique (l) (by simp)).Nodup

/-- **No duplicates theorem**: Result has no duplicate elements. -/
@[simp] theorem no_duplicates_thm (l : List Nat) : no_duplicates_prop l := by
  sorry

/-- **Sorted property**: Result is sorted in ascending order. -/
def sorted_prop (l : List Nat) : Prop :=
  let result := unique (l) (by simp)
  ∀ i j : Nat, i < j → j < result.length → result[i]! ≤ result[j]!

/-- **Sorted theorem**: Result is sorted in ascending order. -/
@[simp] theorem sorted_thm (l : List Nat) : sorted_prop l := by
  sorry

/-- **Membership property**: All result elements were in the original list. -/
def membership_prop (l : List Nat) : Prop := ∀ x ∈ unique (l) (by simp), x ∈ l

/-- **Membership theorem**: All result elements were in the original list. -/
@[simp] theorem membership_thm (l : List Nat) : membership_prop l := by
  sorry

/-- **Completeness property**: All original elements appear in result (no loss). -/
def completeness_prop (l : List Nat) : Prop := ∀ x ∈ l, x ∈ unique (l) (by simp)

/-- **Completeness theorem**: All original elements appear in result (no loss). -/
@[simp] theorem completeness_thm (l : List Nat) : completeness_prop l := by
  sorry

-- !benchmark @end proof_aux

theorem unique_spec_satisfied (l : List Nat) (h_precond : unique_precond (l)) :
    unique_postcond (l) (unique (l) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof