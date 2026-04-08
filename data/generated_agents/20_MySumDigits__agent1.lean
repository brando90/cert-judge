import VeriBench

/-!
# Sum of Digits
Returns the sum of digits in a non-negative integer.
-/

namespace SumOfDigits

/-- True iff n is a non-negative integer -/
def pre (n : Int) : Prop :=
  n ≥ 0

/-- The sum of digits of a non-negative integer -/
def prog (n : Int) : Int :=
  if n == 0 then
    0
  else
    let rec loop (n : Int) (total : Int) : Int :=
      if n ≤ 0 then
        total
      else
        loop (n / 10) (total + n % 10)
    loop n 0

/-- The specification of the sum of digits function -/
def post (n : Int) (result : Int) : Prop :=
  if n == 0 then
    result == 0
  else
    let rec sumDigits (n : Int) : Int :=
      if n ≤ 0 then
        0
      else
        n % 10 + sumDigits (n / 10)
    result == sumDigits n

theorem prog_correct (n : Int) (h : pre n) : post n (prog n) := sorry

#eval prog 123 -- 6
#eval prog 0   -- 0

/-- Test cases for the sum of digits function -/
def test : IO Unit := do
  VeriBench.check "prog 123 = 6" (prog 123 = 6)
  VeriBench.check "prog 0 = 0" (prog 0 = 0)
  VeriBench.check "prog 9 = 9" (prog 9 = 9)
  VeriBench.check "prog 999 = 27" (prog 999 = 27)
  VeriBench.check "prog 12345 = 15" (prog 12345 = 15)

end SumOfDigits
