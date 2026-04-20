-- !benchmark @start import type=solution
import Mathlib
namespace StatisticsMedianLow
-- !benchmark @end import

-- !benchmark @start solution_aux
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def benchmark_median_low_precond (data : List Int) : Prop :=
  -- !benchmark @start precond
  data ≠ []
  -- !benchmark @end precond

-- !benchmark @start code_aux
/-- Safe indexing: return element at `idx`, or 0 if out of bounds. -/
def nthOrZero (xs : List Int) (idx : Nat) : Int :=
  (xs[idx]?).getD 0

/--
Implementation of `median_low`.

`median_low data` returns the low median of numeric data.
-/
def median_low (data : List Int) : Int :=
  let sorted := data.mergeSort (· ≤ ·)
  let n := sorted.length
  if n == 0 then
    0
  else if n % 2 == 1 then
    nthOrZero sorted (n / 2)
  else
    nthOrZero sorted (n / 2 - 1)
-- !benchmark @end code_aux

def benchmark_median_low (data : List Int) (h_precond : benchmark_median_low_precond (data)) : Int :=
  -- !benchmark @start code
  median_low data
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux

@[reducible, simp]
def benchmark_median_low_postcond (data : List Int) (result : Int)
    (h_precond : benchmark_median_low_precond (data)) : Prop :=
  -- !benchmark @start postcond
  (Pre : Prop := data ≠ []) →
      (let sorted := data.mergeSort (· ≤ ·)
       let n := sorted.length
       n % 2 = 1 → result = nthOrZero sorted (n / 2)) ∧
    ((Pre : Prop := data ≠ []) →
      (let sorted := data.mergeSort (· ≤ ·)
       let n := sorted.length
       n % 2 = 0 → result = nthOrZero sorted (n / 2 - 1))) ∧
    (∀ perm, List.Perm perm data →
      (benchmark_median_low (perm) (by sorry)) =
        benchmark_median_low (data) h_precond) ∧
    (∀ c, (Pre : Prop := data ≠ []) →
      (benchmark_median_low (data.map (fun x => x + c)) (by sorry)) =
        benchmark_median_low (data) h_precond + c)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
/-- **Odd-length property**: odd length returns the middle element of the sorted list. -/
def odd_index_prop (data : List Int) : Prop :=
  (data ≠ []) →
    let sorted := data.mergeSort (· ≤ ·)
    let n := sorted.length
    n % 2 = 1 → benchmark_median_low data (by sorry) = nthOrZero sorted (n / 2)

theorem odd_index_thm (data : List Int) : odd_index_prop data := by
  sorry

/-- **Even-length property**: even length returns the lower middle element of the sorted list. -/
def even_index_prop (data : List Int) : Prop :=
  (data ≠ []) →
    let sorted := data.mergeSort (· ≤ ·)
    let n := sorted.length
    n % 2 = 0 → benchmark_median_low data (by sorry) = nthOrZero sorted (n / 2 - 1)

theorem even_index_thm (data : List Int) : even_index_prop data := by
  sorry

/-- **Permutation-invariance property**: median is unchanged by reordering. -/
def permutation_invariance_prop (data : List Int) : Prop :=
  ∀ perm, List.Perm perm data → benchmark_median_low perm (by sorry) = benchmark_median_low data (by sorry)

theorem permutation_invariance_thm (data : List Int) : permutation_invariance_prop data := by
  sorry

/-- **Shift-invariance property**: adding a constant shifts the median. -/
def shift_invariance_prop (data : List Int) (c : Int) : Prop :=
  (data ≠ []) →
    benchmark_median_low (data.map (fun x => x + c)) (by sorry) = benchmark_median_low data (by sorry) + c

theorem shift_invariance_thm (data : List Int) (c : Int) : shift_invariance_prop data c := by
  sorry
-- !benchmark @end proof_aux

theorem benchmark_median_low_spec_satisfied (data : List Int)
    (h_precond : benchmark_median_low_precond (data)) :
    benchmark_median_low_postcond (data) (benchmark_median_low (data) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof