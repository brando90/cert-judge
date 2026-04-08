import Mathlib.Data.Int.Order.Basic

/--
Multiply two 2x2 matrices represented as tuples (a11, a12, a21, a22).
-/
def matrixMultiply (a b : Int × Int × Int × Int) : Int × Int × Int × Int :=
  let (a11, a12, a21, a22) := a
  let (b11, b12, b21, b22) := b
  (
    a11 * b11 + a12 * b21,  -- c11
    a11 * b12 + a12 * b22,  -- c12
    a21 * b11 + a22 * b21,  -- c21
    a21 * b12 + a22 * b22   -- c22
  )

/--
Compute matrix^n using binary exponentiation.
-/
def matrixPower (matrix : Int × Int × Int × Int) (n : Nat) : Int × Int × Int × Int :=
  match n with
  | 0 => (1, 0, 0, 1)  -- Identity matrix
  | 1 => matrix
  | n =>
      let half := matrixPower matrix (n / 2)
      let result := matrixMultiply half half
      if n % 2 == 1 then
        matrixMultiply result matrix
      else
        result

/--
Computes the nth Fibonacci number using matrix exponentiation.
The Fibonacci sequence is defined as:
F(0) = 0
F(1) = 1
F(n) = F(n-1) + F(n-2) for n > 1

This implementation uses matrix exponentiation for O(log n) time complexity.

Precondition: n must be a non-negative integer

Returns: The nth Fibonacci number
-/
def fastFibonacci (n : Int) : Int :=
  if n < 0 then
    panic! "Input must be non-negative integer"
  else if n <= 1 then
    n
  else
    -- The Fibonacci matrix: [[1, 1], [1, 0]]
    let fibMatrix : Int × Int × Int × Int := (1, 1, 1, 0)
    
    -- Compute matrix^(n-1)
    let resultMatrix := matrixPower fibMatrix (n.toNat - 1)
    
    -- The nth Fibonacci number is the top-left element of matrix^(n-1)
    resultMatrix.1

/--
Precondition for fastFibonacci: n must be a non-negative integer
-/
def fastFibonacci.pre (n : Int) : Prop :=
  n >= 0

/--
Postcondition for fastFibonacci: result is the nth Fibonacci number
-/
def fastFibonacci.post (n : Int) (result : Int) : Prop :=
  match n.toNat with
  | 0 => result = 0
  | 1 => result = 1
  | n+2 => result = fastFibonacci (n+1) + fastFibonacci n

/--
Recursive definition of Fibonacci numbers for verification
-/
def fib : Nat → Int
  | 0 => 0
  | 1 => 1
  | n+2 => fib (n+1) + fib n

/--
The implementation of fastFibonacci correctly computes the nth Fibonacci number
-/
theorem fastFibonacci_correct (n : Int) (h : fastFibonacci.pre n) : 
  fastFibonacci.post n (fastFibonacci n) := by
  sorry

/--
Tests for fastFibonacci
-/
def fastFibonacci.tests : List (Int × Int) := [
  (0, 0),
  (1, 1),
  (2, 1),
  (3, 2),
  (4, 3),
  (5, 5),
  (7, 13),
  (10, 55)
]

/--
Run tests for fastFibonacci
-/
def fastFibonacci.runTests : IO Unit := do
  for (input, expectedOutput) in fastFibonacci.tests do
    let result := fastFibonacci input
    if result != expectedOutput then
      throw (IO.userError s!"Test failed for input {input}: expected {expectedOutput}, got {result}")
    IO.println s!"Test passed for input {input}"
  IO.println "All tests passed!"
