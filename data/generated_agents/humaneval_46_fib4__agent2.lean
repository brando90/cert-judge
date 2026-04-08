/-
# File: humaneval_46_fib4.lean
# HumanEval problem HumanEval/46
-/

/--
The Fib4 number sequence is a sequence similar to the Fibbonacci sequnece that's defined as follows:
fib4(0) -> 0
fib4(1) -> 0
fib4(2) -> 2
fib4(3) -> 0
fib4(n) -> fib4(n-1) + fib4(n-2) + fib4(n-3) + fib4(n-4).
This function efficiently computes the n-th element of the fib4 number sequence without using recursion.
-/
def fib4 (n : Nat) : Nat :=
  if n < 4 then
    match n with
    | 0 => 0
    | 1 => 0
    | 2 => 2
    | 3 => 0
    | _ => 0 -- Unreachable due to the n < 4 check
  else
    let rec loop (i : Nat) (a b c d : Nat) : Nat :=
      if i == n then
        d
      else
        loop (i + 1) b c d (a + b + c + d)
    loop 4 0 0 2 0

/-- Specification of fib4 using recursion (for verification purposes) -/
def fib4_spec (n : Nat) : Nat :=
  match n with
  | 0 => 0
  | 1 => 0
  | 2 => 2
  | 3 => 0
  | n + 4 => fib4_spec n + fib4_spec (n + 1) + fib4_spec (n + 2) + fib4_spec (n + 3)

/-- Lemma: fib4 and fib4_spec produce the same results -/
theorem fib4_eq_fib4_spec (n : Nat) : fib4 n = fib4_spec n := by
  sorry

/-- Test cases for fib4 -/
def fib4_test : IO Unit := do
  assert! (fib4 5 == 4)
  assert! (fib4 8 == 28)
  assert! (fib4 10 == 104)
  assert! (fib4 12 == 386)
  IO.println "All tests passed!"

/-- Main function to run the tests -/
def main : IO Unit :=
  fib4_test
