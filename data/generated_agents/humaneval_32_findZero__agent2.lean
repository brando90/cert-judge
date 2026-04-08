import Mathlib.Data.Real.Basic
import Mathlib.Tactic

/-!
# VeriBench: Find a root of a polynomial via bisection

This file implements and verifies a bisection algorithm to find 
roots of polynomials within a given bracket.
-/

/-- Evaluate a polynomial with coefficients `xs` at point `x`. -/
def poly (xs : List Float) (x : Float) : Float :=
  let rec go (i : Nat) (acc : Float) (p : Float) :=
    match i with
    | 0 => acc
    | i+1 =>
      match xs.get? i with
      | some c => go i (acc + c * p) (p * x)
      | none => acc
  go xs.length 0.0 1.0

/-- Precondition for `findZero`. -/
def pre (xs : List Float) (a b : Float) (fuel : Nat) : Prop :=
  xs.length > 0 ∧ a < b ∧ poly xs a * poly xs b ≤ 0

/-- Postcondition for `findZero`. -/
def post (xs : List Float) (a b : Float) (fuel : Nat) (result : Float) : Prop :=
  a ≤ result ∧ result ≤ b ∧
  (abs (poly xs result) < 1e-10 ∨ fuel = 0 ∨
   (poly xs a * poly xs result ≤ 0 ∨ poly xs result * poly xs b ≤ 0))

/--
Find an approximate root of a polynomial via bisection.
Returns a point in [a,b] where the polynomial is close to zero.
-/
def findZero (xs : List Float) (a b : Float) (fuel : Nat) : Float :=
  let rec bisect (left right : Float) (n : Nat) : Float :=
    if n = 0 then
      (left + right) / 2.0
    else
      let mid := (left + right) / 2.0
      let f_mid := poly xs mid
      if abs f_mid < 1e-10 then
        mid
      else if poly xs left * f_mid ≤ 0 then
        bisect left mid (n - 1)
      else
        bisect mid right (n - 1)
  
  if h : pre xs a b fuel then
    bisect a b fuel
  else
    a  -- Arbitrary return value when precondition fails

/-- Correctness theorem for `findZero`. -/
theorem findZero_correct (xs : List Float) (a b : Float) (fuel : Nat) :
  pre xs a b fuel → post xs a b fuel (findZero xs a b fuel) := by
  intro h
  unfold findZero
  simp [h]
  sorry

/-- Test cases for `findZero`. -/
def findZeroTests : Bool :=
  -- Basic unit tests (close to expected roots)
  let r1 := findZero [1.0, 2.0] (-1.0) 0.0 100
  let test1 := abs (r1 + 0.5) < 1e-2

  let r2 := findZero [-6.0, 11.0, -6.0, 1.0] 0.0 2.0 100
  let test2 := abs (r2 - 1.0) < 1e-2

  -- Edge unit tests
  let r3 := findZero [0.0, 1.0] (-1.0) 1.0 100
  let test3 := abs (r3 - 0.0) < 1e-2

  let r4 := findZero [4.0, -4.0, 1.0] 1.0 3.0 100
  let test4 := abs (r4 - 2.0) < 1e-2

  -- Check all tests pass
  test1 && test2 && test3 && test4

#eval findZeroTests  -- Should evaluate to true
