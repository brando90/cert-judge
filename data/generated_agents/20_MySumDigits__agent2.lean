import VeriBench.Common

/-- Return the sum of digits in a non-negative integer.

Edge cases:
- Sum of digits of 0 is 0.
- Single digit numbers return themselves.
- The function raises ValueError if input is not a non-negative integer.
-/

namespace SumOfDigits

/-- True iff n is a non-negative integer. -/
def pre (n : Int) : Bool :=
  n ≥ 0

/-- Return the sum of digits in n.
    Raises error if the precondition is violated. -/
def prog (n : Int) : Int :=
  if !pre n then
    panic! s!"Require non-negative integer (got n={n})"
  else if n = 0 then
    0
  else
    let rec sumDigits (n : Int) (total : Int) : Int :=
      if n = 0 then
        total
      else
        sumDigits (n / 10) (total + n % 10)
    
    sumDigits n 0

/-- The sum of digits of 0 is 0. -/
theorem sum_of_digits_zero : prog 0 = 0 := by
  simp [prog, pre]

/-- The sum of digits of a single digit number is the number itself. -/
theorem sum_of_digits_single_digit (n : Int) (h1 : 0 < n) (h2 : n < 10) : 
  prog n = n := by
  sorry

/-- The sum of digits of a multi-digit number is the sum of its last digit
    and the sum of digits of the number without its last digit. -/
theorem sum_of_digits_recursive (n : Int) (h : n ≥ 10) : 
  prog n = prog (n / 10) + n % 10 := by
  sorry

/-- The postcondition: the result is always non-negative. -/
def post (n : Int) (result : Int) : Bool :=
  pre n → result ≥ 0

/-- The sum of digits function satisfies its postcondition. -/
theorem prog_correct (n : Int) : post n (prog n) := by
  sorry

/-- Test cases for the sum of digits function -/
def test : IO Unit := do
  assert! (prog 123 = 6)
  assert! (prog 0 = 0)
  assert! (prog 9 = 9)
  assert! (prog 999 = 27)
  IO.println "All tests passed!"

end SumOfDigits
