/-
# Benchmark Task: Median of a Sample

This module provides functions for calculating the median (middle value)
of data, sourced from Python's standard `statistics` library.

The primary function to verify is `benchmark_median`, which computes the
median of a non-empty iterable of numeric data.
-/

import Std
import Mathlib.Data.Rat.Defs

namespace VeriBenchStatisticsMedian

/-
# Implementation
-/

/-- Insert an element into a sorted list. -/
def insertSorted (x : Rat) : List Rat → List Rat
| [] => [x]
| y :: ys =>
    if x ≤ y then
      x :: y :: ys
    else
      y :: insertSorted x ys

/-- Simple insertion sort (stable, nondecreasing order). -/
def sortData : List Rat → List Rat
| [] => []
| x :: xs => insertSorted x (sortData xs)

/-- Safe indexing with default `0` (valid indices are guaranteed by the precondition). -/
def nthOrZero (xs : List Rat) (idx : Nat) : Rat :=
  (xs.get? idx).getD 0

/-- Arithmetic mean of two rationals. -/
def avg2 (a b : Rat) : Rat :=
  (a + b) / 2

/-- Median of a list following Python's definition. Empty input defaults to 0. -/
def median (data : List Rat) : Rat :=
  let sorted := sortData data
  let n := sorted.length
  if _h : n = 0 then
    0
  else if _ : n % 2 = 1 then
    nthOrZero sorted (n / 2)
  else
    let mid := n / 2
    let leftIdx := mid - 1
    avg2 (nthOrZero sorted leftIdx) (nthOrZero sorted mid)

/-- Low median: for even sizes, return the lower middle element. -/
def median_low (data : List Rat) : Rat :=
  let sorted := sortData data
  let n := sorted.length
  if _h : n = 0 then
    0
  else if _ : n % 2 = 1 then
    nthOrZero sorted (n / 2)
  else
    let mid := n / 2
    let idx := mid - 1
    nthOrZero sorted idx

/-- High median: for even sizes, return the upper middle element. -/
def median_high (data : List Rat) : Rat :=
  let sorted := sortData data
  let n := sorted.length
  if _h : n = 0 then
    0
  else
    nthOrZero sorted (n / 2)

/-- Benchmark entry point mirroring Python's `median`. -/
def benchmark_median (data : List Rat) : Rat :=
  median data

/-- Helper: raise `10` to a natural power. -/
def pow10 (n : Nat) : Nat := Nat.pow 10 n

/-- Parse a decimal string (e.g., `"3.65"`) into a rational. -/
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

/-- Mimic Decimal literals by parsing strings (unknown inputs map to 0). -/
def D (spec : String) : Rat :=
  (decimalStringToRat? spec).getD 0

/-- Common fraction constructor mirroring Python's `Fraction`. -/
def F (n d : Nat) : Rat :=
  if d = 0 then 0 else (n : Rat) / (d : Rat)


/-
# Tests
-/

/-- Odd number of data points with integers. -/
example :
    benchmark_median [(1 : Rat), 2, 3, 4, 5, 6, 9] = 4 := by
  native_decide

/-- Odd number of data points with fractions. -/
example :
    benchmark_median [F 1 7, F 2 7, F 3 7, F 4 7, F 5 7] = F 3 7 := by
  native_decide

/-- Odd number of data points with decimal-style inputs. -/
example :
    benchmark_median [D "2.5", D "3.1", D "4.2", D "5.7", D "5.8"] = D "4.2" := by
  native_decide

/-- Even number of data points with integers. -/
example :
    benchmark_median [(1 : Rat), 2, 3, 4, 5, 6] = (7 : Rat) / 2 := by
  native_decide

/-- Even number of data points with fractions. -/
example :
    benchmark_median [F 1 7, F 2 7, F 3 7, F 4 7, F 5 7, F 6 7] = F 1 2 := by
  native_decide

/-- Even number of data points with decimals. -/
example :
    benchmark_median [D "1.2", D "2.5", D "3.1", D "4.2", D "5.7", D "5.8"] = D "3.65" := by
  native_decide

/-- Single-value list returns that value. -/
example :
    benchmark_median [42] = (42 : Rat) := by
  native_decide

/-- Idempotence under duplication mirrors the Python property test. -/
example :
    let data : List Rat := [15, 25, 975].map (fun x : Nat => (x : Rat) / 10)
    let duplicated := data.foldr (fun x acc => x :: x :: acc) []
    benchmark_median duplicated = benchmark_median data := by
  native_decide


/-
# Pre-condition
-/

/-- Inputs must form a non-empty list or tuple of supported numbers. -/
def Pre (data : List Rat) : Prop :=
  data ≠ []

/-- Negative scenario: empty list violates the precondition. -/
example :
    ¬ Pre ([] : List Rat) := by
  simp [Pre]


/-
# Property Theorems
-/

/-- Specification property capturing the median selection logic. -/
def median_spec_prop (data : List Rat) : Prop :=
  Pre data →
    let sorted := sortData data
    let n := sorted.length
    if n % 2 = 1 then
      benchmark_median data = nthOrZero sorted (n / 2)
    else
      let mid := n / 2
      benchmark_median data = avg2 (nthOrZero sorted (mid - 1)) (nthOrZero sorted mid)

/-- Duplication property: repeating entries in pairs leaves the median unchanged. -/
def duplication_prop (data : List Rat) : Prop :=
  Pre data →
    let duplicated := data.foldr (fun x acc => x :: x :: acc) []
    benchmark_median duplicated = benchmark_median data

/-- Proof placeholder: specification theorem. -/
theorem median_spec_thm (data : List Rat) :
    median_spec_prop data := by
  sorry

/-- Proof placeholder: duplication theorem. -/
theorem duplication_thm (data : List Rat) :
    duplication_prop data := by
  sorry


/-
# Post-condition
-/

/-- Combined post-condition bundling specification and duplication invariance. -/
def Post (data : List Rat) : Prop :=
  median_spec_prop data ∧
  duplication_prop data


/-
# Correctness Theorem
-/

/-- Correctness: the precondition implies the bundled post-condition. -/
theorem correctness_thm (data : List Rat) (hPre : Pre data) :
    Post data := by
  have _ := hPre
  refine And.intro ?spec ?dup
  · exact median_spec_thm data
  · exact duplication_thm data

end VeriBenchStatisticsMedian
