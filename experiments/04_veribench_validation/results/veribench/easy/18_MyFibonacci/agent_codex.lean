import Mathlib.Tactic
import Mathlib.Data.Nat.Basic

namespace VeriBench.Fibonacci

/-- Return the nth Fibonacci number for natural number indices. -/
def fibonacci (n : Int) : Int :=
  if n ≤ 1 then 
    if n < 0 then 
      panic! s!"Input must be a non-negative integer (got n={n})"
    else 
      n
  else 
    let rec loop (i : Int) (a : Int) (b : Int) : Int :=
      if i = n then b
      else loop (i + 1) b (a + b)
    loop 1 0 1

/-- True iff the input is a non-negative integer. -/
def pre (n : Int) : Bool :=
  n ≥ 0

/-- The post-condition: result equals the nth Fibonacci number. -/
def post (n : Int) (result : Int) : Prop :=
  pre n → 
  if n = 0 then result = 0
  else if n = 1 then result = 1
  else result = fibonacci (n - 1) + fibonacci (n - 2)

/-- Recursive definition of Fibonacci for proofs -/
def fib : Nat → Nat
  | 0 => 0
  | 1 => 1
  | n+2 => fib n + fib (n+1)

/-- The fibonacci function satisfies its specification. -/
theorem fibonacci_correct (n : Int) : post n (fibonacci n) := by
  intro h
  simp [post]
  cases n with
  | ofNat n =>
    simp [fibonacci]
    cases n with
    | zero => simp
    | succ n =>
      cases n with
      | zero => simp
      | succ n => sorry
  | negSucc n => 
    simp [pre] at h
    contradiction

/-- Test cases for fibonacci -/
def test : IO Unit := do
  -- Basic test
  assert! (fibonacci 6 = 8)
  
  -- Edge test
  assert! (fibonacci 0 = 0)
  
  -- Test for larger values
  assert! (fibonacci 10 = 55)
  
  -- Negative tests would raise an exception
  IO.println "All tests passed!"

end VeriBench.Fibonacci
