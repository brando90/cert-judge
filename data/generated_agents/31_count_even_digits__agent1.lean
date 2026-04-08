import Lean.Data.HashMap

namespace CountEvenDigits

def isDigitEven (d : Nat) : Bool :=
  d % 2 == 0

def countEvenDigits (n : Nat) : Nat :=
  if n == 0 then
    1  -- 0 has one even digit (0)
  else
    let rec countEvenInDigits (n : Nat) (acc : Nat) : Nat :=
      if n == 0 then
        acc
      else
        let lastDigit := n % 10
        let newAcc := if isDigitEven lastDigit then acc + 1 else acc
        countEvenInDigits (n / 10) newAcc
    
    countEvenInDigits n 0

/-- Specification: countEvenDigits n returns the number of even digits in n -/
def countEvenDigitsSpec (n : Nat) : Nat :=
  if n == 0 then
    1  -- 0 has one even digit (0)
  else
    let digits := String.toList (toString n)
    List.foldl (fun count c => 
      let digit := (c.toNat - '0'.toNat)
      if isDigitEven digit then count + 1 else count
    ) 0 digits

/-- Pre-condition: n must be a natural number (always satisfied in Lean) -/
def pre (n : Nat) : Prop := True

/-- Post-condition: The result is the number of even digits in n -/
def post (n : Nat) (result : Nat) : Prop :=
  result = countEvenDigitsSpec n

theorem countEvenDigits_correct (n : Nat) : 
  pre n → post n (countEvenDigits n) :=
  fun _ => by sorry

#eval countEvenDigits 24863  -- Should be 4
#eval countEvenDigits 0      -- Should be 1
#eval countEvenDigits 13579  -- Should be 0

/-- Test suite for countEvenDigits -/
def testCountEvenDigits : IO Unit := do
  let tests : List (Nat × Nat) := [
    (24863, 4),  -- Basic test
    (0, 1),      -- Edge case: 0 has one even digit
    (13579, 0),  -- No even digits
    (2468, 4),   -- All even digits
    (123456, 3)  -- Mixed case
  ]
  
  for (input, expected) in tests do
    let result := countEvenDigits input
    if result != expected then
      throw (IO.userError s!"Test failed: countEvenDigits {input} = {result}, expected {expected}")
    else
      IO.println s!"Test passed: countEvenDigits {input} = {expected}"

#eval testCountEvenDigits

end CountEvenDigits
