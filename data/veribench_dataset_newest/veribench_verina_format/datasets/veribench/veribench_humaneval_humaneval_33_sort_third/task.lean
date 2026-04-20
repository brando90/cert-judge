-- !benchmark @start import type=solution
import Mathlib
namespace SortThird
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def sort_third_precond (l : List Int) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond


-- !benchmark @start code_aux
/-- Helper function to sort a list using insertion sort -/
def insertionSort (l : List Int) : List Int :=
  let rec insert (x : Int) (l : List Int) : List Int :=
    match l with
    | [] => [x]
    | h :: t => if x ≤ h then x :: h :: t else h :: (insert x t)

  let rec sort (l : List Int) : List Int :=
    match l with
    | [] => []
    | h :: t => insert h (sort t)

  sort l
-- !benchmark @end code_aux


def sort_third (l : List Int) (h_precond : sort_third_precond (l)) : List Int :=
  -- !benchmark @start code
  let indices := List.range l.length
  let third_indices := indices.filter (fun i => i % 3 = 0)
  let third_values := third_indices.map (fun i => l[i]!)
  let sorted_third := insertionSort third_values
  let rec update_list (curr : List Int) (pos : List Nat) (vals : List Int) : List Int :=
    match pos, vals with
    | [], _ => curr
    | _, [] => curr
    | p :: ps, v :: vs =>
      let new_curr := curr.set p v
      update_list new_curr ps vs

  update_list l third_indices sorted_third
  -- !benchmark @end code


-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux


@[reducible, simp]
def sort_third_postcond (l : List Int) (result : List Int) (h_precond : sort_third_precond (l)) :=
  -- !benchmark @start postcond
  let length_preservation_prop : Prop := result.length = l.length
  let non_third_preservation_prop : Prop :=
    ∀ i, i < l.length → i % 3 ≠ 0 → result[i]! = l[i]!
  let third_sorting_prop : Prop :=
    ∀ i j,
      i < l.length →
      j < l.length →
      i % 3 = 0 →
      j % 3 = 0 →
      i < j →
      result[i]! ≤ result[j]!
  let idempotent_prop : Prop :=
    sort_third (result) (by simp) = result
  length_preservation_prop ∧
    non_third_preservation_prop ∧
    third_sorting_prop ∧
    idempotent_prop
  -- !benchmark @end postcond


-- !benchmark @start proof_aux

-- !benchmark @end proof_aux


theorem sort_third_spec_satisfied (l : List Int) (h_precond : sort_third_precond (l)) :
    sort_third_postcond (l) (sort_third (l) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof
end SortThird