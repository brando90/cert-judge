import Std.Data.List.Basic
import Std.Data.Nat.Basic

/--
Count even digits in a non-negative integer.

Edge cases:
- 0 has one even digit (0).
- Negative inputs are invalid.
-/

def pre (n : Int) : Bool :=
  n ≥ 0

def countEvenDigits (n : Int) : Int :=
  if !pre n then
    panic! "Input must be a non-negative integer"
  else
    let digits := String.toList (toString n)
    let evenDigits := digits.filter (fun c =>
      let digit := c.toNat - '0'.toNat
      digit % 2 == 0
    )
    evenDigits.length

/--
Specification: countEvenDigits returns the number of even digits in a non-negative integer.
-/
def countEvenDigitsSpec (n : Int) : Int :=
  if !pre n then
    panic! "Input must be a non-negative integer"
  else
    let digits := String.toList (toString n)
    let evenCount := digits.foldl (fun count c =>
      let digit := c.toNat - '0'.toNat
      if digit % 2 == 0 then count + 1 else count
    ) 0
    evenCount

theorem countEvenDigitsCorrect (n : Int) (h : pre n) :
  countEvenDigits n = countEvenDigitsSpec n := by
  sorry

#eval countEvenDigits 24863 -- Expected: 4
#eval countEvenDigits 0     -- Expected: 1
#eval countEvenDigits 13579 -- Expected: 0

/--
Test suite for countEvenDigits
-/
def testCountEvenDigits : IO Unit := do
  -- Basic test
  assert! (countEvenDigits 24863 = 4)
  -- Edge case
  assert! (countEvenDigits 0 = 1)
  -- No even digits
  assert! (countEvenDigits 13579 = 0)
  -- Many digits
  assert! (countEvenDigits 8642086420 = 10)
  IO.println "All tests passed!"

#eval testCountEvenDigits
