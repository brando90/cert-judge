/-
  File: humaneval_46_fib4.lean
  HumanEval problem HumanEval/46
-/

namespace HumanEval46

/-- 
  The Fib4 number sequence is a sequence similar to the Fibbonacci sequnece that's defined as follows:
  fib4(0) -> 0
  fib4(1) -> 0
  fib4(2) -> 2
  fib4(3) -> 0
  fib4(n) -> fib4(n-1) + fib4(n-2) + fib4(n-3) + fib4(n-4).
-/
def fib4 (n : Nat) : Nat :=
  if n < 4 then
    match n with
    | 0 => 0
    | 1 => 0
    | 2 => 2
    | 3 => 0
    | _ => 0 -- unreachable
  else
    let rec loop (i : Nat) (a b c d : Nat) : Nat :=
      if i == n then a
      else loop (i + 1) (a + b + c + d) a b c
    loop 4 2 0 0 0

/-- Specification of fib4 using recursion -/
def fib4_spec (n : Nat) : Nat :=
  match n with
  | 0 => 0
  | 1 => 0
  | 2 => 2
  | 3 => 0
  | n+4 => fib4_spec (n+3) + fib4_spec (n+2) + fib4_spec (n+1) + fib4_spec n

/-- Tests for fib4 -/
def tests : List (Nat × Nat) := [
  (5, 4),
  (8, 28),
  (10, 104),
  (12, 386)
]

/-- Run tests -/
def runTests : IO Unit := do
  for (input, expected) in tests do
    let result := fib4 input
    if result != expected then
      throw (IO.userError s!"Test failed: fib4({input}) = {result}, expected {expected}")
    else
      IO.println s!"Test passed: fib4({input}) = {expected}"
  IO.println "All tests passed!"

/-- Precondition: n is a natural number -/
def pre (_n : Nat) : Prop := True

/-- Postcondition: fib4 returns the correct nth element of the fib4 sequence -/
def post (n : Nat) (result : Nat) : Prop :=
  result = fib4_spec n

/-- Correctness theorem: fib4 satisfies its specification -/
theorem fib4_correct (n : Nat) : pre n → post n (fib4 n) := by
  intro _
  unfold post
  
  -- Base cases
  cases n with
  | zero => simp [fib4, fib4_spec]
  | succ n =>
    cases n with
    | zero => simp [fib4, fib4_spec]
    | succ n =>
      cases n with
      | zero => simp [fib4, fib4_spec]
      | succ n =>
        cases n with
        | zero => simp [fib4, fib4_spec]
        | succ n =>
          -- Inductive case
          -- Prove that the iterative implementation matches the recursive specification
          sorry

end HumanEval46
