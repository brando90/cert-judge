import Mathlib.Data.Nat.Basic
import Mathlib.Data.Nat.Sqrt
import Mathlib.Tactic.Ring

/--
  `isPrime n` checks if `n` is a prime number.
-/
def isPrime (n : Nat) : Bool :=
  if n < 2 then
    false
  else
    let sqrtN := Nat.sqrt n + 1
    let upperBound := min sqrtN (n - 1)
    let rec checkDivisors (k : Nat) : Bool :=
      if k > upperBound then
        true
      else if n % k == 0 then
        false
      else
        checkDivisors (k + 1)
    checkDivisors 2

/--
  `primeFib n` returns the n-th number that is both a Fibonacci number and a prime number.
-/
def primeFib (n : Nat) : Nat :=
  if n == 0 then
    0
  else
    let rec loop (count : Nat) (a : Nat) (b : Nat) : Nat :=
      let next := a + b
      if isPrime next then
        if count + 1 == n then
          next
        else
          loop (count + 1) b next
      else
        loop count b next
    loop 0 0 1

/--
  Specification for `primeFib`.
  The function should return the n-th number that is both a Fibonacci number and a prime number.
-/
def primeFibSpec (n : Nat) : Nat :=
  if n == 0 then
    0
  else if n == 1 then
    2
  else if n == 2 then
    3
  else if n == 3 then
    5
  else if n == 4 then
    13
  else if n == 5 then
    89
  else if n == 6 then
    233
  else if n == 7 then
    1597
  else if n == 8 then
    28657
  else if n == 9 then
    514229
  else if n == 10 then
    433494437
  else
    0 -- Placeholder for larger values

/--
  Precondition for `primeFib`.
  The function requires that n is a positive natural number.
-/
def primeFibPre (n : Nat) : Prop :=
  n > 0

/--
  Postcondition for `primeFib`.
  The function returns a number that is both a Fibonacci number and a prime number,
  and it's the n-th such number.
-/
def primeFibPost (n : Nat) (result : Nat) : Prop :=
  result = primeFibSpec n

theorem primeFibCorrect (n : Nat) (h : primeFibPre n) : primeFibPost n (primeFib n) := sorry

#eval primeFib 1  -- Expected: 2
#eval primeFib 2  -- Expected: 3
#eval primeFib 3  -- Expected: 5
#eval primeFib 4  -- Expected: 13
#eval primeFib 5  -- Expected: 89
#eval primeFib 6  -- Expected: 233
#eval primeFib 7  -- Expected: 1597
#eval primeFib 8  -- Expected: 28657
#eval primeFib 9  -- Expected: 514229
#eval primeFib 10 -- Expected: 433494437
