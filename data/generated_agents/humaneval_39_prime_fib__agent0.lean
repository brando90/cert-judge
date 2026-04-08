import Mathlib.Data.Nat.Prime
import Mathlib.Data.Nat.Sqrt

namespace VeriBench.HumanEval.Problem39

/-- Returns true if n is a prime number -/
def isPrime (n : Nat) : Bool :=
  if n < 2 then
    false
  else
    let sqrtN := Nat.sqrt n
    !((List.range (sqrtN - 1)).map (fun i => i + 2) |>.any (fun k => n % k == 0))

/-- Generates the Fibonacci sequence up to a certain index -/
def fibSeq (n : Nat) : List Nat :=
  match n with
  | 0 => [0]
  | 1 => [0, 1]
  | n + 2 =>
    let init := fibSeq (n + 1)
    init ++ [init.getLast! + init.get! (init.length - 2)]

/-- Returns the nth Fibonacci number -/
def fib (n : Nat) : Nat :=
  match n with
  | 0 => 0
  | 1 => 1
  | n + 2 => fib (n + 1) + fib n

/-- Specification: returns n-th number that is a Fibonacci number and it's also prime -/
def primeFibSpec (n : Nat) : Nat :=
  if n == 0 then
    0
  else
    let rec findNthPrimeFib (count : Nat) (fibIdx : Nat) : Nat :=
      let fibNum := fib fibIdx
      if isPrime fibNum then
        if count == n then
          fibNum
        else
          findNthPrimeFib (count + 1) (fibIdx + 1)
      else
        findNthPrimeFib count (fibIdx + 1)
    findNthPrimeFib 0 1

/-- Implementation: returns n-th number that is a Fibonacci number and it's also prime -/
def primeFib (n : Nat) : Nat :=
  if n == 0 then
    0
  else
    let rec loop (count : Nat) (f : List Nat) : Nat :=
      let nextFib := f.getLast! + f.get! (f.length - 2)
      let newF := f ++ [nextFib]
      if isPrime nextFib then
        if count + 1 == n then
          nextFib
        else
          loop (count + 1) newF
      else
        loop count newF
    loop 0 [0, 1]

/-- Precondition: n must be a positive integer -/
def primeFib.pre (n : Nat) : Prop :=
  n > 0

/-- Postcondition: result is both a Fibonacci number and a prime number -/
def primeFib.post (n : Nat) (result : Nat) : Prop :=
  (∃ i, fib i = result) ∧ Nat.Prime result

/-- Correctness theorem: primeFib satisfies its specification -/
theorem primeFib_correct (n : Nat) (h : primeFib.pre n) : 
  primeFib n = primeFibSpec n := by
  sorry

/-- Tests for the primeFib function -/
def primeFib_test : IO Unit := do
  assert! (primeFib 1 = 2)
  assert! (primeFib 2 = 3)
  assert! (primeFib 3 = 5)
  assert! (primeFib 4 = 13)
  assert! (primeFib 5 = 89)
  assert! (primeFib 6 = 233)
  assert! (primeFib 7 = 1597)
  assert! (primeFib 8 = 28657)
  assert! (primeFib 9 = 514229)
  assert! (primeFib 10 = 433494437)
  IO.println "All tests passed!"

end VeriBench.HumanEval.Problem39
