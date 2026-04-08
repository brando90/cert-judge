import Mathlib.Data.Int.Basic

/--
  Return the sum of digits in a non-negative integer.

  Edge cases:
  - Sum of digits of 0 is 0.
  - Single digit numbers return themselves.
-/

def pre (n : Int) : Bool :=
  n ≥ 0

def sumDigits (n : Int) : Int :=
  if !pre n then
    panic! s!"Require non-negative integer (got n={n})"
  else if n = 0 then
    0
  else
    let rec loop (n : Int) (total : Int) : Int :=
      if n = 0 then
        total
      else
        loop (n / 10) (total + n % 10)
    loop n 0

/-- Tests for sumDigits function -/
def sumDigitsTests : Bool :=
  sumDigits 123 = 6 &&
  sumDigits 0 = 0

#eval sumDigitsTests

/-- Specification for sumDigits function -/
def sumDigitsSpec (n : Int) : Int :=
  if n = 0 then
    0
  else
    let rec sumDigitsRec (n : Int) : Int :=
      if n = 0 then
        0
      else
        (n % 10) + sumDigitsRec (n / 10)
    sumDigitsRec n

/-- Precondition for sumDigits function -/
def sumDigitsPre (n : Int) : Prop :=
  n ≥ 0

/-- Postcondition for sumDigits function -/
def sumDigitsPost (n : Int) (result : Int) : Prop :=
  result = sumDigitsSpec n

/-- Correctness theorem for sumDigits function -/
theorem sumDigitsCorrect (n : Int) (h : sumDigitsPre n) : 
  sumDigitsPost n (sumDigits n) := by
  unfold sumDigitsPost
  unfold sumDigits
  simp [pre, h]
  
  by_cases h₁ : n = 0
  · simp [h₁, sumDigitsSpec]
  · sorry
