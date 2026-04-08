import Mathlib.Data.List.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.LibrarySearch

/-- Evaluate a polynomial with coefficients `xs` at point `x`. -/
def poly (xs : List Float) (x : Float) : Float :=
  let rec loop (acc p : Float) (cs : List Float) : Float :=
    match cs with
    | [] => acc
    | c :: rest => loop (acc + c * p) (p * x) rest
  loop 0.0 1.0 xs

/-- Check if the inputs satisfy the precondition for `findZero`. -/
def pre (xs : List Float) (a b : Float) (fuel : Nat) : Bool :=
  xs.length > 0 && a < b && poly xs a * poly xs b ≤ 0

/-- Find an approximate root of a polynomial using bisection method. -/
def findZero (xs : List Float) (a b : Float) (fuel : Nat) : Float :=
  if !pre xs a b fuel then
    panic! "Invalid inputs or bracket does not contain a root"
  else
    let rec bisect (left right : Float) (remaining : Nat) : Float :=
      if remaining = 0 then
        (left + right) / 2.0
      else
        let mid := (left + right) / 2.0
        let f_mid := poly xs mid
        if f_mid.abs < 1e-10 then
          mid
        else if poly xs left * f_mid ≤ 0 then
          bisect left mid (remaining - 1)
        else
          bisect mid right (remaining - 1)
    bisect a b fuel

/-- Test cases for the `findZero` function. -/
def test : Bool :=
  -- Basic unit tests (close to expected roots)
  let r1 := findZero [1.0, 2.0] (-1.0) 0.0 100
  let _ := assert! (r1 + 0.5).abs < 1e-2

  let r2 := findZero [-6.0, 11.0, -6.0, 1.0] 0.0 2.0 100
  let _ := assert! (r2 - 1.0).abs < 1e-2

  -- Edge unit tests
  let r3 := findZero [0.0, 1.0] (-1.0) 1.0 100
  let _ := assert! (r3 - 0.0).abs < 1e-2

  let r4 := findZero [4.0, -4.0, 1.0] 1.0 3.0 100
  let _ := assert! (r4 - 2.0).abs < 1e-2

  true

/-- Run the tests -/
#eval test

/-- Formal specification of what it means for a value to be a root of a polynomial. -/
def isRoot (xs : List Float) (r : Float) : Prop :=
  poly xs r = 0

/-- Formal specification of what it means for a bracket to contain a root. -/
def bracketContainsRoot (xs : List Float) (a b : Float) : Prop :=
  a < b ∧ poly xs a * poly xs b ≤ 0

/-- Formal specification that the result is an approximate root. -/
def isApproxRoot (xs : List Float) (r : Float) (epsilon : Float) : Prop :=
  (poly xs r).abs < epsilon

/-- The main correctness theorem for findZero. -/
theorem findZero_correct (xs : List Float) (a b : Float) (fuel : Nat) :
    pre xs a b fuel → 
    (∃ epsilon > 0, isApproxRoot xs (findZero xs a b fuel) epsilon) ∧
    a ≤ findZero xs a b fuel ∧ findZero xs a b fuel ≤ b :=
  sorry
