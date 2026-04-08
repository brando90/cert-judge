import Std.Data.Nat.Prime
import Std.Data.List.Basic
import Mathlib.Tactic.Ring

namespace PrimeFib

def isPrime (p : Nat) : Bool :=
  if p < 2 then false
  else
    let sqrt_p := Nat.sqrt p
    let range := List.range (sqrt_p - 1) |>.map (· + 2)
    range.all (fun k => p % k != 0)

def fibonacci (n : Nat) : Nat :=
  match n with
  | 0 => 0
  | 1 => 1
  | n+2 => fibonacci (n+1) + fibonacci n

def primeFib (n : Nat) : Nat :=
  let rec findNthPrimeFib (count : Nat) (i : Nat) : Nat :=
    let fib := fibonacci i
    if isPrime fib then
      if count == n then fib
      else findNthPrimeFib (count + 1) (i + 1)
    else
      findNthPrimeFib count (i + 1)
  
  if n == 0 then 0
  else findNthPrimeFib 1 3

-- Specification
def isPrimeFib (x : Nat) : Prop :=
  ∃ i, fibonacci i = x ∧ Nat.Prime x

def isNthPrimeFib (x n : Nat) : Prop :=
  x ≠ 0 ∧ ∃ seq : List Nat, 
    (∀ i ∈ seq, isPrimeFib i) ∧
    seq.length = n ∧
    seq.isSorted (· ≤ ·) ∧
    seq.getLast (by simp) = x

-- Pre and post conditions
def primeFib_pre (n : Nat) : Prop :=
  n > 0

def primeFib_post (n : Nat) (result : Nat) : Prop :=
  isNthPrimeFib result n

theorem primeFib_correct (n : Nat) (h : primeFib_pre n) : primeFib_post n (primeFib n) := by
  sorry

-- Tests
#eval primeFib 1 -- 2
#eval primeFib 2 -- 3
#eval primeFib 3 -- 5
#eval primeFib 4 -- 13
#eval primeFib 5 -- 89
#eval primeFib 6 -- 233
#eval primeFib 7 -- 1597
#eval primeFib 8 -- 28657
#eval primeFib 9 -- 514229
#eval primeFib 10 -- 433494437

def test : IO Unit := do
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

end PrimeFib
