import Mathlib.Data.Real.Basic
import Mathlib.Tactic

namespace VeriBench.HumanEval32

/--
  Evaluates polynomial with coefficients xs at point x.
  return xs[0] + xs[1] * x + xs[1] * x^2 + .... xs[n] * x^n
-/
def poly (xs : List Float) (x : Float) : Float :=
  xs.enum.foldl (fun acc (i, coeff) => acc + coeff * x ^ i.val) 0.0

/--
  xs are coefficients of a polynomial.
  find_zero find x such that poly(x) = 0.
  find_zero returns only only zero point, even if there are many.
  Moreover, find_zero only takes list xs having even number of coefficients
  and largest non zero coefficient as it guarantees
  a solution.
-/
def find_zero (xs : List Float) : Float :=
  let rec binary_search (begin end : Float) : Float :=
    if end - begin ≤ 1e-10 then
      begin
    else
      let center := (begin + end) / 2.0
      if poly xs center * poly xs begin > 0.0 then
        binary_search center end
      else
        binary_search begin center

  let rec find_bounds (begin end : Float) : Float × Float :=
    if poly xs begin * poly xs end ≤ 0.0 then
      (begin, end)
    else
      find_bounds (begin * 2.0) (end * 2.0)

  let (begin, end) := find_bounds (-1.0) 1.0
  binary_search begin end

-- Tests
def test_find_zero : IO Unit := do
  -- Test case 1: f(x) = 1 + 2x
  let result1 := find_zero [1.0, 2.0]
  IO.println s!"Test 1: {result1}, expected around -0.5"
  assert! (abs (poly [1.0, 2.0] result1) < 1e-4)

  -- Test case 2: (x - 1) * (x - 2) * (x - 3) = -6 + 11x - 6x^2 + x^3
  let result2 := find_zero [-6.0, 11.0, -6.0, 1.0]
  IO.println s!"Test 2: {result2}, expected around 1.0, 2.0, or 3.0"
  assert! (abs (poly [-6.0, 11.0, -6.0, 1.0] result2) < 1e-4)

  -- Test case 3: f(x) = 2 - 3x
  let result3 := find_zero [2.0, -3.0]
  IO.println s!"Test 3: {result3}, expected around 0.67"
  assert! (abs (poly [2.0, -3.0] result3) < 1e-4)

  IO.println "All tests passed!"

-- Specification and verification
/--
  Precondition for find_zero: The input list should have an even number of coefficients
  and the largest coefficient should be non-zero to guarantee a solution.
-/
def find_zero_pre (xs : List Float) : Prop :=
  xs.length % 2 = 0 ∧ xs.length > 0 ∧ xs.getLast? ≠ some 0.0

/--
  Postcondition for find_zero: The returned value should be a root of the polynomial,
  i.e., poly(xs, result) should be approximately zero.
-/
def find_zero_post (xs : List Float) (result : Float) : Prop :=
  abs (poly xs result) < 1e-4

/--
  Theorem stating that find_zero satisfies its specification.
-/
theorem find_zero_correct (xs : List Float) (h : find_zero_pre xs) : 
  find_zero_post xs (find_zero xs) := by
  sorry

end VeriBench.HumanEval32
