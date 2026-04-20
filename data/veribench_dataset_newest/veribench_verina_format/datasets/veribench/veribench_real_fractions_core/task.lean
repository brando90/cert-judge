-- !benchmark @start import type=solution
import Mathlib
namespace VeriBenchFractionsCore
-- !benchmark @end import

open Std

/-- Alias the underlying canonical rational numbers. -/
abbrev Fraction := Rat

namespace Fraction

/-- Construct a normalized fraction from integers (denominator defaults to 1). -/
def mk (numerator : Int) (denominator : Int := 1) : Fraction :=
  if denominator = 0 then
    0
  else
    let denomAbs := Int.natAbs denominator
    let adjNumerator := if denominator < 0 then -numerator else numerator
    (adjNumerator : Rat) / (denomAbs : Rat)

/-- Access the numerator (matches Python's API). -/
def numerator (f : Fraction) : Int :=
  f.num

/-- Access the denominator as an integer (always positive). -/
def denominator (f : Fraction) : Int :=
  Int.ofNat f.den

/-- Underlying positive denominator as a natural number. -/
def denominatorNat (f : Fraction) : Nat :=
  f.den

end Fraction

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def benchmark_fraction_precond (numerator : Int) (denominator : Int) : Prop :=
  -- !benchmark @start precond
  denominator ≠ 0
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

/-- Alias matching the Python naming. -/
def benchmark_fraction (numerator : Int) (denominator : Int) (h_precond : benchmark_fraction_precond (numerator) (denominator)) : Fraction :=
  -- !benchmark @start code
  Fraction.mk numerator denominator
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def benchmark_fraction_postcond (numerator : Int) (denominator : Int) (result : Fraction)
    (h_precond : benchmark_fraction_precond (numerator) (denominator)) : Prop :=
  -- !benchmark @start postcond
  result = Fraction.mk numerator denominator
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem benchmark_fraction_spec_satisfied (numerator : Int) (denominator : Int)
    (h_precond : benchmark_fraction_precond (numerator) (denominator)) :
    benchmark_fraction_postcond (numerator) (denominator) (benchmark_fraction (numerator) (denominator) h_precond) h_precond := by
  -- !benchmark @start proof
  simp [benchmark_fraction, benchmark_fraction_postcond]
  -- !benchmark @end proof

end VeriBenchFractionsCore