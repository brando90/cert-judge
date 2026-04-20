-- !benchmark @start import type=solution
import Mathlib
namespace MyEvenList
-- !benchmark @end import

-- !benchmark @start solution_aux
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def myEvenList_precond (xs : List Int) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
-- !benchmark @end code_aux

def myEvenList : List Int → List Int :=
  List.filter (fun x => x % 2 = 0)

def myEvenList (xs : List Int) (h_precond : myEvenList_precond (xs)) : List Int :=
  -- !benchmark @start code
  List.filter (fun x => x % 2 = 0) xs
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux

@[reducible, simp]
def myEvenList_postcond (xs : List Int) (result : List Int) (h_precond : myEvenList_precond (xs)) :=
  -- !benchmark @start postcond
  (∀ x, x ∈ result → x % 2 = 0) ∧
  (∀ x, x ∈ result → x ∈ xs) ∧
  (∀ x, result.count x = if x % 2 = 0 then xs.count x else 0) ∧
  (myEvenList result (by simp) = result)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

/-- **All even property**: All elements in the result are even. -/
def all_even_prop (xs : List Int) : Prop := ∀ x ∈ myEvenList xs (by simp), x % 2 = 0

/-- **All even theorem**: All elements in the result are even. -/
@[simp] theorem all_even_thm (xs : List Int) : all_even_prop xs := by
  sorry

/-- **Subset property**: All elements in the result are from the input. -/
def subset_prop (xs : List Int) : Prop := ∀ x ∈ myEvenList xs (by simp), x ∈ xs

/-- **Subset theorem**: All elements in the result are from the input. -/
@[simp] theorem subset_thm (xs : List Int) : subset_prop xs := by
  sorry

/-- **Multiplicity property**: Output keeps exactly the even occurrences and removes all odd ones. -/
def multiplicity_prop (xs : List Int) : Prop :=
  ∀ x, (myEvenList xs (by simp)).count x = if x % 2 = 0 then xs.count x else 0

/-- **Multiplicity theorem**: Output keeps exactly the even occurrences and removes all odd ones. -/
@[simp] theorem multiplicity_thm (xs : List Int) : multiplicity_prop xs := by
  sorry

/-- **Idempotence property**: Applying the filter twice is the same as once. -/
def idempotent_prop (xs : List Int) : Prop :=
  myEvenList (myEvenList xs (by simp)) (by simp) = myEvenList xs (by simp)

/-- **Idempotence theorem**: Applying the filter twice is the same as once. -/
@[simp] theorem idempotent_thm (xs : List Int) : idempotent_prop xs := by
  sorry

-- !benchmark @end proof_aux

theorem myEvenList_spec_satisfied (xs : List Int) (h_precond : myEvenList_precond (xs)) :
    myEvenList_postcond (xs) (myEvenList (xs) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof