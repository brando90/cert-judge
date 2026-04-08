/-
# Benchmark Task: Covariance and Correlation

This module provides functions for calculating the sample covariance and
Pearson's correlation coefficient for two variables, sourced from
Python's standard `statistics` library.

The primary function to verify is `benchmark_correlation`.
-/

import Std

namespace VeriBenchStatisticsCorrelation

/-
# Implementation
-/

/-- Sum of a list of floating-point numbers. -/
def sumFloat (xs : List Float) : Float :=
  xs.foldl (· + ·) 0

/-- Pairwise sum of products. Assumes both lists have the same length. -/
def sumProd (xs ys : List Float) : Float :=
  ((List.zip xs ys).foldl (fun acc pair => acc + pair.fst * pair.snd) 0)

/-- Arithmetic mean of a list (defaulting to `0` for empty lists). -/
def mean (xs : List Float) : Float :=
  let n := xs.length
  if _h : n = 0 then
    0
  else
    sumFloat xs / (Float.ofNat n)

/-- Center the data by subtracting the mean. -/
def center (xs : List Float) : List Float :=
  let μ := mean xs
  xs.map (fun x => x - μ)

/-- Sample covariance of two data sequences. -/
def covariance (xs ys : List Float) : Float :=
  let n := xs.length
  let xc := center xs
  let yc := center ys
  let sxy := sumProd xc yc
  if n ≤ 1 then
    0
  else
    sxy / Float.ofNat (n - 1)

/-- Pearson correlation coefficient for two aligned data sets. -/
def correlation (xs ys : List Float) : Float :=
  let xc := center xs
  let yc := center ys
  let sxy := sumProd xc yc
  let sxx := sumProd xc xc
  let syy := sumProd yc yc
  let denom := Float.sqrt (sxx * syy)
  if denom == 0 then
    0
  else
    sxy / denom

/-- Benchmark wrapper enforcing the precondition. -/
def benchmark_correlation (xs ys : List Float) : Float :=
  correlation xs ys


/-
# Tests
-/

/-- Helper for concise float lists. -/
def floats (xs : List Int) : List Float :=
  xs.map (fun x => (Float.ofInt x))

/-- Tolerance for approximate comparisons. -/
def tol : Float := 1e-9

/-- Basic unit test: small sample correlation (approx 0.5). -/
example :
    Float.abs (benchmark_correlation (floats [1, 2, 3]) (floats [1, 3, 2]) - 0.5) < tol := by
  native_decide

/-- Repeating pattern correlation (~ sqrt(1/10)). -/
example :
    Float.abs (
      benchmark_correlation
        (floats [1,2,3,4,5,6,7,8,9])
        (floats [1,2,3,1,2,3,1,2,3])
      - 0.316227766) < tol := by
  native_decide

/-- Perfect positive correlation. -/
example :
    Float.abs (benchmark_correlation (floats [1, 2, 3]) (floats [1, 2, 3]) - 1) < tol := by
  native_decide

/-- Perfect negative correlation. -/
example :
    Float.abs (benchmark_correlation (floats [1, 2, 3]) (floats [-1, -2, -3]) + 1) < tol := by
  native_decide

/-- Reverse order correlation gives -1. -/
example :
    Float.abs (benchmark_correlation (floats [1, 2, 3]) (floats [3, 2, 1]) + 1) < tol := by
  native_decide

/-- Symmetry: corr(x,y) = corr(y,x). -/
example :
    let x := floats [1,2,3,4,5,6,7,8,9]
    let y := floats [9,8,7,6,5,4,3,2,1]
    Float.abs (benchmark_correlation x y - benchmark_correlation y x) < tol := by
  native_decide


/-
# Pre-condition
-/

/-- Both sequences must be lists/tuples of equal length at least two. -/
def Pre (xs ys : List Float) : Prop :=
  xs.length = ys.length ∧ xs.length ≥ 2

/-- Negative scenario: mismatched lengths. -/
example :
    ¬ Pre (floats [1, 2, 3]) (floats [4, 5]) := by
  simp [Pre, floats]

/-- Negative scenario: insufficient data points. -/
example :
    ¬ Pre (floats [1]) (floats [2]) := by
  simp [Pre, floats]


/-
# Property Theorems
-/

/-- Specification property: correlation equals covariance divided by the product of standard deviations. -/
def correlation_spec_prop (xs ys : List Float) : Prop :=
  Pre xs ys →
    let xc := center xs
    let yc := center ys
    let sxy := sumProd xc yc
    let sxx := sumProd xc xc
    let syy := sumProd yc yc
    let denom := Float.sqrt (sxx * syy)
    if denom == 0 then
      benchmark_correlation xs ys = 0
    else
      benchmark_correlation xs ys = sxy / denom

/-- Symmetry property: corr(x,y) = corr(y,x). -/
def symmetry_prop (xs ys : List Float) : Prop :=
  Pre xs ys →
    benchmark_correlation xs ys = benchmark_correlation ys xs

/-- Proof placeholder: specification theorem. -/
theorem correlation_spec_thm (xs ys : List Float) :
    correlation_spec_prop xs ys := by
  sorry

/-- Proof placeholder: symmetry theorem. -/
theorem symmetry_thm (xs ys : List Float) :
    symmetry_prop xs ys := by
  sorry


/-
# Post-condition
-/

/-- Combined post-condition bundling specification and symmetry. -/
def Post (xs ys : List Float) : Prop :=
  correlation_spec_prop xs ys ∧
  symmetry_prop xs ys


/-
# Correctness Theorem
-/

/-- Correctness: valid inputs imply the combined properties. -/
theorem correctness_thm (xs ys : List Float) (hPre : Pre xs ys) :
    Post xs ys := by
  have _ := hPre
  refine And.intro ?spec ?symm
  · exact correlation_spec_thm xs ys
  · exact symmetry_thm xs ys

end VeriBenchStatisticsCorrelation
