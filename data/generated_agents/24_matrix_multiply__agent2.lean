import Mathlib.Algebra.BigOperators.Ring
import Mathlib.Tactic

namespace VeriBench

/-- Matrix multiplication for 2x2 matrices represented as 4-tuples -/
def matrixMultiply (a b : Int × Int × Int × Int) : Int × Int × Int × Int :=
  let (a11, a12, a21, a22) := a
  let (b11, b12, b21, b22) := b
  (a11 * b11 + a12 * b21,  -- c11
   a11 * b12 + a12 * b22,  -- c12
   a21 * b11 + a22 * b21,  -- c21
   a21 * b12 + a22 * b22)  -- c22

/-- Compute matrix^n using binary exponentiation -/
def matrixPower (matrix : Int × Int × Int × Int) (n : Nat) : Int × Int × Int × Int :=
  match n with
  | 0 => (1, 0, 0, 1)  -- Identity matrix
  | 1 => matrix
  | n =>
    let half := matrixPower matrix (n / 2)
    let result := matrixMultiply half half
    if n % 2 = 1 then
      matrixMultiply result matrix
    else
      result

/-- Precondition for fast_fibonacci: n must be non-negative -/
def fastFibonacciPre (n : Int) : Prop :=
  n ≥ 0

/-- The nth Fibonacci number -/
def fibonacci (n : Nat) : Nat :=
  match n with
  | 0 => 0
  | 1 => 1
  | n+2 => fibonacci (n+1) + fibonacci n

/-- Postcondition: fastFibonacci returns the nth Fibonacci number -/
def fastFibonacciPost (n : Int) (result : Int) : Prop :=
  result = fibonacci n.toNat

/-- Fast Fibonacci via 2x2 matrix exponentiation for non-negative n -/
def fastFibonacci (n : Int) : Int :=
  if h : fastFibonacciPre n then
    if n ≤ 1 then
      n
    else
      -- The Fibonacci matrix: [[1, 1], [1, 0]]
      let fibMatrix := (1, 1, 1, 0)
      -- Compute matrix^(n-1)
      let resultMatrix := matrixPower fibMatrix (n.toNat - 1)
      -- The nth Fibonacci number is the top-left element of matrix^(n-1)
      resultMatrix.1
  else
    panic! "Input must be non-negative integer"

/-- Tests for fastFibonacci -/
def fastFibonacciTests : List (Int × Int) := [
  (0, 0),
  (1, 1),
  (2, 1),
  (3, 2),
  (4, 3),
  (5, 5),
  (7, 13)
]

/-- Run tests for fastFibonacci -/
def testFastFibonacci : Bool :=
  fastFibonacciTests.all (fun (input, expected) => fastFibonacci input = expected)

#eval testFastFibonacci -- Should evaluate to true

/-- Correctness theorem for fastFibonacci -/
theorem fastFibonacci_correct (n : Int) (h : fastFibonacciPre n) : 
  fastFibonacciPost n (fastFibonacci n) := by
  -- Unfold definitions
  simp [fastFibonacci, h, fastFibonacciPost]
  -- Split into cases
  by_cases h₁ : n ≤ 1
  · -- Case n ≤ 1
    simp [h₁]
    cases n
    · -- Case n = 0
      simp [fibonacci]
    · -- Case n = 1
      simp [fibonacci]
    · -- Case n < 0
      have : ¬(n < 0) := by linarith [h]
      contradiction
  · -- Case n > 1
    sorry  -- Proof of matrix exponentiation correctness

end VeriBench
