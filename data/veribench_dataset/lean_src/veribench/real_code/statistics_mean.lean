/-
# Benchmark Task: Arithmetic Mean

This module provides a function for calculating the arithmetic mean (average)
of a sample, sourced from Python's standard `statistics` library.

The primary function to verify is `benchmark_mean`, which computes the mean
of a non-empty iterable of numeric data.
-/

import Std
import Mathlib.Data.Rat.Defs

namespace VeriBenchStatisticsMean

/-
# Implementation
-/

/-- Helper: raise `10` to a natural power. -/
def pow10 (n : Nat) : Nat :=
  Nat.pow 10 n

/-- Parse a decimal string like `"0.5"` into a Lean rational. Returns `none` on malformed input. -/
def decimalStringToRat? (s : String) : Option Rat := do
  let trimmed := s.trim
  let neg := trimmed.startsWith "-"
  let core := if neg then trimmed.drop 1 else trimmed
  let parts := core.splitOn "."
  match parts with
  | [intPart] =>
      let i ← String.toNat? intPart
      let value : Rat := (i : Rat)
      pure (if neg then -value else value)
  | [intPart, fracPart] =>
      let i ← String.toNat? intPart
      let f ← String.toNat? fracPart
      let denom := pow10 fracPart.length
      let base : Rat := (i : Rat)
      let fractional : Rat :=
        if denom = 0 then
          0
        else
          (f : Rat) / (denom : Rat)
      let value : Rat := base + fractional
      pure (if neg then -value else value)
  | _ => none

/-- Interpret a string literal as a rational (used to mimic Decimal inputs). Unknown inputs map to 0. -/
def D (s : String) : Rat :=
  (decimalStringToRat? s).getD 0

/-- Construct a rational from a Python-style fraction `Fraction(n, d)`. -/
def F (n d : Nat) : Rat :=
  if d = 0 then 0 else (n : Rat) / (d : Rat)

/-- Sum of rationals. -/
def sumRat (xs : List Rat) : Rat :=
  xs.foldl (· + ·) 0

/-- Arithmetic mean of a list of rationals. Empty list returns 0 (guarded by `Pre`). -/
def benchmark_mean (data : List Rat) : Rat :=
  let n := data.length
  if _h : n = 0 then
    0
  else
    sumRat data / (n : Rat)

/-
# Tests
-/

/-- Basic unit test with integers (expected 14/5). -/
example :
    benchmark_mean [(1 : Rat), 2, 3, 4, 4] = (14 : Rat) / 5 := by
  native_decide

/-- Fractions combine correctly (expected 13/21). -/
example :
    benchmark_mean [F 3 7, F 1 21, F 5 3, F 1 3] = (13 : Rat) / 21 := by
  native_decide

/-- Decimal strings (treated as rationals) average correctly. -/
example :
    benchmark_mean [D "0.5", D "0.75", D "0.625", D "0.375"] = D "0.5625" := by
  native_decide

/-- Single-value list returns that value. -/
example :
    benchmark_mean [85 / (2 : Rat)] = 85 / (2 : Rat) := by
  native_decide

/-- All-equal entries return that value. -/
example :
    benchmark_mean [(17 : Rat), 17, 17, 17] = 17 := by
  native_decide

/-- Shift invariance property mirrors Python's floating-point check. -/
example :
    let data : List Rat := [34, 45, 49, 67, 68, 72, 80, 81, 94] |>.map (fun x => (x : Rat) / 10)
    let c : Rat := 1000000000
    benchmark_mean (data.map (· + c)) = benchmark_mean data + c := by
  native_decide

/-
# Pre-condition
-/

/-- Inputs must be non-empty (mirroring the Python precondition). -/
def Pre (data : List Rat) : Prop :=
  data ≠ []

/-- Negative scenario: empty list violates the precondition. -/
example :
    ¬ Pre ([] : List Rat) := by
  simp [Pre]


/-
# Property Theorems
-/

/-- Specification property: mean equals sum divided by count for non-empty data. -/
def mean_spec_prop (data : List Rat) : Prop :=
  Pre data →
    benchmark_mean data = sumRat data / (data.length : Rat)

/-- Shift invariance property. -/
def shift_invariance_prop (data : List Rat) (c : Rat) : Prop :=
  Pre data →
    benchmark_mean (data.map (· + c)) = benchmark_mean data + c

/-- Proof placeholder: specification theorem. -/
theorem mean_spec_thm (data : List Rat) :
    mean_spec_prop data := by
  sorry

/-- Proof placeholder: shift invariance theorem. -/
theorem shift_invariance_thm (data : List Rat) (c : Rat) :
    shift_invariance_prop data c := by
  sorry


/-
# Post-condition
-/

/-- Combined post-condition bundling key properties. -/
def Post (data : List Rat) (c : Rat) : Prop :=
  mean_spec_prop data ∧
  shift_invariance_prop data c


/-
# Correctness Theorem
-/

/-- Correctness: valid inputs satisfy the bundled post-condition. -/
theorem correctness_thm (data : List Rat) (c : Rat) (hPre : Pre data) :
    Post data c := by
  have _ := hPre
  refine And.intro ?spec ?shift
  · exact mean_spec_thm data
  · exact shift_invariance_thm data c

end VeriBenchStatisticsMean
