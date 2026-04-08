/-
# Benchmark Task: Sample and Population Variance

This module provides functions for calculating the sample and population
variance of data, sourced from Python's standard `statistics` library.

The primary function to verify is `benchmark_variance`, which computes the
sample variance of an iterable with at least two data points.
-/

import Std
import Mathlib.Data.Rat.Defs

namespace VeriBenchStatisticsVariance

/-
# Implementation
-/

/-- Helper: raise `10` to a natural power. -/
def pow10 (n : Nat) : Nat :=
  Nat.pow 10 n

/-- Parse a decimal string such as `"9.5"` into a rational. Returns `none` if malformed. -/
def decimalStringToRat? (s : String) : Option Rat := do
  let trimmed := s.trim
  if trimmed = "" then
    none
  else
    let neg := trimmed.startsWith "-"
    let core := if neg then trimmed.drop 1 else trimmed
    let parts := core.splitOn "."
    match parts with
    | [intPart] =>
        let intVal ← String.toNat? intPart
        let value : Rat := (intVal : Rat)
        pure (if neg then -value else value)
    | [intPart, fracPart] =>
        let intVal ← String.toNat? intPart
        let fracVal ← String.toNat? fracPart
        let denom := pow10 fracPart.length
        if denom = 0 then
          none
        else
          let base : Rat := (intVal : Rat)
          let fractional : Rat := (fracVal : Rat) / (denom : Rat)
          let value := base + fractional
          pure (if neg then -value else value)
    | _ => none

/-- Interpret a string literal as a rational to mimic Decimal inputs. Unknown inputs map to 0. -/
def D (spec : String) : Rat :=
  (decimalStringToRat? spec).getD 0

/-- Construct a rational from a Python-style fraction `Fraction(n, d)`. -/
def F (n d : Nat) : Rat :=
  if d = 0 then 0 else (n : Rat) / (d : Rat)

/-- Sum all rationals in the list. -/
def sumRat (xs : List Rat) : Rat :=
  xs.foldl (· + ·) 0

/-- Arithmetic mean of a non-empty list (guards against empty input with a default of 0). -/
def mean (data : List Rat) : Rat :=
  let n := data.length
  if _h : n = 0 then
    0
  else
    sumRat data / (n : Rat)

/-- Sample variance using the two-pass, exact rational computation. -/
def benchmark_variance (data : List Rat) : Rat :=
  let n := data.length
  if _h : n < 2 then
    0
  else
    let μ : Rat := mean data
    let ssd :=
      data.foldl (fun acc x =>
        let diff := x - μ
        acc + diff * diff) 0
    ssd / ((n - 1) : Rat)


/-
# Tests
-/

/-- Basic unit test with integers (expected variance 30). -/
example :
    benchmark_variance [(4 : Rat), 7, 13, 16] = (30 : Rat) := by
  native_decide

/-- Fractions average to the expected sample variance. -/
example :
    benchmark_variance [F 1 4, F 1 4, F 3 4, F 7 4] = F 1 2 := by
  native_decide

/-- Decimal-style inputs match the Python expectation (38 / 3). -/
example :
    benchmark_variance [(2 : Rat), 2, 7, 9] = (38 : Rat) / 3 := by
  native_decide

/-- Minimum data points (two values) give variance 1/2. -/
example :
    benchmark_variance [(1 : Rat), 2] = (1 : Rat) / 2 := by
  native_decide

/-- Constant data has zero variance. -/
example :
    benchmark_variance [(7 : Rat), 7, 7, 7] = 0 := by
  native_decide

/-- Shift invariance mirrors Python's property check. -/
example :
    let raw : List Rat := [1, 3, 3, 4, 5, 7, 9, 10, 11, 16].map (fun x : Nat => (x : Rat))
    let c : Rat := 1000000000
    benchmark_variance (raw.map (· + c)) = benchmark_variance raw := by
  native_decide


/-
# Pre-condition
-/

/-- Inputs must contain at least two numeric elements. -/
def Pre (data : List Rat) : Prop :=
  data.length ≥ 2

/-- Negative scenario: singleton list violates the precondition. -/
example :
    ¬ Pre ([42] : List Rat) := by
  simp [Pre]


/-
# Property Theorems
-/

/-- Specification property: sample variance equals squared deviation sum over `n - 1`. -/
def variance_spec_prop (data : List Rat) : Prop :=
  Pre data →
    let n := data.length
    let μ := mean data
    let ssd :=
      data.foldl (fun acc x =>
        let diff := x - μ
        acc + diff * diff) 0
    benchmark_variance data = ssd / ((n - 1) : Rat)

/-- Shift invariance property for the sample variance. -/
def shift_invariance_prop (data : List Rat) (c : Rat) : Prop :=
  Pre data →
    benchmark_variance (data.map (· + c)) = benchmark_variance data

/-- Proof placeholder: specification theorem. -/
theorem variance_spec_thm (data : List Rat) :
    variance_spec_prop data := by
  sorry

/-- Proof placeholder: shift invariance theorem. -/
theorem shift_invariance_thm (data : List Rat) (c : Rat) :
    shift_invariance_prop data c := by
  sorry


/-
# Post-condition
-/

/-- Combined post-condition bundling the spec and shift invariance properties. -/
def Post (data : List Rat) (c : Rat) : Prop :=
  variance_spec_prop data ∧
  shift_invariance_prop data c


/-
# Correctness Theorem
-/

/-- Correctness: valid inputs satisfy the bundled post-condition. -/
theorem correctness_thm (data : List Rat) (c : Rat) (hPre : Pre data) :
    Post data c := by
  have _ := hPre
  refine And.intro ?spec ?shift
  · exact variance_spec_thm data
  · exact shift_invariance_thm data c

end VeriBenchStatisticsVariance
