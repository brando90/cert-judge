import VeriBench

namespace CountEvenDigits

/-- Check if a number is a non-negative integer. -/
def pre (n : Int) : Bool :=
  n ≥ 0

/-- Get the digit at a specific position in a number. -/
def getDigit (n : Nat) (pos : Nat) : Nat :=
  (n / (10 ^ pos)) % 10

/-- Count the number of digits in a natural number. -/
def numDigits (n : Nat) : Nat :=
  if n < 10 then 1 else 1 + numDigits (n / 10)

/-- Count even digits in a non-negative integer.
    Returns the number of even digits in the input. -/
def count_even_digits (n : Int) : Int :=
  if !pre n then
    panic! "Input must be a non-negative integer"
  else
    let nat_n := n.toNat
    let num_digits := numDigits nat_n
    let mut count := 0
    for i in [0:num_digits] do
      let digit := getDigit nat_n i
      if digit % 2 == 0 then
        count := count + 1
    count

/-- Specification: Count even digits in a non-negative integer. -/
def count_even_digits_spec (n : Int) : Int :=
  if !pre n then
    panic! "Input must be a non-negative integer"
  else
    let digits := String.mk (toString n.toNat).data
    let mut count := 0
    for c in digits do
      let digit := (c.toString.toNat!)
      if digit % 2 == 0 then
        count := count + 1
    count

/-- Post-condition: The function returns a non-negative integer. -/
def post (n : Int) (result : Int) : Prop :=
  result ≥ 0

theorem count_even_digits_correct (n : Int) (h : pre n) : 
  count_even_digits n = count_even_digits_spec n := by
  sorry

/-- Unit tests for count_even_digits -/
def test : IO Unit := do
  VeriBench.check (count_even_digits 24863 = 4)
  VeriBench.check (count_even_digits 0 = 1)
  VeriBench.check (count_even_digits 13579 = 0)
  VeriBench.check (count_even_digits 2468 = 4)
  VeriBench.check (count_even_digits 1 = 0)
  VeriBench.check (count_even_digits 10 = 1)
  pure ()

end CountEvenDigits
