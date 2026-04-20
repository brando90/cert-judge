-- !benchmark @start import type=solution
import Mathlib
namespace StatisticsMedianHigh
-- !benchmark @end import

-- !benchmark @start solution_aux
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def benchmark_median_high_precond (data : List Int) : Prop :=
  -- !benchmark @start precond
  data ≠ []
  -- !benchmark @end precond

-- !benchmark @start code_aux
/-- Safe indexing: return element at `idx`, or 0 if out of bounds. -/
def nthOrZero (xs : List Int) (idx : Nat) : Int :=
  (xs[idx]?).getD 0

/--
Implementation of `median_high`.

`median_high data` returns the high median of numeric data.
-/
def median_high (data : List Int) : Int :=
  let sorted := data.mergeSort (· ≤ ·)
  let n := sorted.length
  if n == 0 then
    0
  else
    nthOrZero sorted (n / 2)
-- !benchmark @end code_aux

def benchmark_median_high (data : List Int) (h_precond : benchmark_median_high_precond (data)) : Int :=
  -- !benchmark @start code
  median_high data
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux

@[reducible, simp]
def benchmark_median_high_postcond (data : List Int) (result : Int)
    (h_precond : benchmark_median_high_precond (data)) : Prop :=
  -- !benchmark @start postcond
  let odd_index_prop (data : List Int) : Prop :=
    benchmark_median_high_precond data →
      let sorted := data.mergeSort (· ≤ ·)
      let n := sorted.length
      n % 2 = 1 → benchmark_median_high data (by simp) = nthOrZero sorted (n / 2)
  let even_index_prop (data : List Int) : Prop :=
    benchmark_median_high_precond data →
      let sorted := data.mergeSort (· ≤ ·)
      let n := sorted.length
      n % 2 = 0 → benchmark_median_high data (by simp) = nthOrZero sorted (n / 2)
  let permutation_invariance_prop (data : List Int) : Prop :=
    ∀ perm, List.Perm perm data → benchmark_median_high perm (by sorry) = benchmark_median_high data (by simp)
  let shift_invariance_prop (data : List Int) (c : Int) : Prop :=
    benchmark_median_high_precond data →
      benchmark_median_high (data.map (fun x => x + c)) (by sorry) = benchmark_median_high data (by simp) + c
  result = benchmark_median_high data h_precond ∧
    (odd_index_prop data) ∧
    (even_index_prop data) ∧
    (permutation_invariance_prop data) ∧
    (∀ c, shift_invariance_prop data c)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
-- Property theorems (kept as auxiliary proof material; proofs omitted)

def odd_index_prop (data : List Int) : Prop :=
  benchmark_median_high_precond data →
    let sorted := data.mergeSort (· ≤ ·)
    let n := sorted.length
    n % 2 = 1 → benchmark_median_high data (by simp) = nthOrZero sorted (n / 2)

theorem odd_index_thm (data : List Int) : odd_index_prop data := by
  sorry

def even_index_prop (data : List Int) : Prop :=
  benchmark_median_high_precond data →
    let sorted := data.mergeSort (· ≤ ·)
    let n := sorted.length
    n % 2 = 0 → benchmark_median_high data (by simp) = nthOrZero sorted (n / 2)

theorem even_index_thm (data : List Int) : even_index_prop data := by
  sorry

def permutation_invariance_prop (data : List Int) : Prop :=
  ∀ perm, List.Perm perm data → benchmark_median_high perm (by sorry) = benchmark_median_high data (by simp)

theorem permutation_invariance_thm (data : List Int) : permutation_invariance_prop data := by
  sorry

def shift_invariance_prop (data : List Int) (c : Int) : Prop :=
  benchmark_median_high_precond data →
    benchmark_median_high (data.map (fun x => x + c)) (by sorry) = benchmark_median_high data (by simp) + c

theorem shift_invariance_thm (data : List Int) (c : Int) : shift_invariance_prop data c := by
  sorry
-- !benchmark @end proof_aux

theorem benchmark_median_high_spec_satisfied (data : List Int) (h_precond : benchmark_median_high_precond (data)) :
    benchmark_median_high_postcond (data) (benchmark_median_high (data) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof